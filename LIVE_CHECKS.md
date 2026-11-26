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
   that must be seen. Do not say "done" before it has been read.
5. For a GitOps deploy also read "synced and healthy". For firmware keep the previous build ready to
   reflash.
6. Name both undos in the PR: `git revert` plus the Argo sync, and the Home Assistant backup restore.
7. Never send a command to a live device as a test; the kiosks, ReSpeaker satellites and BLE proxies are
   never exercised. Do not land a change that restarts HA across an adhan or iqamah reminder.
8. If a read does not match, the change is not complete: rework it or revert.
