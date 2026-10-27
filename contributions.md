# Contributing to Mind-Games

Thanks for helping build Mindball and future EEG-controlled mini-games.

## Project phases

- **Phase 1:** Build and test the core Mindball game.
- **Phase 2:** Design and build EEG-controlled mini-games in small teams.

Coordinate with your subgroup before taking on a task. The current setup and project status are in the [README](README.md).

## Before you start

Install:

- [Git](https://git-scm.com/downloads)
- [Python 3.13.18](https://www.python.org/downloads/release/python-31318/)
- [Visual Studio Code](https://code.visualstudio.com/download)

This repository is currently a scaffold: it has no dependency list or runnable game entry point yet. Check the README and existing files before assuming setup or run commands.

## Development workflow

### Set your commit name and email

Git records a name and email on each commit; these identify your commits but do not sign you in to GitHub. Use a name you want shown on your commits and an email verified on GitHub (or your GitHub-provided noreply address):

```sh
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Check the values with `git config --global --get user.name` and `git config --global --get user.email`. `--global` applies to all your repositories; omit it to configure only this repository. See GitHub's guides for [setting your Git username](https://docs.github.com/en/get-started/git-basics/setting-your-username-in-git) and [setting your commit email](https://docs.github.com/en/account-and-profile/how-tos/email-preferences/setting-your-commit-email-address).

### Sign in to GitHub

Install the [GitHub CLI](https://cli.github.com/) and run `gh auth login`. Choose GitHub.com, HTTPS, and browser sign-in; sign in on GitHub with your username or email and complete any 2FA prompt. If Git Credential Manager opens the browser during a Git operation, follow that prompt instead. Never put your GitHub password or a token in `git config` or a Git command. See the [`gh auth login` guide](https://cli.github.com/manual/gh_auth_login).

### Pull the latest changes

`git pull` downloads changes from GitHub and updates your current branch. Before starting new work, update `main`:

```sh
git switch main
git pull --ff-only origin main
```

`--ff-only` stops safely if Git cannot update `main` without a merge; ask your subgroup for help rather than forcing it.

### Create a branch

A branch keeps your task separate from `main`. Create one from the updated `main` before editing files:

```sh
git switch -c phase1/short-task-name
```

Use a short name that describes your task and replace `phase1/short-task-name` in the commands below with your branch name. Do not make task changes directly on `main`.

### Commit and push your branch

A commit saves your selected changes locally. Review `git status`, then replace the example path with the file(s) you changed:

```sh
git status
git add path/to/changed-file
git commit -m "Describe the change"
```

`git push` uploads your branch to GitHub; it does not merge the work into `main`. The first push sets the upstream branch:

```sh
git push --set-upstream origin phase1/short-task-name
```

For later updates to the same branch, use `git push`.

### Pull requests for `main`

Pushing a task branch does not require a PR. Open one only when you want the team to review and merge that branch into `main`. On GitHub, choose **Pull requests → New pull request**, set the base to `main` and the compare branch to your task branch, review the changes, then create the PR. Include what changed and which tests you ran. Push follow-up commits to the same branch to update the PR.

## Testing

- For code changes, run the relevant automated checks and live-test the behavior in its intended environment when possible.
- For EEG or Arduino work, test with recorded or simulated data first, then test with the real hardware when available. State clearly which tests you ran and any hardware you could not test.
- For documentation changes, check commands and links, then run `git diff --check`.
- Never claim a test passed if it was not run.

## Pull requests

Include a short summary, the checks and live tests performed, and any remaining limitations. Keep unrelated changes out of the pull request.
