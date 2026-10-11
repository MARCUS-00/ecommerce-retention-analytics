# Dashboard archive (local only, not part of the deliverable)

Everything in this folder is superseded. **The authoritative report is
`../ecommerce_retention_dashboard_final.pbix`** (SHA-256
`16a2401e8e88350428442a2b349e397b22b9f647d02b9f2c638f985b51841560`, October 2026).

This folder is listed in `.gitignore`, so only this README is tracked. The files below stay on the
local disk for rollback and history, and none of them has been checked against the final report.

| Item | What it is | Status |
|---|---|---|
| `ecommerce_retention_dashboard_final_BACKUP_pre_polish.pbix` | The report as it was before the final polish pass. SHA-256 `8adaca54710ac82347597202ae83ad9c8e826b4525b288827da17ad9550f91db` | Rollback copy only |
| `pbip_ecommerce_analytics_old/` | An early Power BI Project (PBIP) development copy that predates the final fixes | Obsolete |
| `pbip_final_export/` | A PBIP export made from the final report (its own README says "post-polish source") | Not verified against the final .pbix |
| `screenshots_original/` | The four page screenshots as first captured, with the full Power BI Desktop window (ribbon, side panes, taskbar). Replaced by cropped versions in `../screenshots/` | Superseded |
| `ecommerce_retention_dashboard_final_ORIGINAL_3361bc56.pbix` | The approved report before the October 2026 presentation fix (card padding, text colour, page 3 footnote). SHA-256 `3361bc56936996c912274accf7997f527702e6b280161a8e260aa7d8c6c32f20` | Rollback copy only |
| `screenshots_pre_oct2026_fix/` | The cropped page screenshots that were current until the October 2026 fix | Superseded |
| `pbip_work_copy/` | The temporary PBIP working copy used to apply the polish edits (it includes the alt-text edits) | Not verified against the final .pbix |

Notes
- The three PBIP folders had their `.pbi/cache.abf` removed. That file is a local data cache that
  Power BI recreates on refresh, so each project needs a refresh against the database when opened.
- The duplicate `ecommerce_retention_dashboard.pbix` (byte-identical to the final file) was removed
  from the working tree in October 2026. It is still in Git history.
- Do not edit or refresh these files, and do not publish them.
