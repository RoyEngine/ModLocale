# 修复extract_mode输出问题

## 问题分析

从终端输出可以看到两个主要问题：

1. **输出文件夹命名错误**：
   - 输出文件夹被命名为 `English`，而不是源mod文件夹的名称 `Quality Captains 1.7.0`
   - 这导致输出文件被错误地保存到了错误的位置

2. **save_report 缺少参数**：
   - 错误信息：`save_report() missing 1 required positional argument: 'timestamp'`
   - `save_report` 函数需要多个参数，但调用时只传递了两个

## 修复计划

### 步骤1：修复输出文件夹命名错误

1. **问题根源**：
   - 在 `_extract_strings_from_source` 函数中，`mod_folder` 被错误地设置为 `os.path.dirname(source_path)`
   - 而 `source_path` 已经是包含src文件夹的模组文件夹路径
   - 这导致 `mod_name` 被设置为模组文件夹的父目录名称（即 `English`）

2. **修复方案**：
   - 修改 `_extract_strings_from_source` 函数，直接使用 `source_path` 作为 `mod_folder`
   - 确保 `mod_name` 是源mod文件夹的名称

### 步骤2：修复save_report缺少参数问题

1. **问题根源**：
   - `save_report` 函数需要 `report_path`、`timestamp` 等参数
   - 但在 `run_extract_sub_flow` 函数中，只传递了 `result` 和 `"Extract"` 两个参数

2. **修复方案**：
   - 修改 `run_extract_sub_flow` 函数，正确调用 `save_report` 函数
   - 传递所有必需的参数，包括 `report_path`、`timestamp` 等

### 步骤3：验证修复效果

1. **运行测试脚本**：
   - 执行extract流程，验证输出文件夹名是否与源mod文件夹名一致
   - 验证save_report函数是否能正确执行

2. **手动验证**：
   - 检查输出目录结构，确保输出文件夹名与源mod文件夹名完全匹配
   - 检查报告是否正确保存

## 预期效果

1. **输出文件夹命名正确**：
   - 源mod文件夹为 `Quality Captains 1.7.0`，输出文件夹也为 `Quality Captains 1.7.0`
   - 输出文件正确保存到对应位置

2. **save_report函数正常执行**：
   - 不再出现缺少参数的错误
   - 报告正确保存到指定位置

3. **整体效果**：
   - extract流程能够正常完成
   - 输出文件和报告正确保存
   - 系统稳定性提高

## 修复细节

### 1. 修改 `_extract_strings_from_source` 函数

- 将 `mod_folder = os.path.dirname(source_path)` 改为 `mod_folder = source_path`
- 确保 `mod_name` 是源mod文件夹的名称

### 2. 修改 `run_extract_sub_flow` 函数

- 正确调用 `save_report` 函数，传递所有必需的参数
- 确保报告路径正确
- 确保时间戳正确传递

## 注意事项

1. **保持向后兼容**：
   - 修复后，现有功能应继续正常工作
   - 不破坏现有的文件结构和工作流程

2. **遵循项目规范**：
   - 确保代码符合PEP 8规范
   - 保持良好的代码风格和文档

3. **测试覆盖**：
   - 确保修复后的功能经过充分测试
   - 验证各种场景下的正确性

通过以上修复，确保extract_mode能够正常输出结果，输出文件夹名称与源mod文件夹名称一致，报告正确保存。