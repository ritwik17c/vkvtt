# VKV Nalbari Timetable and Daily Proxy Management System

## v57.0 — Safe Leave Import & Legacy Accounting Update

- Master Timetable Import / Restore accepts JSON only and remains separate from Leave Import.
- Approved Leave / OD / Special Excel import validates the entire workbook before saving.
- Any genuine validation error blocks the whole import; no partial import is performed.
- Dated approved events are stored as operational leave/status records.
- Non-dated legacy balances are preserved separately as **Legacy Leave Accounting**. No date is invented.
- Legacy accounting is read-only reference data and is not used for proxy coverage or dated leave events.
- Exact duplicate dated records and duplicate legacy accounting items are skipped.
- Error Report and Legacy Accounting exports are available.
- Approved Leave Viewer remains read-only.
- Date display is dd/mm/yyyy throughout visible reporting.
