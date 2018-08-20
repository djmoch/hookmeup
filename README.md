# Hook Me Up

A Git hook to automate your Pipenv and Django workflows

## Requires

- Python 3.5 or newer

## Features

- Cleans and Syncs your pipenv if there are changes to Pipfile
- (TODO) Migrates your Django DB to it's current working state, applying
  and unapplying migrations as necessary

## Notes

- Nominal Django migrate case
  - If manage.py exists
    - `git diff --name-status` the whole branch
    - Look for file changes in a 'migrations' path
      - If deleted, unapply
      - If changed, reapply (shouldn't usually happen)
      - If added, apply
    - For third party apps
      - Always run to the latest migration (must be done after Pipenv
        update)
- Should we adjust pipenv based on Pipfile.lock instead of Pipfile?
