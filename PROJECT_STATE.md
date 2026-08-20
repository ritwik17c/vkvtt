# VKV Nalbari Timetable — Current Project State

## Current integrated release: v64.1

This release exists because the v64 files were present in the repository package but were not actually wired into the production `index.html` / `admin-dashboard.html`, leaving the visible app on v62.

### v64.1 integrated fixes
- Production `admin-leave-editor.html` is now the clean v64 editor.
- Admin Dashboard actually loads the v64 Quick Add Leave add-on.
- Main homepage permanently shows **Today’s Proxy Allotment (All Teachers)**.
- The all-teachers proxy button remains visible even when today's final proxy sheet has not yet been published; the view then reports that status.
- Google sign-in now explicitly offers account selection.
- Signed-in users have **Use another Google account** in the top cloud bar.
- Cache-busting links use v64.1.

### Important data-safety rule
Feature updates must not rewrite `master/current` unless the administrator explicitly uses the Master Timetable Import/Restore workflow.

### Required regression checks after deployment
1. Main login screen says Cloud v64.1.
2. Use another Google account opens Google account selection.
3. Homepage shows My Proxy Today, Proxy Allotment, and Today’s Proxy Allotment (All Teachers).
4. All-teachers proxy button remains visible before finalisation.
5. Admin Dashboard shows Quick Add Leave.
6. Leave editor uses the clean row logic: one Date Row per click and one Date-Range Row per click.
7. Existing timetable and leave data are unchanged.
