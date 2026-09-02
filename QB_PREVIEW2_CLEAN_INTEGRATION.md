# VKVTT Preview 2 — Clean Question Bank Integration

Date: 03/09/2026
Branch: `preview-2`

## Purpose
Integrate the current Question Bank and Question Paper Builder into Preview 2 without copying obsolete patches, diagnostics and legacy loaders wholesale.

## Safety rules
- Do not change `main` production while Preview 2 is being cleaned.
- Continue using the existing Firestore Question Bank data (`qbQuestions`, `qbConfig`, coordinator configuration and workflow fields).
- Preserve canonical `teacherUid` ownership and existing question IDs/status/history.
- Add and test clean entry points before replacing old Preview 2 pages.
- No bulk migration or Firestore rewrite is part of the UI integration.

## Phase 1 — Teacher Question Bank (started)
- [x] Add a parallel clean teacher entry page: `qb-preview2.html`.
- [x] Use the current canonical/paged teacher-history core from production without replacing the older Preview 2 core.
- [x] Add the shared active-subject catalogue required by the current core/importer.
- [x] Add the shared Excel/Word bulk-import parser.
- [x] Add teacher self-service Excel/Word bulk import.
- [x] Keep the old `qb-module-v2.html` untouched for rollback/comparison.
- [ ] Runtime test teacher sign-in, typed draft, typed submission, history total, next-100 paging and verified-bank loading.
- [ ] Runtime test Excel import and Word Analyse & Preview before any save.
- [ ] Bring the latest returned-question correction/resubmission UX after Phase 1 smoke test.

## Phase 2 — Coordinator
- [ ] Clean verification queue.
- [ ] Queue ageing and oldest-first review.
- [ ] Corrected/resubmitted badge/filter.
- [ ] Return feedback and revision/workflow visibility.

## Phase 3 — Principal/Admin
- [ ] Clean QB configuration and coordinator assignment.
- [ ] Principal workflow visibility.
- [ ] Submission/verified leaderboards with clear volume-vs-quality distinction.
- [ ] This Month / Session / All Time scopes and drill-downs.
- [ ] Admin Excel/Word import with canonical UID safeguards.
- [ ] Keep integrity/audit tools separate from normal daily UI.

## Phase 4 — Question Paper Builder
- [ ] Verified-bank selection and section targets.
- [ ] Marks/count health checks.
- [ ] Parent/subquestion structures and numbering.
- [ ] Internal choice / attempt-N / passage-case structures.
- [ ] Saved/versioned lifecycle: Draft → Ready → Reviewed/Corrections → Final → Locked.

## Cleanup gate
The older Preview 2 QB entry/files will not be deleted until the clean entry passes runtime testing and the Principal approves replacement.
