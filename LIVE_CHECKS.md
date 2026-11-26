# Live checks before a change is called complete

A change to this repo that ships firmware (anything under `esphome/`, `platformio.ini`,
`sdkconfig.defaults*`) is not complete when it merges. It is complete when its live items
have been read and match.

1. Before `merge_ready`, list every live item in the task's acceptance criteria.
2. For each item, name the exact read-only read that proves it (for example a Home Assistant
   state, history or logbook read through the `homeassistant` connector).
3. Run each read that can run before the deploy and quote the output with its read time in the PR.
4. For a read that only makes sense after the deploy, write it in the PR as a post-deploy check,
   with the entity and the value that must be seen. Do not say "done" until it has been read.
5. Never send a command to a live device to test it. Reads only.
6. If a read does not match, the change is not complete: rework it, or revert with `git revert`.
