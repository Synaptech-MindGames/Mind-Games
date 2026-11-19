#!/usr/bin/env python3
"""
EEG Explorer for MILimbEEG CSV recordings.

Install dependencies:
    python3 -m pip install pandas numpy plotly

Run:
    python3 eeg_explorer.py path/to/S1R1I1_1.csv

The script creates an interactive HTML report beside the CSV.
"""
from pathlib import Path
import argparse
import re
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from html import escape

CHANNELS = ["FC5", "F3", "Fz", "F4", "FC6", "FC1", "FC2", "Cz",
            "T7", "CP5", "C3", "CP1", "CP2", "C4", "CP6", "T8"]
TASKS = {
    1: "BEO — Baseline, eyes open",
    2: "CLH — Closing left hand",
    3: "CRH — Closing right hand",
    4: "DLF — Dorsal flexion, left foot",
    5: "PLF — Plantar flexion, left foot",
    6: "DRF — Dorsal flexion, right foot",
    7: "PRF — Plantar flexion, right foot",
    8: "Rest"
}
FS = 125

def main():
    parser = argparse.ArgumentParser(description="Create an interactive EEG HTML report.")
    parser.add_argument("csv_file", help="Path to a MILimbEEG CSV file")
    args = parser.parse_args()
    path = Path(args.csv_file).expanduser().resolve()
    df = pd.read_csv(path)

    if df.shape[1] != 17:
        raise ValueError(f"Expected 17 columns (sample index + 16 EEG channels); found {df.shape[1]}.")

    samples = df.iloc[:, 0].to_numpy()
    eeg = df.iloc[:, 1:].to_numpy(dtype=float)
    time = samples / FS
    n_samples, n_channels = eeg.shape

    match = re.match(r"S(\d+)R(\d+)([MI])(\d+)_(\d+)", path.stem)
    if match:
        subject, run, activity, task_code, trial = match.groups()
        activity_name = {"M": "Motor execution", "I": "Motor imagery"}[activity]
        task_name = TASKS.get(int(task_code), "Unknown task")
    else:
        subject, run, activity_name, task_code, trial, task_name = (
            "Unknown", "Unknown", "Unknown", "Unknown", "Unknown", "Unknown"
        )

    fig = make_subplots(
        rows=n_channels, cols=1, shared_xaxes=True, vertical_spacing=0.008,
        subplot_titles=[f"Channel {i} · {CHANNELS[i]}" for i in range(n_channels)]
    )
    for i in range(n_channels):
        fig.add_trace(go.Scatter(
            x=time, y=eeg[:, i], mode="lines", name=f"{i}: {CHANNELS[i]}",
            customdata=samples,
            hovertemplate=(
                "Time: %{x:.3f} s<br>Electrode: " + CHANNELS[i] +
                f" (channel {i})<br>Sample: " + "%{customdata}<br>" +
                "Amplitude: %{y:.2f} µV<extra></extra>"
            ),
            line=dict(width=1)
        ), row=i+1, col=1)
        fig.update_yaxes(title_text="µV", row=i+1, col=1, tickfont=dict(size=8))
    fig.update_xaxes(title_text="Time (seconds)", row=n_channels, col=1)
    fig.update_layout(
        title="EEG Explorer · 16-channel recording",
        height=1900, width=1250, hovermode="x", showlegend=False,
        template="plotly_white", margin=dict(l=90, r=35, t=90, b=55)
    )

    stats = []
    for i in range(n_channels):
        x = eeg[:, i]
        stats.append({
            "Channel": i, "Electrode": CHANNELS[i],
            "Min (µV)": f"{np.min(x):.2f}", "Max (µV)": f"{np.max(x):.2f}",
            "Mean (µV)": f"{np.mean(x):.2f}", "Std dev (µV)": f"{np.std(x, ddof=1):.2f}"
        })
    stats_html = pd.DataFrame(stats).to_html(index=False, border=0)

    properties = [
        ("File", path.name), ("Participant", f"S{subject}"),
        ("Run", run), ("Recording marker", activity_name),
        ("Task code", task_code), ("Task", task_name), ("Trial", trial),
        ("Channels", str(n_channels)), ("Samples", str(n_samples)),
        ("Sampling rate", f"{FS} Hz"), ("Duration", f"{n_samples/FS:.2f} seconds"),
        ("Units", "microvolts (µV)")
    ]
    props_html = "".join(
        f"<tr><th>{escape(k)}</th><td>{escape(v)}</td></tr>" for k, v in properties
    )
    plot_html = fig.to_html(full_html=False, include_plotlyjs="cdn")
    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>EEG Explorer</title>
    <style>body{{font-family:Arial,sans-serif;background:#f6f7f9;color:#20242a;margin:25px}}
    main{{max-width:1400px;margin:auto}}section{{background:white;padding:20px;margin:18px 0;border:1px solid #ddd;border-radius:10px}}
    table{{border-collapse:collapse;width:100%}}td,th{{padding:8px;border-bottom:1px solid #eee;text-align:left}}
    th{{background:#f3f5f7}}.plot{{overflow-x:auto}}</style></head><body><main>
    <h1>EEG Explorer</h1><section><h2>Recording properties</h2><table>{props_html}</table></section>
    <section><h2>Interactive waveforms</h2><p>Hover to see time, electrode, sample and amplitude in µV. Zoom and pan with the graph toolbar.</p>
    <div class="plot">{plot_html}</div></section>
    <section><h2>Channel statistics</h2>{stats_html}</section>
    <section><h2>Interpretation notes</h2><ul>
    <li>EEG measures voltage differences at scalp electrodes; it is not a direct measurement of focus.</li>
    <li>Channel order: {", ".join(CHANNELS)}.</li>
    <li>Filename I means imagery recording set, but task code 1 is baseline eyes open (BEO), not a movement task.</li>
    <li>Frequency bands require frequency analysis; individual waveform wiggles do not each have a specific meaning.</li>
    <li>MILimbEEG recordings were hardware-filtered at 5–50 Hz with a 60 Hz notch.</li>
    </ul></section></main></body></html>"""
    output = path.with_name(path.stem + "_EEG_Explorer.html")
    output.write_text(html, encoding="utf-8")
    print(f"Created: {output}")

if __name__ == "__main__":
    main()
