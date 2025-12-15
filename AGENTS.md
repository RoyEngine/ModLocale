
---

# AGENTS.md（完整内容）

```md
# AGENTS — Starsector Localization Tool (V0)

This file defines the working contract for automated agents (e.g., Codex) and contributors.
Follow it strictly.

## V0 Goal
Deliver a CLI closed loop for Java/Kotlin source localization:
1) Extract: parse `.java/.kt/.kts` under `src/` using Tree-sitter and generate/update rules (YAML/JSON).
2) Apply: apply translated rules to an English source tree and produce a translated output tree + report.
Translation is manual. No machine translation in V0.

## Canonical Repo Layout (Scheme B)
- Tool code (canonical): `legacy/Localization_Tool/src`
- Fixtures (do not move):
  - English: `legacy/Localization_File/source/English/<ModFolder>/src`
  - Chinese: `legacy/Localization_File/source/Chinese/<ModFolder>/src`
- Baseline extracted mappings (keep for regression):
  - `legacy/Localization_File/output/Extract_English/**/English_mappings.yaml|json`
  - `legacy/Localization_File/output/Extract_Chinese/**/Chinese_mappings.yaml|json`

## Non-goals (V0)
- Do NOT implement jar decompile/unpack in the main loop.
- Do NOT translate `data/localization` CSV/JSON.
- Do NOT perform global search/replace by raw text.

## Rules File Compatibility (MUST)
Rules YAML must remain backward compatible with the current schema:
- Top-level: `version`, `created_at`, `mappings: []`
- Each mapping keeps at least:
  - `id`, `original`, `translated`, `context`, `status`, `placeholders`
You MAY add new fields (e.g., `rel_path`, `loc`, `key`) but MUST NOT rename/remove existing ones.

## Determinism Requirements
- Mod folder enumeration must be sorted (by folder name).
- File enumeration inside `src/` must be sorted (by relative path).
- Apply replacements must be done per-file in reverse order of location (descending start_byte) to avoid offset shifts.

## Kotlin Safety Requirements
- Kotlin strings with interpolation (`$var` or `${expr}`) are high risk.
- Extract MUST collect placeholders into `placeholders`.
- Apply MUST validate placeholders consistency before replacement:
  - If mismatch, skip replacement and record reason `placeholder_mismatch`.

## Target CLI (V0 interface to implement/keep)
Run from repo root:

### Extract (recursively for all mods under a language root)
- `python legacy/Localization_Tool/src/main.py extract --lang English --source-root legacy/Localization_File/source/English --out-root legacy/Localization_File/output`
- `python legacy/Localization_Tool/src/main.py extract --lang Chinese --source-root legacy/Localization_File/source/Chinese --out-root legacy/Localization_File/output`

### Apply (one mod at a time)
- `python legacy/Localization_Tool/src/main.py apply --src legacy/Localization_File/source/English/<ModFolder> --rules <PATH_TO_YAML> --out <OUT_DIR>`

## Reporting (MUST)
Apply must produce a machine-readable report (JSON preferred) including:
- total mappings processed
- replaced count
- skipped count (by reason)
- failures (by reason, including file + mapping id)
At minimum include reasons:
- `placeholder_mismatch`
- `locate_failed`
- `status_not_translated` (or equivalent)

## Definition of Done (V0)
- Extract produces mapping files for each `<ModFolder>` under English/Chinese roots.
- After manually editing some `translated` + setting `status=translated`, Apply generates an output tree with valid string literal syntax.
- Report is produced and allows tracing any skipped/failed item.
