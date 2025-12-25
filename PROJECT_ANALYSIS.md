# Project Analysis

## Purpose and Scope
- The repository provides a CLI-focused localization workflow for Starsector mods, targeting Java/Kotlin source files under `src/` with extract, apply, and extend phases driven by YAML mappings.【F:README.md†L1-L24】
- V0 emphasizes human-driven translations and explicitly excludes built-in JAR decompilation or aggressive automated fixes, keeping the tooling deterministic and auditable.【F:AGENTS.md†L7-L113】

## Directory Layout Highlights
- **Tooling core**: `Localization_Tool/src/` hosts the Python implementation, with `run_localization.py` serving as a thin entrypoint into the shared CLI logic under `common/`.【F:Localization_Tool/src/run_localization.py†L1-L20】
- **Command dispatcher**: `Localization_Tool/src/common/localization_tool.py` aggregates subcommands for extracting mappings, processing unmapped strings, and detecting conflicts through a single argparse interface.【F:Localization_Tool/src/common/localization_tool.py†L4-L129】【F:Localization_Tool/src/common/localization_tool.py†L226-L317】
- **Top-level helpers**: Utility scripts such as `check_translation_status.py` support workflow reporting on merged YAML files (e.g., translation status breakdowns).【F:check_translation_status.py†L1-L34】

## CLI Entry Points and Flows
- **Extraction**: The `extract` command validates source/process directories, extracts AST-based mappings, optionally merges them with existing YAML rules, updates statuses, and persists the combined result.【F:Localization_Tool/src/common/localization_tool.py†L32-L129】
- **Unmapped processing**: The `process-unmapped` command loads a rules file to generate reports, list missing translations, or bulk-mark them as translated, ensuring at least one action flag is supplied.【F:Localization_Tool/src/common/localization_tool.py†L132-L172】
- **Conflict handling**: The `conflict` command loads rules, detects duplicate IDs/originals and translation mismatches, optionally emits a report, and can run configured resolution strategies.【F:Localization_Tool/src/common/localization_tool.py†L174-L225】
- **Quick start paths**: README examples show extract usage from the repository root, reinforcing the expected Scheme B directory layout under `legacy/Localization_File` for English/Chinese sources and outputs.【F:README.md†L14-L37】

## Observations
- The CLI is split between an interactive launcher (`main.py`) and the more structured argparse-based entry (`run_localization.py` → `common/localization_tool.py`), offering both guided and direct command flows.【F:Localization_Tool/src/main.py†L1-L131】【F:Localization_Tool/src/common/localization_tool.py†L4-L317】
- Workflow determinism and placeholder safety requirements from `AGENTS.md` govern how extraction, application, and extension should operate, guiding future changes to preserve stable ordering and validation behaviors.【F:AGENTS.md†L7-L113】
