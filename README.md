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
- [Python 3.13](https://www.python.org/downloads/) — choose the latest 3.13.x release.
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
.\.venv\Scripts\Activate.ps1
```

**macOS or Linux:**

```sh
python3.13 -m venv .venv
source .venv/bin/activate
```

The `.venv/` folder is ignored by Git. This repository does not yet include a dependency list or runnable entry point, so there is no program to launch yet. Code will go in `source/`; project notes will go in `documentation/`.

## Contribute

Before starting work, update `main` and create a branch for your task:

```sh
git switch main
git pull --ff-only
git switch -c group/short-task-name
```

Commit and push your branch, then open a pull request to `main` for review. Do not push task changes directly to `main`.

## License

[MIT License with attribution requirement](LICENSE)
