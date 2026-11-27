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
9. A read that returns nothing, "?", `unknown` or `unavailable` is a failed read, not a pass. Miss 161
   (task 37): a change was called complete while its live check read "?". Name the read before the
   review (step 2), and do not call the change complete until it returns the expected value.
10. Miss 163 (task 30, `home` PR 95): a change was called complete after the merge and its live acceptance
   then failed, because the reads had not been run against the deployed state. The seat's report before the
   merge says "ready for merge, not complete". Only a later run that has read every post-deploy check, with
   each read matching its expected value, says "complete". A live item whose expected value is not written
   down before the review is itself a failure: write it (entity, value) in the PR, and if the criteria give
   no read-only read for it, ask for one (step 2) instead of merging.

## Completion record (required before "complete")

Miss 118 (task 101, live check 10): a change was called complete after the merge without its live reads.
So the seat's final report and the PR body must carry this block; without it the change is not complete:

```
Live items: <each live item from the acceptance criteria, or "none">
Expected: <per live item, the entity and the value, written before the review>
Read 1: <connector path> at <read time> -> <quoted output> (matches: yes/no)
Post-deploy check: <entity and value that must be seen> -> <read time and quoted output, or "pending">
Synced and healthy (GitOps) / previous build ready to reflash (firmware): <quote or name>
Undos: <per step 6>
Status: <ready for merge, not complete | complete>
```

- Status line: "ready for merge, not complete" until every post-deploy check is read and matches; only then "complete".
- "Pending" is allowed in the PR; it is not allowed in the word "complete". Read it after the deploy, quote it, then say complete.
- If a live item has no read-only read, say so and ask for one; do not skip it.

Check a report before saying "complete": `python3 script/check_completion_record.py <file with the PR body or report>`.
It exits 1 when a record line (including `Status:`) is missing, or when the status is anything but
"not complete" while a read failed, did not match, or the post-deploy check is pending, empty, `?`, unknown,
unavailable or has no read time. It exits 2 on bad usage. Wiring it into the seat's refusal of "complete" is
fleet task 1303 (`live-checks-pack`); that task should call this script.
