"""
Team 1 - Mindball relaxation score, v0.2
=======================================

Builds on "team 1 mindball v0.1". Core idea:

    relaxation = log( (alpha + theta) / beta )

Pipeline (every 0.25 s):
    last 4 s of EEG -> clean -> Welch band powers (newest 2 s)
    -> quality checks -> add up electrodes -> score
    -> scale using this player's rest AND focus calibration (z-score)
    -> clip to +/-2 -> smooth (EMA) -> game

Calibration (before playing):
    1. REST  45 s  (eyes open, relaxed)   -> also finds the player's own
                                             alpha peak (IAF) to set bands
    2. FOCUS 45 s  (count back from 1000 by 7s)
    -> 0 = halfway between their rest and focus, + = relaxed, - = focused

Run:
    python mindball_v0_2.py --port COM3          (Windows)
    python mindball_v0_2.py --port /dev/ttyUSB0  (Mac/Linux)
"""

import argparse
import time

import numpy as np
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from brainflow.data_filter import (DataFilter, WindowOperations,
                                   DetrendOperations, FilterTypes)

# =====================================================================
# Settings
# =====================================================================
# --- Timing ---
SCORE_SECONDS = 2           # window we actually score
BUFFER_SECONDS = 4          # extra older data so filters settle first
UPDATE_SECONDS = 0.25       # new score 4 times per second
SMOOTHING_ALPHA = 0.4       # EMA: 40% new score, 60% previous
CALIBRATION_SECONDS = 45    # length of EACH calibration phase (rest, focus)
SETTLE_SECONDS = 5          # ignore the start of each phase

# --- Electrodes ---
SCORE_CHANNELS = ["O1", "O2", "P3", "P4"]   # back of head: strongest alpha
BLINK_CHANNELS = ["Fp1", "Fp2"]             # above eyes: only to detect blinks
MIN_GOOD_CHANNELS = 2       # fewer clean electrodes than this = bad window

# --- Individual alpha peak (IAF) ---
IAF_SEARCH = (7.0, 13.0)    # where to look for the alpha peak
DEFAULT_IAF = 10.0          # used if no clear peak is found
BETA_TOP = 30.0

# --- Scaling ---
CLIP_LIMIT = 2.0            # final z-score is kept between -2 and +2

# --- Quality checks (standard starting values; tune once you have recordings) ---
RAILED_UV = 0.9 * 187500    # Cyton amplifier max is +/-187,500 uV
LINE_NOISE_RATIO = 1.0      # 60 Hz power > all brain power = poor contact
FLAT_STD = 0.5              # uV; less = electrode not touching
PTP_THRESHOLD = 150         # uV; bigger swing = movement (common EEG cutoff)
KURTOSIS_THRESHOLD = 8.0    # "spikiness"; clean EEG is about 3
EMG_RATIO_THRESHOLD = 0.20  # share of power in 30-45 Hz; more = muscle
OUTLIER_FACTOR = 3.0        # channel much noisier than the others = bad
BLINK_UV = 100              # swing on Fp1/Fp2 that counts as a blink


# =====================================================================
# 1. Frequency bands from the player's alpha peak
# =====================================================================
def make_bands(iaf):
    """Bands centred on this player's own alpha peak (Klimesch-style).
    For a typical IAF of 10 Hz this gives theta 4-8, alpha 8-12, beta 12-30."""
    return {
        "theta": (max(iaf - 6.0, 3.0), iaf - 2.0),
        "alpha": (iaf - 2.0, iaf + 2.0),
        "beta":  (iaf + 2.0, BETA_TOP),
    }


def find_iaf(rest_data, fs, rows):
    """Find the frequency where alpha peaks during rest.
    Uses long Welch pieces (~4 s) for fine frequency detail (~0.25 Hz)."""
    nfft = DataFilter.get_nearest_power_of_two(4 * fs)
    spectra = []
    for r in rows:
        x = clean_channel(rest_data[r], fs)
        if len(x) < nfft:
            continue
        psd, freqs = DataFilter.get_psd_welch(x, nfft, nfft // 2, fs,
                                              WindowOperations.HANNING.value)
        spectra.append(psd)
    if not spectra:
        return DEFAULT_IAF
    avg = np.mean(spectra, axis=0)
    lo, hi = IAF_SEARCH
    mask = (freqs >= lo) & (freqs <= hi)
    peak = float(freqs[mask][np.argmax(avg[mask])])
    # A peak sitting on the edge of the search range isn't a real peak
    if peak <= lo + 0.5 or peak >= hi - 0.5:
        return DEFAULT_IAF
    return peak


