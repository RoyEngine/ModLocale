# common 模块

## 功能描述
通用工具模块，为本地化工具提供各种基础功能支持，包括文件操作、JAR处理、AST解析、YAML处理、配置管理等。

## 主要文件及其用途

| 文件名 | 用途 |
|--------|------|
| `__init__.py` | 模块初始化文件，导出所有工具函数 |
| `config_utils.py` | 配置管理工具，用于加载和管理配置文件 |
| `file_utils.py` | 文件操作工具，包括文件夹创建、文件复制、移动等 |
| `flow_executor.py` | 流程执行器，用于管理和执行本地化工具的工作流程 |
| `jar_utils.py` | JAR文件处理工具，包括JAR文件检测、反编译等 |
| `levenshtein_utils.py` | 编辑距离计算工具，用于字符串相似度比较 |
| `localization_tool.py` | 本地化工具核心类，提供主要的本地化功能 |
| `logger_utils.py` | 日志记录工具，用于设置和获取日志记录器 |
| `mod_info_utils.py` | 模组信息处理工具，用于加载和管理模组信息 |
| `report_utils.py` | 报告生成工具，用于生成和保存处理报告 |
| `suggestion_generator.py` | 建议生成工具，用于生成字符串映射建议 |
| `timestamp_utils.py` | 时间戳工具，用于生成和格式化时间戳 |
| `tools_integrator.py` | 工具集成工具，用于集成外部工具 |
| `tree_sitter_utils.py` | Tree-sitter AST解析工具，用于从源代码中提取字符串和映射 |
| `yaml_utils.py` | YAML文件处理工具，用于加载、保存和验证映射规则 |

## 关键实现逻辑

### 模块化设计
采用模块化设计，每个工具类或函数独立封装，便于维护和扩展。所有工具函数通过`__init__.py`统一导出，供其他模块调用。

### Tree-sitter AST解析
使用Tree-sitter库进行AST解析，支持Java和Kotlin等语言，能够准确提取源代码中的字符串和映射关系。

### YAML映射规则
实现了YAML映射规则的加载、保存和验证功能，支持从源代码自动生成初始映射规则，并根据现有映射规则更新源代码。

### 配置管理
提供了配置文件的加载和管理功能，支持从不同位置加载配置，并验证配置的完整性和正确性。

### 日志记录
集成了日志记录功能，支持不同级别日志的输出和保存，便于调试和监控。

## 使用示例

### 加载YAML映射规则
```python
from src.common.yaml_utils import load_yaml_mappings

# 加载映射规则
mappings = load_yaml_mappings("path/to/mappings.yml")
print(mappings)
```

### 从文件中提取字符串
```python
from src.common.tree_sitter_utils import extract_strings_from_file

# 初始化语言解析器
initialize_languages()

# 从Java文件中提取字符串
strings = extract_strings_from_file("path/to/File.java", "java")
print(strings)
```

### 生成报告
```python
from src.common.report_utils import generate_report, save_report

# 生成报告
report = generate_report("process_id")

# 保存报告
save_report(report, "path/to/report.json")
```

## 依赖关系

- 外部依赖：tree-sitter库用于AST解析
- 被其他模块(extend_mode、extract_mode、init_mode、decompile_mode)依赖

## 开发和维护注意事项

1. **模块化设计**：保持模块化设计，每个工具函数专注于单一功能
2. **类型注解**：严格遵循PEP 8规范，添加类型注解
3. **测试覆盖**：确保所有工具函数都有对应的单元测试
4. **避免循环依赖**：注意模块间的依赖关系，避免循环依赖
5. **文档更新**：添加或修改功能时，及时更新对应的文档
6. **兼容性**：确保代码在不同操作系统下正常运行

## 测试

模块包含完整的单元测试，位于项目根目录的`test/`目录下，使用pytest进行测试。

### 运行测试
```bash
pytest test/
```
