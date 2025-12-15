# Starsector Mod 源码本地化工具（V0 / CLI 闭环）

本仓库用于对 **Starsector Mod 的 Java/Kotlin 源码（src/**）**进行字符串提取与回填替换。
V0 阶段目标是实现 **CLI 闭环**：Extract →（人工翻译）→ Apply，并输出可追踪报告。

> 重要说明：
> - 本工具不做机器翻译，翻译由人工在规则文件中填写。
> - V0 不负责 jar 反编译/解包：请先准备好 mod 的 `src/` 目录。
> - V0 不处理 `data/localization` 的 CSV/JSON（二期再做）。

---

## 1. 仓库结构（方案 B / 固定路径）

### 1.1 工具代码（不要改动位置）
工具源码位于：

legacy/Localization_Tool/src/

r

### 1.2 输入源码（两种语言 / 多 Mod 目录）
请把各 Mod 源码按以下结构放置（每个 Mod 单独一个文件夹，内部必须包含 `src/`）：

legacy/Localization_File/source/
English/
<ModFolderA>/
src/...
<ModFolderB>/
src/...
Chinese/
<ModFolderA>/
src/...
<ModFolderB>/
src/...

shell

> 注意：本工具支持“多 Mod 递归扫描”，不支持 `source/English/src` 这种单一扁平结构。

### 1.3 规则文件与输出目录
历史与生成物统一放在：

legacy/Localization_File/output/
Extract_English/ # 从英文源码提取出的规则文件（用于翻译与 apply）
Extract_Chinese/ # 从中文源码提取出的规则文件（用于对照/学习）
Apply_En2Zh/ # apply 输出（英文源码替换后生成的翻译源码树）

yaml

---

## 2. V0 功能说明

### 2.1 Extract（提取字符串，生成规则文件）
- 输入：`legacy/Localization_File/source/<Lang>/<ModFolder>/src/**/*.(java|kt|kts)`
- 输出：`legacy/Localization_File/output/Extract_<Lang>/**/<Lang>_mappings.yaml|json`

Extract 的核心是 **AST 提取**：使用 Tree-sitter 提取字符串字面量以及上下文信息（如 node_type/parent_types）。

### 2.2 人工翻译（编辑规则文件）
规则文件是 YAML，人工主要编辑每条 mapping 的 `translated` 与 `status` 字段。

> 推荐只对 English 规则做翻译（English_mappings.yaml），Chinese 规则主要作为“对照/学习基线”，不建议直接用于 apply。

### 2.3 Apply（将翻译写回英文源码，生成输出源码树）
- 输入：英文源码目录 + 规则文件（通常是 English_mappings.yaml）
- 输出：输出目录下生成新的 `src/` 树，并生成 report

---

## 3. 规则文件（YAML）格式（与你当前文件一致）

规则文件结构示例：

```yaml
version: "1.0"
created_at: "2025-12-15T22:06:54.233731"
mappings:
  - id: "C:\\...\\src\\a\\b\\C.java:73"
    original: "Hello"
    translated: "你好"
    context:
      parent_types: ["binary_expression", "..."]
      node_type: "string_literal"
    status: "untranslated"
    placeholders: []

3.1 字段解释（V0 关键字段）
id：当前为 绝对路径 + :行号（兼容历史产物）。
V0 会逐步增强：新增稳定字段（如 rel_path、loc、key）以避免换机器/换目录导致失配。

original：源字符串

translated：译文（人工填写）

context.node_type / context.parent_types：Tree-sitter 上下文信息（用于更稳健的匹配/回归）

status：建议取值：

untranslated：未翻译（待人工）

translated：已翻译（可用于 apply）

ignored：明确不翻译（保留原文）

stale：源码更新导致定位失效，需要人工复核

fuzzy：存在风险（例如 Kotlin 占位符不一致），默认不自动写回

placeholders：占位符/插值片段列表（见 Kotlin 部分）

3.2 English 与 Chinese 两类规则文件怎么用
English_mappings.yaml

original 是英文；你填 translated 为中文，并把 status 改为 translated

apply 推荐使用它

Chinese_mappings.yaml

通常 original 本身就是中文（可能 translated==original）

主要用途是“对照/学习基线”，用于后续 EN+ZH 对齐（learn/extend）

一般不用于 apply

注意：如果你发现 Chinese 规则里 status 仍为 untranslated，但 translated==original，这通常是提取时的默认状态，并不代表它真的未翻译。
V0 的报告/统计会逐步修正这一点（区分“参考基线”与“待翻译”）。

4. Kotlin 插值字符串（非常重要）
Kotlin 字符串中出现 $var 或 ${expr} 属于高风险：

Extract 阶段：应将 $var/${expr} 收集到 placeholders 列表。

Apply 阶段：必须校验占位符集合一致性：

译文必须保留同样的 placeholders（同名同数量）

不一致 → 标记为 fuzzy 或 placeholder_mismatch，默认跳过，不写回

V0 的原则是：宁可少替换，也不替坏代码。

5. CLI（V0 目标接口）
说明：以下命令定义为 V0 目标接口（若你现有 main.py 参数不同，后续会以此为准统一）。

从仓库根目录执行：

5.1 Extract（按语言递归提取所有 Mod）
提取 English：

bash

python legacy/Localization_Tool/src/main.py extract ^
  --lang English ^
  --source-root legacy/Localization_File/source/English ^
  --out-root legacy/Localization_File/output
提取 Chinese：

bash
python legacy/Localization_Tool/src/main.py extract ^
  --lang Chinese ^
  --source-root legacy/Localization_File/source/Chinese ^
  --out-root legacy/Localization_File/output
5.2 Apply（对单个 Mod 应用规则）
bash
python legacy/Localization_Tool/src/main.py apply ^
  --src legacy/Localization_File/source/English/<ModFolder> ^
  --rules legacy/Localization_File/output/Extract_English/<...>/English_mappings.yaml ^
  --out legacy/Localization_File/output/Apply_En2Zh/<ModFolder>
输出将包含：

Apply_En2Zh/<ModFolder>/src/...（翻译后的源码树）

Apply_En2Zh/<ModFolder>/report.json（统计与失败原因）

6. 常见问题排查
Q1：为什么没有提取到任何字符串？
检查目录是否符合：source/<Lang>/<ModFolder>/src

确认文件后缀为 .java/.kt/.kts

Q2：Apply 后 Kotlin/Java 语法出错？
通常是翻译内容导致引号/转义破坏，或 Kotlin placeholders 被删改

查看 report.json 中的失败原因（placeholder_mismatch / locate_failed 等）

Q3：规则里同样的英文文本出现多次？
规则按“出现点”记录，而不是按文本去重（避免同文不同译覆盖）

7. 路线图
V1：完善 EN+ZH 对齐学习（自动填充已翻译条目，补齐新增条目）

V2：支持 data/localization CSV/JSON 翻译

V3：更强的重构抗性（byte-range + AST context hash + 模糊匹配回落策略）

perl
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