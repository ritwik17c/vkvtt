# Version 66.0 — Timetable Studio

## Purpose

Version 66.0 adds a non-destructive timetable design and generation system. A generated timetable is never an automatic replacement for the operational master. Every saved candidate remains an independently named version and can be activated later by the Principal/Admin.

## New Timetable Studio

- Professional desktop and mobile-responsive workspace.
- Complete version library with Draft, Ready, Active and Inactive states.
- Automatic snapshot of the previous operational master before the first Studio activation.
- Open an active version only as a safe working copy.
- Copy-on-write protection for an inactive historical version: the first edit becomes a new Draft instead of rewriting history.
- JSON export, share summary, print and explicit Admin-only deletion.

## Editable components

- Teachers, codes, daily load limits and unavailable slots.
- Classes and sections with their own active-period patterns.
- Subjects, short names, card colours and daily repetition limits.
- Venues/rooms, types, capacities and unavailable slots.
- Period numbers and bell-time labels.
- Reusable teacher allocation cards containing subject, teacher(s), class(es), venues, weekly periods, lesson length, priority and preferred days.
- Combined classes and co-teaching are represented as single timetable events and expand safely into the existing master-record format on activation.

## Generation

- Every click receives a new random seed and produces a separately stored candidate.
- Each candidate retains its seed, parameter snapshot, attempt count, score and unplaced cards.
- Hard constraints: class, teacher and venue collisions; unavailability; consecutive double/triple periods; joined classes.
- Soft scoring: lesson distribution, repeat-subject avoidance, teacher daily load, gaps and last-period preference.
- Generator yields periodically so the interface remains responsive.

## Visual editor

- Colour-coded timetable cards.
- Desktop drag-and-drop.
- Mobile tap-card then tap-destination workflow.
- Move, swap and replace operations.
- Unplaced-card tray.
- Venue reassignment.
- Card locking for future generation.
- Thirty-step undo/redo history.
- Conflict-increasing edits are rejected immediately.

## Validation and activation

- Full teacher, class, venue, availability and entity-reference validation.
- A version cannot be marked Ready or activated with a hard conflict or unplaced lesson.
- Delegated members may configure, generate, edit, validate and save non-active versions.
- Only the Principal/Admin may activate or delete versions.
- Activation updates `master/current` only after confirmation and records an immutable activation audit.
- Proxy, Free Teachers, workload and public timetable views continue to use only the active operational master.

## Firestore additions

- `timetableVersions/{versionId}` — complete named version documents.
- `timetableActivations/{activationId}` — immutable Admin activation audit.
- `authorizedUsers.permissions.timetableStudio` — independent delegated Studio permission.

The updated rules in `firestore.rules.v62.txt` must be published before the Studio is released.

## Rollback

- Source rollback point: Version 65.4 commit `e1bf53d`.
- Operational rollback: open an earlier retained timetable, validate it and activate it.
- Existing attendance, leave, proxy, temporary-replacement and non-teaching data are preserved during timetable activation.
