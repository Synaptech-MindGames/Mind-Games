Immediately read the contributions.md for instructions on how to work in the codebase.

This is a team project split into 2 phases.

## Tool prerequisites
Use Python 3.13.18 for project tooling. Before invoking a tool that requires Git or Python, check that Git and Python 3.13.18 are installed. Automatically install whichever is missing, then retry the tool.

## Change and verification rules
- For code or documentation changes, make the smallest complete, working addition and avoid unrelated refactoring.
- After every change, run relevant checks and live-test the changed behavior in its real environment. If hardware or another blocker prevents live testing, state that limitation and give instructions on what the user needs to do to have it pass.

## Issues, commits, and pull requests
- Before starting work, search for a matching issue. Reuse it, or create an issue assigned to `MarsLuay` before referencing it in a commit or pull request; do not link nonexistent issue numbers.
- Split large or multi-scope work into multiple focused issues and small commits, one issue per independent work item. Reference the relevant issue in each commit and PR, and keep unrelated work out of each change.
- Pushing to a task branch does not require a PR. Open a PR only when proposing that branch's changes for merging into `main`; changes intended for `main` must go through a PR.
- Close an issue only after its associated work is pushed and verified, and its resolving PR is merged when applicable. Use a closing keyword only if the PR fully resolves the issue.

## Branch synchronization and push recovery
- Before implementation, fetch and fast-forward local `main`, create or switch to a task branch, pull `origin/main` into that branch with `git pull --no-rebase origin main`, resolve all conflicts one file or hunk at a time, and push the synchronized branch before editing. Inspect both sides and preserve intended changes; never choose `ours` or `theirs` blindly or stop just because there are many conflicts.
- If a push is rejected because the remote task branch advanced, never force-push. Pull the advanced task branch into the current branch with `git pull --no-rebase origin <task-branch>`; if `main` advanced, pull `origin/main` into the task branch. Resolve every conflict individually until none remain, finish the merge with an issue-referencing commit, rerun relevant checks, and retry the push. Repeat if the remote advances again.