# =====================================================================
# 2. Cleaning and measuring one electrode
# =====================================================================
def clean_channel(signal, fs):
    """Remove drift and keep 1-45 Hz. Returns a filtered copy."""
    x = np.ascontiguousarray(signal, dtype=np.float64).copy()
    DataFilter.detrend(x, DetrendOperations.LINEAR.value)
    DataFilter.perform_bandpass(x, fs, 1.0, 45.0, 4,
                                FilterTypes.BUTTERWORTH_ZERO_PHASE.value, 0)
    return x


def channel_psd(x, fs):
    """Welch power spectrum: ~1 s pieces, half overlap, Hann window."""
    nfft = DataFilter.get_nearest_power_of_two(fs)
    return DataFilter.get_psd_welch(x, nfft, nfft // 2, fs,
                                    WindowOperations.HANNING.value)


def band_powers(psd, bands):
    return {name: DataFilter.get_band_power(psd, lo, hi)
            for name, (lo, hi) in bands.items()}


# =====================================================================
# 3. Quality checks
# =====================================================================
def kurtosis(x):
    """How 'spiky' a signal is. Smooth brain rhythms ~3, sudden jumps >> 3."""
    d = x - np.mean(x)
    var = np.mean(d ** 2)
    return float(np.mean(d ** 4) / var ** 2) if var > 0 else 0.0


def check_channel(raw, x, psd, fs):
    """raw = unfiltered newest 2 s, x = cleaned newest 2 s.
    Returns None if OK, otherwise the reason the electrode is skipped."""
    # Hardware problems (look at the raw signal)
    if np.max(np.abs(raw)) >= RAILED_UV:
        return "railed"               # amplifier maxed out: lost contact
    raw_d = np.ascontiguousarray(raw - np.mean(raw), dtype=np.float64)
    raw_psd = channel_psd(raw_d, fs)
    if fs / 2 > 62:
        hum = DataFilter.get_band_power(raw_psd, 58.0, 62.0)
        brain = DataFilter.get_band_power(raw_psd, 1.0, 45.0)
        if brain > 0 and hum / brain > LINE_NOISE_RATIO:
            return "line-noise"       # picking up wall power = poor contact
    # Signal problems (look at the cleaned signal)
    if np.std(x) < FLAT_STD:
        return "flat"
    if np.ptp(x) > PTP_THRESHOLD:
        return "spike"
    if kurtosis(x) > KURTOSIS_THRESHOLD:
        return "transient"            # sudden pop, e.g. cable tug
    total = DataFilter.get_band_power(psd, 1.0, 45.0)
    muscle = DataFilter.get_band_power(psd, 30.0, 45.0)
    if total > 0 and muscle / total > EMG_RATIO_THRESHOLD:
        return "muscle"               # jaw clench / tense face
    return None


def blink_detected(data, fs, blink_rows, n):
    """True if the electrodes above the eyes show a blink-sized swing."""
    for r in blink_rows:
        x = clean_channel(data[r], fs)[-n:]
        if np.ptp(x) > BLINK_UV:
            return True
    return False


# =====================================================================
# 4. Combining electrodes and scoring one window
# =====================================================================
def combine_scores(powers):
    """powers: list of {theta, alpha, beta} dicts, one per good electrode.
    Adds up each band across electrodes first, then takes ONE ratio, so a
    single electrode with an unusually small beta can't blow up the score."""
    t = sum(p["theta"] for p in powers)
    a = sum(p["alpha"] for p in powers)
    b = sum(p["beta"] for p in powers)
    return float(np.log((a + t) / b))


