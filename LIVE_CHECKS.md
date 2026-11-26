# Live checks before a change is called complete

Applies to every change of squad homeassistant: firmware here (`esphome/**`, `platformio.ini`,
`sdkconfig.defaults*`) and the `home` repo (Argo deploys a merge live). A change is complete when its
live items have been read and match, not when it merges.

Loading this file at the seat's start (as a context pack for the squad's seats in both repos) and refusing
"complete" without the quoted reads belong to the fleet model. That work is requested from the fleet squad
as task 1303 (subtask `live-checks-pack`; done_when includes a test that a seat is refused "complete"
when the live-read quotes are missing); this file merges after it. This file is the single source: the
`home` repo links to it and keeps no copy.

1. List every live item in the task's acceptance criteria.
2. For each, name the exact read-only read (HA state, history, logbook or backup info through the
   `homeassistant` connector).
3. Run each read that can run before the deploy; quote the output with its read time in the PR.
   A change that takes the operations home backup route (O2) must quote, as read-only readings with
   their read times: an HA backup (`WS /backup/info`) taken after HA's last deployed change or within
   24 h, and a restore drill that succeeded within 7 days. That route does not cover a change to a
   lock, a gas or water valve, or heating.
4. A read that needs the deploy is written in the PR as a post-deploy check: the entity and the value
   that must be seen. Do not say "done" before it has been read, then quote its output with its read
   time in the task's completion record (O6).
5. For a GitOps deploy also read "synced and healthy". For firmware name the previous build kept ready
   to reflash.
6. Name the undos in the PR by deploy path:
   - `home` (Argo): `git revert` plus the Argo sync, and the Home Assistant backup restore as the bigger
     fallback.
   - firmware: `git revert`, and reflash the previous build named in step 5; no Argo sync applies.
     Under the home backup route, also the Home Assistant backup restore.
7. Never send a command to a live device as a test; the kiosks, ReSpeaker satellites and BLE proxies are
   never exercised. A change that restarts HA must not land across an adhan or the iqamah reminders that
   follow it (adhan + learned gap, reminders at -5/-2 min before the iqamah). The merge is the merge
   queue's, never the seat's, so check the window before the queue lands the change: read
   `GET /api/states` through the `homeassistant` connector and pick the prayer-time entities (entity ids
   containing `adhan` or `iqamah`; the ids are not fixed in this repo, so quote the ids you read). Hold
   the change if any adhan or iqamah reminder falls within the window the restart covers.
8. If a read does not match, the change is not complete: rework it or revert.
