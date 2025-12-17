# extend_mode 模块

## 1. 模块概述

extend_mode模块是ModLocale工具的核心功能模块，负责使用映射规则将一种语言映射到另一种语言。该模块支持中英文双向映射，提供完整的工作流管理和规则管理功能。

## 2. 模块结构

```
extend_mode/
├── __init__.py           # 模块入口，统一导出所有功能
├── core.py               # 核心映射功能，负责执行映射流程
├── rules/                # 规则管理子模块
│   ├── __init__.py       # 规则子模块入口
│   ├── extractor.py       # 规则提取功能
│   ├── processor.py      # 未映射内容处理
│   └── conflict.py       # 冲突检测和解决
├── workflow/             # 工作流管理子模块
│   ├── __init__.py       # 工作流子模块入口
│   ├── generator.py      # 规则生成功能
│   ├── updater.py        # 规则更新功能
│   └── runner.py         # 完整工作流执行
└── README.md             # 模块文档
```

## 3. 功能说明

### 3.1 核心映射功能

**文件**：`core.py`

**主要功能**：
- 执行不同类型的映射子流程
- 处理mod映射关系
- 生成映射报告
- 执行单个mod的映射

**核心函数**：
- `run_extend_sub_flow(sub_flow, base_path=None)`: 执行Extend指定子流程

### 3.2 规则管理功能

**文件**：`rules/` 子模块

**主要功能**：
- 从源代码或已处理文件夹提取映射规则
- 处理未映射内容（生成报告、列出、标记为已翻译）
- 检测和解决规则冲突

**核心函数**：
- `extract_mapping_rules()`: 提取映射规则
- `process_unmapped_content()`: 处理未映射内容
- `detect_and_resolve_conflicts()`: 检测和解决规则冲突

### 3.3 工作流管理功能

**文件**：`workflow/` 子模块

**主要功能**：
- 从双语数据生成翻译规则
- 更新现有翻译规则
- 执行完整的翻译工作流

**核心函数**：
- `generate_translation_rules()`: 生成翻译规则
- `update_translation_rules()`: 更新翻译规则
- `run_complete_workflow()`: 执行完整工作流

## 4. 使用方法

### 4.1 基本导入

```python
# 导入extend_mode模块
from src.extend_mode import *

# 或导入特定功能
from src.extend_mode import run_extend_sub_flow, extract_mapping_rules
```

### 4.2 执行映射流程

```python
# 执行映射流程
result = run_extend_sub_flow(
    sub_flow="已有中文src文件夹映射流程"
)
print(f"映射结果: {result}")
```

### 4.3 提取映射规则

```python
# 提取映射规则
result = extract_mapping_rules(
    source_dir="/path/to/source",
    output_file="/path/to/output/rules.yaml"
)
print(f"规则提取结果: {result}")
```

### 4.4 处理未映射内容

```python
# 列出未映射内容
result = process_unmapped_content(
    rule_file="/path/to/rules.yaml",
    list_unmapped=True
)
print(f"未映射内容处理结果: {result}")
```

### 4.5 检测和解决冲突

```python
# 检测冲突
result = detect_and_resolve_conflicts(
    rule_file="/path/to/rules.yaml"
)
print(f"冲突检测结果: {result}")
```

### 4.6 生成翻译规则

```python
# 生成翻译规则
result = generate_translation_rules(
    english_file="/path/to/english.yaml",
    chinese_file="/path/to/chinese.yaml",
    output_file="/path/to/rules.yaml"
)
print(f"规则生成结果: {result}")
```

### 4.7 执行完整工作流

```python
# 执行完整工作流
result = run_complete_workflow(
    english_file="/path/to/english.yaml",
    chinese_file="/path/to/chinese.yaml",
    source_dir="/path/to/source",
    output_dir="/path/to/output"
)
print(f"工作流执行结果: {result}")
```

## 5. 子流程类型

`run_extend_sub_flow()` 支持以下子流程：

1. `"已有中文src文件夹映射流程"`
2. `"没有中文src文件夹映射流程"`
3. `"已有中文映射规则文件流程"`
4. `"已有英文src文件夹映射流程"`
5. `"没有英文src文件夹映射流程"`
6. `"已有英文映射规则文件流程"`

## 6. 配置说明

该模块不直接读取配置文件，而是通过函数参数接收配置信息。主要配置参数包括：

- `source_dir`: 源代码目录路径
- `output_dir`: 输出目录路径
- `rule_file`: 映射规则文件路径
- `language`: 语言类型（"Chinese"或"English"）
- `mark_unmapped`: 是否将未映射内容标记为"unmapped"状态
- `parallel`: 是否启用并行处理
- `use_cache`: 是否使用缓存机制

## 7. 依赖关系

- `src.common.yaml_utils`: YAML映射管理
- `src.common.tree_sitter_utils`: AST解析和字符串提取
- `src.common.file_utils`: 文件操作工具
- `src.common.report_utils`: 报告生成工具

## 8. 测试

模块包含完整的单元测试，位于 `tests/extend_mode/` 目录下。使用pytest运行测试：

```bash
python -m pytest tests/extend_mode/ -v
```

## 9. 版本历史

- v1.0.0: 初始版本，实现了基本的映射功能
- v1.1.0: 增加了规则管理功能
- v1.2.0: 增加了工作流管理功能
- v2.0.0: 重构模块结构，拆分功能为子模块

## 10. 贡献指南

欢迎提交Issue和Pull Request来改进extend_mode模块。

## 11. 许可证

该模块使用与主项目相同的许可证。