# 使用指南

## 1. 工具概述

本地化工具是一个用于处理游戏模组和应用程序翻译工作流的强大工具，支持从双语数据生成翻译规则、自动冲突检测和解决、翻译回写以及翻译报告生成。

## 2. 核心概念

### 2.1 翻译规则

翻译规则是连接原始字符串和翻译后字符串的映射关系，存储在YAML文件中。规则文件包含以下信息：
- 唯一标识符（ID）
- 原始字符串
- 翻译后的字符串
- 翻译状态
- 上下文信息
- 元数据

### 2.2 工作流程

工具的典型工作流程包括：
1. 从源代码提取英文字符串
2. 加载中文翻译数据
3. 生成翻译规则
4. 检测和解决冲突
5. 更新翻译规则
6. 生成翻译报告
7. 将翻译应用到源代码

## 3. 命令行接口

工具提供了命令行接口，支持以下命令：

### 3.1 `generate-rules` - 生成翻译规则

从双语数据生成翻译规则文件。

**语法：**
```bash
python main_workflow.py generate-rules --english-file <英文映射文件> --chinese-file <中文映射文件> --output-file <输出规则文件> [--mod-id <模组ID>]
```

**参数：**
- `--english-file`: 英文映射文件路径（必填）
- `--chinese-file`: 中文映射文件路径（必填）
- `--output-file`: 输出规则文件路径（必填）
- `--mod-id`: 模组ID（可选）

**示例：**
```bash
python main_workflow.py generate-rules --english-file English_mappings.yaml --chinese-file Chinese_mappings.yaml --output-file rules.yaml
```

### 3.2 `update-rules` - 更新翻译规则

更新现有翻译规则，保留已翻译内容。

**语法：**
```bash
python main_workflow.py update-rules --existing-rules <现有规则文件> --new-english <新英文映射文件> --new-chinese <新中文映射文件> --output-file <输出规则文件> [--mod-id <模组ID>]
```

**参数：**
- `--existing-rules`: 现有规则文件路径（必填）
- `--new-english`: 新的英文映射文件路径（必填）
- `--new-chinese`: 新的中文映射文件路径（必填）
- `--output-file`: 输出规则文件路径（必填）
- `--mod-id`: 模组ID（可选）

**示例：**
```bash
python main_workflow.py update-rules --existing-rules old_rules.yaml --new-english new_en.yaml --new-chinese new_zh.yaml --output-file updated_rules.yaml
```

### 3.3 `workflow` - 完整工作流

运行完整的本地化工作流，包括规则生成/更新、冲突检测和解决、翻译报告生成等。

**语法：**
```bash
python main_workflow.py workflow --english-file <英文映射文件> --chinese-file <中文映射文件> --source-dir <源代码目录> --output-dir <输出目录> [--mod-id <模组ID>] [--existing-rules <现有规则文件>] [--parallel] [--max-workers <最大线程数>] [--no-cache]
```

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

**示例：**
```bash
# 基本用法
python main_workflow.py workflow --english-file English_mappings.yaml --chinese-file Chinese_mappings.yaml --source-dir ./src --output-dir ./output

# 启用并行处理
python main_workflow.py workflow --english-file English_mappings.yaml --chinese-file Chinese_mappings.yaml --source-dir ./src --output-dir ./output --parallel

# 禁用缓存
python main_workflow.py workflow --english-file English_mappings.yaml --chinese-file Chinese_mappings.yaml --source-dir ./src --output-dir ./output --no-cache
```

## 4. 完整工作流示例

以下是一个完整的本地化工作流示例：

### 4.1 准备工作

1. 确保已安装工具和依赖
2. 准备好英文映射文件和中文映射文件
3. 准备好源代码目录

### 4.2 执行工作流

