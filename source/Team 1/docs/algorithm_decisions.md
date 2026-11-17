# Team 1 – Relaxation Score: Algorithm Decisions

This explains every design decision in `mindball_v0_2.py` and what it affects.

## Data and timing

- **2 s scoring window (4 s buffer):** enough repeats of the slowest rhythm (theta) to measure it reliably, while still reacting quickly. The extra 2 s lets the filters settle.
- **New score every 0.25 s:** the ball moves smoothly, 4 updates per second.
- **BrainFlow for everything:** one library for the headset, filters and Welch, matching Team 1's v0.1.

## Electrodes

- **O1, O2, P3, P4 for scoring:** back and top-back of the head, where the relaxation rhythm (alpha) is strongest and blinks and jaw muscles interfere least.
- **Fp1, Fp2 for blink detection only:** they sit above the eyes, so they pick up blinks clearly but would distort the score.
- **At least 2 of the 4 must be clean:** one good electrode alone isn't trustworthy enough.

## Cleaning

- **Detrend + 1–45 Hz bandpass (zero-phase Butterworth, order 4):** removes slow drift and fast noise without shifting the signal in time.
- **No 60 Hz notch:** the score only uses up to 30 Hz, and the bandpass already cuts above 45 Hz, so wall hum can't affect it.

## Measuring rhythms

- **Welch's method (≈1 s pieces, half overlap, Hann window):** averages several FFTs for a steadier reading on noisy EEG, with 1 Hz detail.
- **Personal alpha peak (IAF) from the rest phase:** bands are shifted to fit each player's brain, so someone whose alpha peaks at 8.5 Hz isn't measured wrong.
- **Bands = theta IAF−6 to IAF−2, alpha IAF±2, beta IAF+2 to 30 Hz:** standard Klimesch method. For a typical player this equals the textbook 4–8 / 8–12 / 12–30 Hz.
- **Fallback to 10 Hz if no clear peak:** some people have weak alpha with their eyes open.

## Quality checks

- **Per electrode:** railed, line noise, flat, spike (150 µV), spikiness (kurtosis), muscle (20% of power in 30–45 Hz), outlier. Each removes a specific kind of junk (lost contact, poor contact, movement, cable pops, jaw clench, one bad electrode) before it reaches the score.
- **Whole window: blink (100 µV on Fp1/Fp2):** a blink throws out the whole moment, not just one electrode.
- **Reject instead of repair:** simple and fast enough for real time. The trade-off is that some data gets thrown away.

## The score

- **Formula = `log((alpha + theta) / beta)`:** slow rhythms vs. fast rhythms. Higher means more relaxed, which fits Mindball, where the calmer player wins. The log keeps it balanced around 0.
- **Combine by sum:** add each band across the good electrodes, then take one ratio. That's more stable than averaging separate ratios.

## Calibration and output

- **45 s rest + 45 s focus (counting backwards by 7s):** each player gets their own scale, so naturally different brains compete fairly.
- **Ignore the first 5 s of each phase:** the player is still settling in.
- **z-score from the midpoint of rest and focus:** 0 = halfway, + = relaxed, − = focused, measured in units of the player's normal wobble.
- **Separation numbers (overall and per electrode):** show whether the algorithm can actually tell this player's states apart, and which electrodes help.
- **Clip to ±2:** one weird reading can't fling the ball, and the game stays calmer.
- **Smoothing (EMA, 0.4):** removes jitter while still reacting within about a second.
- **Bad window = hold the last value + report "BAD":** the game can freeze the ball instead of moving it on bad data.

## What will likely need changing once we have data and hardware

- **All quality thresholds:** check the rejected % while someone sits still. Over about 20% means something is too strict, and the printout shows which check.
- **Electrode choice:** keep whichever electrodes show high separation across several players.
- **Electrode map:** confirm O1, O2, P3, P4, Fp1 and Fp2 are in BrainFlow's default Cyton + Daisy positions and nobody moved them.
- **The formula itself:** if separation is low for most people, try dropping theta (`alpha / beta`) or relative alpha.
- **Calibration length and task:** 45 + 45 s may feel long in a game. See if shorter still gives good separation.
- **Smoothing and clip:** tune by feel once people actually play.
- **Two players:** the code handles one headset. Running two at once depends on Group 1's hardware setup.
- **Connecting to the game:** right now it prints scores. It will eventually need to send them to Group 4's game logic.
