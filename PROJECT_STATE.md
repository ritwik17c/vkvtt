# VKV Nalbari Timetable — Current Next Release

## v65.0 — Performance Architecture Reset
Reason: repeated v64.x feature patches left too much expensive work on initial page load and repeated calculations.

v65.0 keeps the full feature set but changes heavy operations to cached or on-demand execution.

Protected working feature: Bulk VL Update.
Master Timetable remains untouched.

## v65.1 — Operational Replacement Proxy Integration

Active temporary replacements are now included in Free Teachers and proxy candidate selection while inheriting the replaced teacher's regular timetable. The permanent roster and all 1,140 master timetable records remain untouched.

Configuration remains date-bound through Admin Dashboard → Temporary Leave-Vacancy Replacements. Source-code rollback: revert the v65.1 commit. Operational-record rollback: end, cancel or archive the replacement record in the dashboard.