```bash
# 1. 生成初始翻译规则
python main_workflow.py generate-rules --english-file English_mappings.yaml --chinese-file Chinese_mappings.yaml --output-file rules.yaml

# 2. 检测规则冲突
# （generate-rules命令会自动检测冲突）

# 3. 查看生成的规则文件
cat rules.yaml

# 4. 更新规则（当有新的翻译时）
python main_workflow.py update-rules --existing-rules rules.yaml --new-english new_en.yaml --new-chinese new_zh.yaml --output-file rules.yaml

# 5. 运行完整工作流
python main_workflow.py workflow --english-file English_mappings.yaml --chinese-file Chinese_mappings.yaml --source-dir ./src --output-dir ./output --parallel

# 6. 查看生成的报告
cat output/translation_report.md
```

## 5. 数据格式

### 5.1 英文映射文件格式

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

### 5.2 中文映射文件格式

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

### 5.3 生成的规则文件格式

```yaml
version: "1.0"
created_at: "2025-12-17T10:00:00"
id: "test_mod"
mappings:
  - id: main_menu.py:10
    original: Start Game
    translated: 开始游戏
    status: translated
    context: UI/MainMenu
    placeholders: []
    created_at: "2025-12-17T10:00:00"
  - id: main_menu.py:15
    original: Exit Game
    translated: 退出游戏
    status: translated
    context: UI/MainMenu
    placeholders: []
    created_at: "2025-12-17T10:00:00"
```

## 6. 性能优化建议

### 6.1 使用并行处理

对于大型项目，启用并行处理可以显著提高处理速度：

```bash
python main_workflow.py workflow --english-file English_mappings.yaml --chinese-file Chinese_mappings.yaml --source-dir ./src --output-dir ./output --parallel
```

### 6.2 合理使用缓存

默认情况下，工具会启用缓存机制，只处理已变更的文件。如果需要强制重新处理所有文件，可以使用`--no-cache`参数：

```bash
python main_workflow.py workflow --english-file English_mappings.yaml --chinese-file Chinese_mappings.yaml --source-dir ./src --output-dir ./output --no-cache
```

### 6.3 调整线程数

根据系统的CPU核心数调整线程数，可以获得最佳性能：

```bash
# 使用8个线程
python main_workflow.py workflow --english-file English_mappings.yaml --chinese-file Chinese_mappings.yaml --source-dir ./src --output-dir ./output --parallel --max-workers 8
```

## 7. 常见问题和解决方案

### 7.1 数据对齐失败

**问题**：英文和中文映射条目数不一致

**解决方案**：
- 检查数据源，确保英文和中文条目一一对应
- 工具会自动处理不一致情况，只处理前N条数据（N为较小的数量）

### 7.2 冲突检测到重复ID

**解决方案**：
- 使用`latest`策略保留最新的映射
- 或使用`manual`策略手动解决冲突
- 检查数据源，修复重复ID问题

### 7.3 翻译报告生成失败

**解决方案**：
- 检查规则文件格式是否正确
- 确保规则文件包含必要的字段
- 尝试使用JSON格式报告，查看详细错误信息

### 7.4 缓存导致的问题

**问题**：工具没有检测到文件变更

**解决方案**：
- 使用`--no-cache`参数强制重新处理所有文件
- 删除缓存目录（默认：`.cache/`）并重新运行工具

## 8. 高级用法

### 8.1 自定义缓存目录

可以在代码中修改缓存目录：

```python
from src.common.cache_utils import FileCacheManager

# 使用自定义缓存目录
cache_manager = FileCacheManager(cache_dir=".custom_cache")
```

### 8.2 集成到其他脚本

可以将工具集成到其他脚本中：

```python
from src.common.yaml_utils import load_yaml_mappings, generate_translation_rules
from src.common.tree_sitter_utils import extract_ast_mappings

# 加载映射数据
english_mappings = load_yaml_mappings("English_mappings.yaml")
chinese_mappings = load_yaml_mappings("Chinese_mappings.yaml")

# 生成翻译规则
generate_translation_rules(english_mappings, chinese_mappings, "rules.yaml")

# 提取AST映射
ast_mappings = list(extract_ast_mappings("./src", use_parallel=True, use_cache=True))
```

## 9. 下一步

- 阅读[API文档](api.md)了解更多高级用法
- 查看[开发指南](development.md)了解如何为工具贡献代码
- 查看[常见问题](faq.md)了解更多问题和解决方案
