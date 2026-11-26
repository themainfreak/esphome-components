# Live checks before a change is called complete

Applies to every change of squad homeassistant: firmware here (`esphome/**`, `platformio.ini`,
`sdkconfig.defaults*`) and the `home` repo (Argo deploys a merge live). A change is complete when its
live items have been read and match, not when it merges. This file is the written rule. Loading it at the
seat's start and refusing "complete" without it belong to the fleet model (the fleet squad).

1. List every live item in the task's acceptance criteria.
2. For each, name the exact read-only read (HA state, history, logbook or backup info through the
   `homeassistant` connector).
3. Run each read that can run before the deploy; quote the output with its read time in the PR.
4. A read that needs the deploy is written in the PR as a post-deploy check: the entity and the value
   that must be seen. Do not say "done" before it has been read, then quote its output with its read time in the completion record (O6).
5. For a GitOps deploy also read "synced and healthy". For firmware keep the previous build ready to
   reflash.
6. Name the undos in the PR by deploy path:
   - `home` (Argo): `git revert` plus the Argo sync, and the Home Assistant backup restore as the bigger fallback.
   - firmware: `git revert`, and reflash the previous build (step 5); no Argo sync applies.
7. Never send a command to a live device as a test; the kiosks, ReSpeaker satellites and BLE proxies are
   never exercised. Do not land a change that restarts HA across an adhan or iqamah reminder: before merging, read the prayer-time sensor states through the `homeassistant` connector (`GET /api/states`, the adhan/iqamah entities) and merge only when the next adhan, less the iqamah reminders at -5/-2 min, is clear.
8. If a read does not match, the change is not complete: rework it or revert.
