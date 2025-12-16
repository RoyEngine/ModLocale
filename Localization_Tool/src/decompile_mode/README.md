# decompile_mode 模块

## 功能描述
反编译模式核心模块，提供完整的JAR文件反编译和提取API，支持单个JAR文件和目录中所有JAR文件的处理。

## 主要文件及其用途

| 文件名 | 用途 |
|--------|------|
| `__init__.py` | 模块初始化文件 |
| `core.py` | 反编译模式核心流程控制，包含run_decompile_sub_flow函数及相关API |

## 关键实现逻辑

### 五种子流程设计

1. **反编译单个JAR文件流程**：
   - 适用于单个JAR文件的反编译
   - 流程：加载JAR文件 → 执行反编译 → 保存反编译结果

2. **反编译目录中所有JAR文件流程**：
   - 适用于目录中所有JAR文件的批量反编译
   - 流程：扫描目录 → 加载所有JAR文件 → 执行批量反编译 → 保存反编译结果

3. **提取单个JAR文件内容流程**：
   - 适用于单个JAR文件的内容提取
   - 流程：加载JAR文件 → 提取文件内容 → 保存提取结果

4. **提取目录中所有JAR文件内容流程**：
   - 适用于目录中所有JAR文件的批量内容提取
   - 流程：扫描目录 → 加载所有JAR文件 → 执行批量内容提取 → 保存提取结果

### 核心API

`run_decompile_sub_flow`函数是反编译模式的核心入口，根据指定的子流程类型执行相应的流程，包括：
- 初始化流程
- 执行子流程
- 生成报告
- 保存结果

### 辅助API

- `decompile_single_jar`：反编译单个JAR文件
- `decompile_all_jars`：反编译目录中所有JAR文件
- `extract_single_jar`：提取单个JAR文件内容
- `extract_all_jars`：提取目录中所有JAR文件内容

### JAR处理技术

使用外部JAR反编译工具（如CFR、Procyon）进行JAR文件反编译，支持：
- 检测Java环境
- 检测反编译工具
- 批量处理多个JAR文件
- 提取JAR文件内容

## 使用示例

### 执行反编译模式子流程

```python
from src.decompile_mode.core import run_decompile_sub_flow

# 执行反编译单个JAR文件流程
result = run_decompile_sub_flow(
    sub_flow="反编译单个JAR文件",
    base_path="path/to/File.jar"
)

# 执行反编译目录中所有JAR文件流程
result = run_decompile_sub_flow(
    sub_flow="反编译目录中所有JAR文件",
    base_path="path/to/jars_directory"
)

# 执行提取单个JAR文件内容流程
result = run_decompile_sub_flow(
    sub_flow="提取单个JAR文件内容",
    base_path="path/to/File.jar"
)

# 执行提取目录中所有JAR文件内容流程
result = run_decompile_sub_flow(
    sub_flow="提取目录中所有JAR文件内容",
    base_path="path/to/jars_directory"
)
```

### 从命令行执行

```bash
python src/main.py decompile
```

## 依赖关系

- 依赖`src.common`模块，使用其提供的各种工具函数
- 依赖外部JAR反编译工具（CFR、Procyon）

## 开发和维护注意事项

1. **工具集成**：确保反编译工具的正确集成和路径配置
2. **错误处理**：添加完善的错误处理和日志记录，便于调试和监控
3. **性能优化**：优化批量处理算法，提高处理大量JAR文件的性能
4. **测试覆盖**：确保每个子流程都有对应的单元测试
5. **兼容性**：确保代码在不同操作系统下正常运行
6. **文档更新**：添加或修改子流程时，及时更新文档

## 测试

模块包含完整的单元测试，位于项目根目录的`test/`目录下，使用pytest进行测试。

### 运行测试

```bash
pytest test/
```