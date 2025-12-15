# extract_mode 模块

## 功能描述
提取模式核心模块，用于从源代码中提取字符串，支持多种语言和文件类型，生成可用于本地化的字符串映射文件。

## 主要文件及其用途

| 文件名 | 用途 |
|--------|------|
| `__init__.py` | 模块初始化文件 |
| `core.py` | 提取模式核心流程控制，包含run_extract_sub_flow函数 |
| `extractor.py` | 字符串提取器，用于从源代码中提取字符串 |
| `string_extractor.py` | 字符串提取工具，用于处理不同类型的源代码 |

## 关键实现逻辑

### 四种子流程设计

1. **中文src文件夹字符串提取流程**：
   - 适用于中文src文件夹的字符串提取
   - 流程：加载中文src文件夹 → 提取字符串 → 生成中文映射文件

2. **英文src文件夹字符串提取流程**：
   - 适用于英文src文件夹的字符串提取
   - 流程：加载英文src文件夹 → 提取字符串 → 生成英文映射文件

3. **中文jar文件字符串提取流程**：
   - 适用于中文jar文件的字符串提取
   - 流程：加载中文jar文件 → 反编译jar → 提取字符串 → 生成中文映射文件

4. **英文jar文件字符串提取流程**：
   - 适用于英文jar文件的字符串提取
   - 流程：加载英文jar文件 → 反编译jar → 提取字符串 → 生成英文映射文件

### 核心流程控制

`run_extract_sub_flow`函数是提取模式的核心入口，根据指定的子流程类型执行相应的流程，包括：
- 初始化流程
- 执行子流程
- 生成报告
- 保存结果

### 字符串提取技术

使用Tree-sitter AST解析技术，支持从Java和Kotlin等语言的源代码中提取字符串，包括：
- 普通字符串常量
- 格式化字符串
- 注释中的字符串
- 资源文件中的字符串

## 使用示例

### 执行提取模式子流程

```python
from src.extract_mode.core import run_extract_sub_flow

# 执行中文src文件夹字符串提取流程
result = run_extract_sub_flow(
    sub_flow="中文src文件夹字符串提取流程",
    base_path="path/to/project"
)

# 执行英文src文件夹字符串提取流程
result = run_extract_sub_flow(
    sub_flow="英文src文件夹字符串提取流程",
    base_path="path/to/project"
)

# 执行中文jar文件字符串提取流程
result = run_extract_sub_flow(
    sub_flow="中文jar文件字符串提取流程",
    base_path="path/to/project"
)

# 执行英文jar文件字符串提取流程
result = run_extract_sub_flow(
    sub_flow="英文jar文件字符串提取流程",
    base_path="path/to/project"
)
```

### 从命令行执行

```bash
python src/main.py extract
```

## 依赖关系

- 依赖`src.common`模块，使用其提供的各种工具函数
- 依赖Tree-sitter库，用于AST解析

## 开发和维护注意事项

1. **扩展语言支持**：如需支持新的语言，需添加对应的Tree-sitter解析器和提取逻辑
2. **优化提取算法**：不断优化字符串提取算法，提高准确性和性能
3. **错误处理**：添加完善的错误处理和日志记录，便于调试和监控
4. **测试覆盖**：确保每个子流程都有对应的单元测试
5. **兼容性**：确保代码在不同操作系统下正常运行
6. **文档更新**：添加或修改子流程时，及时更新文档

## 测试

模块包含完整的单元测试，位于`tests/`目录下，使用pytest进行测试。

### 运行测试

```bash
pytest src/extract_mode/tests/
```