def score_window(data, fs, rows, bands, blink_rows=(),
                 min_good=MIN_GOOD_CHANNELS):
    """THE core function.

    data       : 2D array (rows = board channels, columns = samples),
                 BUFFER_SECONDS long; only the newest SCORE_SECONDS are scored
    rows       : which rows to score
    bands      : from make_bands()
    blink_rows : rows above the eyes, used only to detect blinks

    Returns (score, report). score is None for a bad window.
    report says why each electrode was skipped (None = used).
    """
    n = int(SCORE_SECONDS * fs)
    if data.shape[1] < n:
        return None, {"window": "not enough data"}
    if blink_detected(data, fs, blink_rows, n):
        return None, {"window": "blink"}

    report, cleaned, powers = {}, {}, {}
    for r in rows:
        raw = data[r][-n:]
        x = clean_channel(data[r], fs)[-n:]
        psd = channel_psd(x, fs)
        report[r] = check_channel(raw, x, psd, fs)
        if report[r] is None:
            cleaned[r] = x
            powers[r] = band_powers(psd, bands)

    # Outlier check: one electrode far noisier than the rest
    if len(cleaned) >= 3:
        stds = {r: np.std(x) for r, x in cleaned.items()}
        typical = np.median(list(stds.values()))
        for r, s in stds.items():
            if s > OUTLIER_FACTOR * typical:
                report[r] = "outlier"
                powers.pop(r)

    if len(powers) < min_good:
        return None, report
    return combine_scores(list(powers.values())), report


def score_recording(data, fs, rows, bands, blink_rows=(), min_good=MIN_GOOD_CHANNELS):
    """Slide a window across a whole recording, like the live game does."""
    buf, step = int(BUFFER_SECONDS * fs), int(UPDATE_SECONDS * fs)
    start = int(SETTLE_SECONDS * fs)
    scores = []
    for end in range(max(buf, start + buf), data.shape[1] + 1, step):
        s, _ = score_window(data[:, end - buf:end], fs, rows, bands,
                            blink_rows, min_good)
        scores.append(s)
    return scores


# =====================================================================
# 5. One player: rest + focus calibration, scaling, smoothing
# =====================================================================
class Player:
    def __init__(self, name, smoothing_alpha=SMOOTHING_ALPHA):
        self.name = name
        self.alpha = smoothing_alpha
        self.iaf = DEFAULT_IAF
        self.bands = make_bands(DEFAULT_IAF)
        self.center = None
        self.spread = None
        self.separation = None
        self.smoothed = 0.0
        self.windows = 0
        self.rejected = 0

    def calibrate(self, rest_scores, focus_scores):
        """Set the scale from this player's own rest and focus scores.
        0 = halfway between their rest and focus, +1 = one 'typical wobble'
        toward relaxed. Also measures how well the two states separate."""
        rest = np.array([s for s in rest_scores if s is not None])
        focus = np.array([s for s in focus_scores if s is not None])
        if len(rest) < 10 or len(focus) < 10:
            raise RuntimeError(f"{self.name}: not enough clean calibration data. "
                               "Check electrodes or the quality thresholds.")
        pooled = np.sqrt((rest.var() + focus.var()) / 2)
        self.center = float((rest.mean() + focus.mean()) / 2)
        self.spread = max(float(pooled), 1e-6)
        self.separation = float((rest.mean() - focus.mean()) / self.spread)
        return len(rest), len(focus)

    def update(self, raw_score):
        """Feed one raw score (or None). Returns (smoothed_z, signal_ok)."""
        self.windows += 1
        if raw_score is None:          # bad window: hold the last value
            self.rejected += 1
            return self.smoothed, False
        z = (raw_score - self.center) / self.spread
        z = float(np.clip(z, -CLIP_LIMIT, CLIP_LIMIT))
        self.smoothed = self.alpha * z + (1 - self.alpha) * self.smoothed
        return self.smoothed, True

    @property
    def rejected_percent(self):
        return 100 * self.rejected / max(self.windows, 1)


# =====================================================================
# 6. Live headset
# =====================================================================
def rows_for(board_id, names):
    """Turn electrode names (e.g. 'O1') into data rows for this board."""
    eeg_rows = BoardShim.get_eeg_channels(board_id)
    board_names = BoardShim.get_eeg_names(board_id)
    return [eeg_rows[board_names.index(n)] for n in names]


