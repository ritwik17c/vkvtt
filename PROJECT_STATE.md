# VKV Nalbari Timetable — Current Project State

## Next deployment: v64.2
The actual deployed/tested baseline is v64.1. Experimental v64.3/v64.4 packages were not deployed.

### Test in this order
1. Existing leave corrections/counts load unchanged.
2. Correct Expected Units on one known wrong item.
3. Run Leave Integrity Checker.
4. Preview Safe Exact Duplicate Remover before confirming any deletion.
5. Preview April VL bulk update.
6. Mark one genuine VL exception and verify bulk apply preserves it.
7. Confirm Master Timetable remains unchanged.
