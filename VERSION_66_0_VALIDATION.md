# Version 66.0 Validation Checklist

## Automated checks completed

- JavaScript syntax checks for all active inline scripts and `timetable-studio.js`.
- HTML script/style balance and referenced static element IDs.
- Git whitespace validation.
- Pure generator test covering teachers, classes, subjects, combined classes, collision validation, candidate generation and activation conversion.
- Preservation test for temporary-replacement and non-teaching fields during master conversion.
- Public-source scan for embedded personal Gmail/Yahoo/Outlook/Hotmail addresses.

## Required authenticated checks before merging

1. Publish the Version 66.0 Firestore rules.
2. Open Admin Dashboard → Timetable Studio as Principal/Admin.
3. Confirm the active master imports into components and allocation cards.
4. Save a named Draft and reopen it from the Version Library.
5. Delegate Timetable Studio to a non-Admin UID and verify that the member can save drafts but cannot activate or delete.
6. Generate at least two candidates and confirm both remain stored with different seeds.
7. Test drag/drop on a computer and tap-to-move/swap/replace on a phone.
8. Confirm a conflict-increasing move is rejected and undo/redo works.
9. Confirm Mark Ready remains blocked when any hard conflict or unplaced card exists.
10. Activate one validated test candidate only after reviewing its timetable.
11. Confirm the former operational master appears as an Inactive preserved version.
12. Refresh the main app and verify Teacher Wise, Class Wise, Day Wise, Free Teachers and Proxy Allotment use the newly active timetable.
13. Reactivate the preserved former version and confirm rollback.

Do not merge or deploy if Firestore rules are not published or any activation/rollback test fails.
