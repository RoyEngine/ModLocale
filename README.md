# ModLocale

一个功能强大的本地化工具，用于处理游戏模组和应用程序的翻译工作流，支持从双语数据生成翻译规则、自动冲突检测和解决、翻译回写以及翻译报告生成。

## 功能特性

### 1. 双语数据处理
- 支持加载和对齐EN+ZH双语数据
- 自动检测数据格式和完整性
- 容错机制，处理数据不一致情况

### 2. 翻译规则生成
- 从双语数据自动生成翻译规则文件
- 支持增量更新，保留已翻译内容
- 智能合并，避免重复翻译

### 3. 冲突检测和解决
- 自动检测重复ID、重复原始字符串和翻译冲突
- 支持多种冲突解决策略：
  - `latest`: 使用最新的映射
  - `first`: 使用第一个映射
  - `longest`: 使用最长的翻译
  - `shortest`: 使用最短的翻译
  - `manual`: 手动解决

### 4. 翻译报告生成
- 支持Markdown和JSON格式报告
- 包含翻译进度、冲突统计、质量评估等信息
- 按文件路径分组统计，便于管理

### 5. 翻译回写
- 支持将翻译应用到源代码文件
- 精确的字节级替换
- 回写前自动备份

### 6. 性能优化
- **并行处理**：支持多线程并行文件处理，加速字符串提取和翻译回写
- **缓存机制**：智能检测文件变更，只处理已变更文件，支持增量更新
- **内存优化**：使用生成器替代列表，减少内存占用，支持处理大型项目

## 安装

### 环境要求
- Python 3.8+
- pip包管理工具

### 安装步骤

1. 克隆项目仓库
   ```bash
   git clone https://github.com/your-username/Localization_Tool.git
   cd Localization_Tool
   ```

2. 创建并激活虚拟环境
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```

3. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

## 快速开始

### 1. 生成翻译规则

```bash
# 使用命令行脚本
python main_workflow.py generate-rules --english-file English_mappings.yaml --chinese-file Chinese_mappings.yaml --output-file rules.yaml

# 或使用Python API
from src.common.yaml_utils import load_yaml_mappings, generate_translation_rules

english_mappings = load_yaml_mappings("English_mappings.yaml")
chinese_mappings = load_yaml_mappings("Chinese_mappings.yaml")
generate_translation_rules(english_mappings, chinese_mappings, "rules.yaml")
```

### 2. 更新翻译规则

```bash
python main_workflow.py update-rules --existing-rules old_rules.yaml --new-english new_en.yaml --new-chinese new_zh.yaml --output-file updated_rules.yaml
```

### 3. 运行完整工作流

```bash
# 基本用法
python main_workflow.py workflow --english-file English_mappings.yaml --chinese-file Chinese_mappings.yaml --source-dir ./src --output-dir ./output

# 启用并行处理（推荐用于大型项目）
python main_workflow.py workflow --english-file English_mappings.yaml --chinese-file Chinese_mappings.yaml --source-dir ./src --output-dir ./output --parallel

# 启用并行处理并指定最大线程数
python main_workflow.py workflow --english-file English_mappings.yaml --chinese-file Chinese_mappings.yaml --source-dir ./src --output-dir ./output --parallel --max-workers 8

# 禁用缓存机制，强制重新处理所有文件
python main_workflow.py workflow --english-file English_mappings.yaml --chinese-file Chinese_mappings.yaml --source-dir ./src --output-dir ./output --no-cache
```

## 命令行接口

### 1. `generate-rules` - 生成翻译规则

从双语数据生成翻译规则文件。

**参数：**
- `--english-file`: 英文映射文件路径（必填）
- `--chinese-file`: 中文映射文件路径（必填）
- `--output-file`: 输出规则文件路径（必填）
- `--mod-id`: 模组ID（可选）

### 2. `update-rules` - 更新翻译规则

更新现有翻译规则，保留已翻译内容。

**参数：**
- `--existing-rules`: 现有规则文件路径（必填）
- `--new-english`: 新的英文映射文件路径（必填）
- `--new-chinese`: 新的中文映射文件路径（必填）
- `--output-file`: 输出规则文件路径（必填）
- `--mod-id`: 模组ID（可选）

### 3. `workflow` - 完整工作流

运行完整的本地化工作流，包括规则生成/更新、冲突检测和解决、翻译报告生成等。

**参数：**
- `--english-file`: 英文映射文件路径（必填）
- `--chinese-file`: 中文映射文件路径（必填）
- `--source-dir`: 源代码目录路径（默认：./src）
- `--output-dir`: 输出目录路径（默认：./output）
- `--mod-id`: 模组ID（可选）
- `--existing-rules`: 现有规则文件路径（可选）
- `--parallel`: 启用并行处理（默认：禁用）
- `--max-workers`: 最大工作线程数（默认：CPU核心数）
- `--no-cache`: 禁用缓存机制，强制重新处理所有文件（默认：启用缓存）

## Python API

### 1. 生成翻译规则

```python
from src.common.yaml_utils import generate_translation_rules

success = generate_translation_rules(english_mappings, chinese_mappings, output_file, mod_id)
```

### 2. 更新翻译规则

```python
from src.common.yaml_utils import update_translation_rules

success = update_translation_rules(existing_rules_file, new_english_file, new_chinese_file, output_file, mod_id)
```

### 3. 生成翻译报告

```python
from src.common.yaml_utils import generate_translation_report

report = generate_translation_report(rules, report_file, format="markdown")
```

### 4. 冲突检测和解决

```python
from src.common.yaml_utils import RuleConflictDetector

# 检测冲突
conflicts = detector.detect_all_conflicts(mappings)