def record_phase(board, seconds, instruction):
    """Clear the buffer, wait while the player follows the instruction,
    then return everything recorded."""
    print(f"\n{instruction}")
    board.get_board_data()                         # throw away old data
    for left in range(int(seconds), 0, -5):
        print(f"  {left} s left...")
        time.sleep(min(5, left))
    return board.get_board_data()


def per_electrode_report(rest, focus, fs, rows, names, bands, blink_rows):
    """How well each electrode ALONE tells rest from focus.
    Bigger separation = more useful electrode for this player."""
    print("\nElectrode separation (higher = better at telling rest from focus):")
    for r, name in zip(rows, names):
        rs = [s for s in score_recording(rest, fs, [r], bands, blink_rows, 1) if s is not None]
        fs_ = [s for s in score_recording(focus, fs, [r], bands, blink_rows, 1) if s is not None]
        if len(rs) < 10 or len(fs_) < 10:
            print(f"  {name:4s}  not enough clean data")
            continue
        pooled = np.sqrt((np.var(rs) + np.var(fs_)) / 2) or 1e-6
        print(f"  {name:4s}  {(np.mean(rs) - np.mean(fs_)) / pooled:+.2f}")


def run_live(port, board_id=BoardIds.CYTON_DAISY_BOARD):
    params = BrainFlowInputParams()
    params.serial_port = port
    board = BoardShim(board_id, params)
    fs = BoardShim.get_sampling_rate(board_id)
    rows = rows_for(board_id, SCORE_CHANNELS)
    blink_rows = rows_for(board_id, BLINK_CHANNELS)
    buffer_len = int(BUFFER_SECONDS * fs)
    player = Player("Player 1")

    board.prepare_session()
    board.start_stream()
    try:
        time.sleep(2)

        # ---- Calibration ----
        rest = record_phase(board, CALIBRATION_SECONDS,
            "REST: eyes open, look at one spot, relax your face and jaw.")
        focus = record_phase(board, CALIBRATION_SECONDS,
            "FOCUS: count backwards from 1000 by 7s in your head. Stay still.")

        player.iaf = find_iaf(rest, fs, rows)
        player.bands = make_bands(player.iaf)
        rest_scores = score_recording(rest, fs, rows, player.bands, blink_rows)
        focus_scores = score_recording(focus, fs, rows, player.bands, blink_rows)
        n_rest, n_focus = player.calibrate(rest_scores, focus_scores)

        print(f"\nAlpha peak (IAF): {player.iaf:.2f} Hz")
        print("Bands: " + ", ".join(f"{k} {lo:.1f}-{hi:.1f} Hz"
                                    for k, (lo, hi) in player.bands.items()))
        print(f"Clean windows: rest {n_rest}/{len(rest_scores)}, "
              f"focus {n_focus}/{len(focus_scores)}")
        print(f"Rest vs focus separation: {player.separation:+.2f}  "
              "(above ~1 = clear; near 0 = can't tell apart; negative = reversed)")
        per_electrode_report(rest, focus, fs, rows, SCORE_CHANNELS,
                             player.bands, blink_rows)

        # ---- Game ----
        print("\nNow playing. + = relaxed, - = focused. Ctrl+C to stop.")
        time.sleep(BUFFER_SECONDS)                 # refill the buffer
        while True:
            data = board.get_current_board_data(buffer_len)
            raw, report = score_window(data, fs, rows, player.bands, blink_rows)
            value, ok = player.update(raw)
            bad = [f"{k}:{v}" for k, v in report.items() if v]
            print(f"relaxation: {value:+.2f}  signal: {'OK ' if ok else 'BAD'}  "
                  f"rejected: {player.rejected_percent:.0f}%  {' '.join(map(str, bad))}")
            time.sleep(UPDATE_SECONDS)
    except KeyboardInterrupt:
        pass
    finally:
        board.stop_stream()                        # always runs, even after an error
        board.release_session()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Team 1 Mindball relaxation score")
    ap.add_argument("--port", required=True, help="e.g. COM3 or /dev/ttyUSB0")
    run_live(ap.parse_args().port)
