# Mind-Games

A team project to recreate Mindball, then build Mario Party–style brain-controlled mini-games.

## The idea

Two players wear EEG headsets. The game turns their brain activity into a score. In Mindball, the ball moves toward the less-relaxed player, so the calmer player wins. A key project challenge is testing whether the EEG score reliably measures relaxation.

## Project plan

1. **Phase 1 — Mindball:** Build the EEG-to-game pipeline and a working Mindball prototype. The first milestone is a Python tool that streams or replays EEG data and saves recordings.
2. **Phase 2 — Mini-games:** Small teams design and build new games that use EEG input.

Teams can work on EEG hardware and data, signal processing, artifact detection, game logic, Arduino/LED display, or optional EEG-model research. Each team should turn its research into a working build.

## Get started

### Install

Install:

- [Git](https://git-scm.com/downloads)
- [Python 3.13.18](https://www.python.org/downloads/release/python-31318/). Use this exact version for project tooling.
- [Visual Studio Code](https://code.visualstudio.com/Download)

### Get the project

```sh
git clone https://github.com/Synaptech-MindGames/Mind-Games.git
cd Mind-Games
```

### Set up Python

**Windows PowerShell:**

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe --version  # Expected: Python 3.13.18
.\.venv\Scripts\Activate.ps1
```

**macOS or Linux:**

```sh
python3.13 -m venv .venv
source .venv/bin/activate
python --version  # Expected: Python 3.13.18
```

## Contribute

Before starting implementation, update `main`, create or switch to a task branch, merge the latest `origin/main` into it, resolve any conflicts, and push the prepared branch:

```sh
git fetch origin
git switch main
git pull --ff-only origin main
git switch -c group/short-task-name
git pull --no-rebase origin main
git push --set-upstream origin group/short-task-name
```

For an existing task branch, switch to it instead of creating it, then pull `origin/main` into it and push before editing. If the pull reports conflicts, resolve them one file or hunk at a time, inspect both sides, and continue until none remain; never choose `ours` or `theirs` blindly. Run relevant checks and push the synchronized branch before beginning implementation.

If a push is rejected because the remote branch advanced, do not force-push. Pull the advanced task branch (`git pull --no-rebase origin group/short-task-name`) or `origin/main` if `main` advanced, resolve conflicts individually, rerun relevant checks, and retry the push. Repeat if the remote changes again.

Search for a matching GitHub issue before starting work. Reuse it, or create and assign one to `MarsLuay` before linking any commit or pull request. Split large or multi-scope work into multiple focused issues and small commits, one issue per independent work item. Reference the relevant issue in each commit and pull request; use `Closes #<number>` only when the PR fully resolves it. Close issues only after the work is pushed, verified, and merged when applicable.

A task-branch push does not require a PR. When changes are ready to be merged into `main`, open a PR with `main` as the base; do not push task changes directly to `main`.

## License

[MIT License with attribution requirement](LICENSE)