# 解决冲突
resolved = detector.resolve_conflicts(mappings, conflicts, strategy="latest")
```

## 数据格式

### 1. 英文映射文件格式

```yaml
- id: main_menu.py:10
  original: Start Game
  context: UI/MainMenu
  placeholders: []
- id: main_menu.py:15
  original: Exit Game
  context: UI/MainMenu
  placeholders: []
```

### 2. 中文映射文件格式

```yaml
- id: main_menu.py:10
  original: 开始游戏
  context: UI/MainMenu
  placeholders: []
- id: main_menu.py:15
  original: 退出游戏
  context: UI/MainMenu
  placeholders: []
```

### 3. 生成的规则文件格式

```yaml
# YAML映射规则文件
# 字段说明：
#   version: 版本信息
#   created_at: 创建时间
#   id: 模组唯一标识符，用于直接匹配文件夹
#   mappings: 映射规则列表
# 映射规则字段说明：
#   id: 唯一标识符，格式为 文件路径:行号
#   original: 原始字符串
#   translated: 翻译后的字符串
#   context: 上下文信息，包含父节点类型和节点类型
#   status: 翻译状态，可选值：translated, untranslated, needs_review
#   placeholders: 占位符列表

version: "1.0"
created_at: "2025-12-17T10:00:00"
id: "test_mod"
mappings:
  - id: main_menu.py:10
    original: Start Game
    translated: 开始游戏
    context: UI/MainMenu
    status: translated
    placeholders: []
    created_at: "2025-12-17T10:00:00"
  - id: main_menu.py:15
    original: Exit Game
    translated: 退出游戏
    context: UI/MainMenu
    status: translated
    placeholders: []
    created_at: "2025-12-17T10:00:00"
```

## 工作流程

### 基本工作流

1. **准备双语数据**：收集并整理EN+ZH双语映射文件
2. **生成翻译规则**：使用`generate-rules`命令生成初始规则文件
3. **检测和解决冲突**：自动检测冲突并使用合适的策略解决
4. **更新规则**：使用`update-rules`命令定期更新规则文件
5. **生成翻译报告**：生成报告监控翻译进度
6. **翻译回写**：将翻译应用到源代码文件

### 完整工作流示例

```bash
# 1. 生成初始规则
python main_workflow.py generate-rules --english-file English_mappings.yaml --chinese-file Chinese_mappings.yaml --output-file rules.yaml

# 2. 更新规则（当有新的翻译时）
python main_workflow.py update-rules --existing-rules rules.yaml --new-english new_en.yaml --new-chinese new_zh.yaml --output-file rules.yaml

# 3. 运行完整工作流
python main_workflow.py workflow --english-file English_mappings.yaml --chinese-file Chinese_mappings.yaml --source-dir ./src --output-dir ./output
```

## 测试

### 运行单元测试

```bash
# 使用unittest运行测试
python test/test_yaml_utils.py

# 或使用pytest（如果安装了pytest）
python -m pytest test/test_yaml_utils.py -v
```

### 测试覆盖范围

- 数据加载和保存
- 翻译规则生成和更新
- 冲突检测和解决
- 翻译报告生成
- 数据对齐和验证

## 目录结构

```
Localization_Tool/
├── src/
│   ├── common/           # 通用工具模块
│   │   ├── file_utils.py          # 文件处理工具
│   │   ├── tree_sitter_utils.py   # Tree-sitter AST处理
│   │   ├── yaml_utils.py          # YAML映射处理
│   │   ├── __init__.py           # 模块导出
│   │   └── ...
│   ├── extend_mode/       # 扩展模式模块
│   ├── extract_mode/      # 提取模式模块
│   ├── init_mode/         # 初始化模式模块
│   └── decompile_mode/    # 反编译模式模块
├── test/                 # 测试目录
│   └── test_yaml_utils.py # 单元测试
├── main_workflow.py       # 主工作流脚本
├── requirements.txt       # 依赖列表
└── README.md             # 项目文档
```

## 常见问题

### 1. 数据对齐失败

**问题**：英文和中文映射条目数不一致

**解决方案**：
- 检查数据源，确保英文和中文条目一一对应
- 工具会自动处理不一致情况，只处理前N条数据（N为较小的数量）

### 2. 冲突检测到重复ID

**解决方案**：
- 使用`latest`策略保留最新的映射
- 或使用`manual`策略手动解决冲突
- 检查数据源，修复重复ID问题

### 3. 翻译报告生成失败

**解决方案**：
- 检查规则文件格式是否正确
- 确保规则文件包含必要的字段
- 尝试使用JSON格式报告，查看详细错误信息

## 贡献指南

### 开发环境设置

1. 克隆仓库
2. 创建虚拟环境并安装依赖
3. 运行测试，确保所有测试通过
4. 编写代码，遵循PEP 8规范
5. 添加单元测试，确保测试覆盖新功能
6. 提交代码，创建Pull Request

### 代码规范

- 遵循PEP 8代码风格
- 每个函数添加docstring
- 关键步骤添加注释
- 使用类型注解

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过以下方式联系：

- 项目仓库：https://github.com/your-username/Localization_Tool
- 邮箱：your-email@example.com

## 更新日志

### v1.0.0 (2025-12-17)
- 初始版本发布
- 支持双语数据处理
- 翻译规则生成和更新
- 冲突检测和解决
- 翻译报告生成
- 完整的命令行接口

## 未来规划

1. 支持更多语言对
2. 集成机器翻译API
3. 可视化界面
4. 支持更多文件格式
5. 增强翻译质量评估
6. 支持团队协作

---

**本地化工具** - 让翻译工作更高效、更准确！