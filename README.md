# Starsector Mod 源码本地化工具（V0 / CLI 闭环）

本仓库用于对 Starsector Mod 的 Java/Kotlin 源码（src/**）进行字符串提取与回填替换。

V0 阶段目标：以 CLI 方式完成三段最小闭环：
1) Extract（提取规则）
2) Apply（回填翻译）
3) Extend（EN+ZH 学习对齐：自动填充已翻译项 + 补齐新增项）

重要说明：
- 本工具不做机器翻译，翻译由人工在规则文件中填写。
- V0 不负责 jar 反编译/解包：请先准备好 mod 的 src/ 目录（作为前置步骤）。
- V0 不处理 data/localization 的 CSV/JSON（二期再做）。

---

## 1. 仓库结构（方案 B / 固定路径）

### 1.1 工具代码（不要改动位置）
legacy/Localization_Tool/src/

### 1.2 输入源码（两种语言 / 多 Mod 目录）
请把各 Mod 源码按以下结构放置（每个 Mod 单独一个文件夹，内部必须包含 src/）：

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

> 注意：src 下文件/目录排序不可控，但文件路径与相对位置可控。本工具会对枚举顺序做排序以保证输出稳定。

### 1.3 规则文件与输出目录
生成物统一放在：
legacy/Localization_File/output/
  Extract_English/   # 从英文源码提取的规则（用于人工翻译与 apply）
  Extract_Chinese/   # 从中文源码提取的规则（用于对照/学习基线）
  Apply_En2Zh/       # apply 输出（翻译后的源码树 + report）
  Extend_Learn/      # extend 输出（学习对齐后的规则文件/报告）

---

## 2. V0 三个最小可用阶段

### 2.1 Extract（MVP-Extract）
用途：从 src 提取字符串与上下文，生成规则文件。

输入：
- legacy/Localization_File/source/<Lang>/<ModFolder>/src/**/*.(java|kt|kts)

输出：
- legacy/Localization_File/output/Extract_<Lang>/**/<Lang>_mappings.yaml|json

命令：
python legacy/Localization_Tool/src/main.py extract ^
  --lang English ^
  --source-root legacy/Localization_File/source/English ^
  --out-root legacy/Localization_File/output

python legacy/Localization_Tool/src/main.py extract ^
  --lang Chinese ^
  --source-root legacy/Localization_File/source/Chinese ^
  --out-root legacy/Localization_File/output

注意：
- V0 Extract 只读取 src，不扫描 jar，不反编译。请先把源码准备好。

### 2.2 人工翻译（编辑规则文件）
规则文件是 YAML，人工主要编辑：
- translated：填写中文
- status：改为 translated（或 ignored/fuzzy 等）

推荐做法：
- 主要翻译 English_mappings.yaml（用于 Apply）
- Chinese_mappings.yaml 主要作为“对照/学习基线”，通常不直接用于 apply

### 2.3 Apply（MVP-Apply）
用途：把 rules 写回英文源码树，生成翻译后的 src 树与 report。

命令：
python legacy/Localization_Tool/src/main.py apply ^
  --src legacy/Localization_File/source/English/<ModFolder> ^
  --rules legacy/Localization_File/output/Extract_English/<...>/English_mappings.yaml ^
  --out legacy/Localization_File/output/Apply_En2Zh/<ModFolder>

输出将包含：
- Apply_En2Zh/<ModFolder>/src/...（翻译后的源码树）
- Apply_En2Zh/<ModFolder>/report.json（统计与失败原因）

原则：
- 替换按 start_byte 逆序写回，避免偏移导致定位错乱
- Kotlin 插值 placeholders 不一致 → 默认跳过，并写入 report（宁可少替换也不替坏）

### 2.4 Extend（MVP-Extend-Learn）
用途：用已存在的 EN + ZH 源码做学习对齐，自动填充可靠的翻译，并补齐新增未翻译条目。

典型场景：
- Mod 更新后：你希望保留旧翻译、自动填回已确认翻译，并新增待翻译项

命令（示例）：
python legacy/Localization_Tool/src/main.py extend ^
  --en-src legacy/Localization_File/source/English/<ModFolder>/src ^
  --zh-src legacy/Localization_File/source/Chinese/<ModFolder>/src ^
  --base-rules legacy/Localization_File/output/Extract_English/<...>/English_mappings.yaml ^
  --out legacy/Localization_File/output/Extend_Learn/<ModFolder>

---

## 3. 规则文件（YAML）格式（兼容你现有文件）

顶层结构：
version / created_at / mappings: []

每条 mapping 至少包含：
- id, original, translated, context, status, placeholders

V0 建议逐步增强但保持兼容：
- 新增 rel_path / start_byte / end_byte 等稳定定位字段
- Apply 优先使用 byte-range 精确定位；旧规则缺字段时才降级兜底

---

## 4. 常见问题排查

Q1：为什么没有提取到任何字符串？
- 检查目录是否符合：source/<Lang>/<ModFolder>/src
- 确认文件后缀为 .java/.kt/.kts

Q2：Apply 后 Kotlin/Java 语法出错？
- 多数是译文破坏引号/转义，或 Kotlin placeholders 被删改
- 查看 report.json：placeholder_mismatch / locate_failed 等原因

Q3：规则里同样的英文文本出现多次？
- 规则按“出现点”记录，而不是按文本去重（避免同文不同译覆盖）
