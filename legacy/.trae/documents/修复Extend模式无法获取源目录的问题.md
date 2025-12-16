# 修复Extend模式无法获取源目录的问题

## 问题分析
从终端输出和代码分析来看，Extend模式执行失败，错误信息为"无法获取源目录，模式: extend"。

### 根因
- `get_source_directory`函数依赖于`mapping_config`中的`source_mappings`配置
- 如果`source_mappings`配置不存在或为空，函数返回`None`
- 实际上，我们有更可靠的方式获取源目录：直接从`directories`配置中获取

## 修复方案
修改extend_mode中的代码，不使用`get_source_directory`函数，而是直接使用`get_directory("source")`来获取源目录。

### 需要修改的文件
- `src/extend_mode/core.py`：将所有`get_source_directory`调用替换为`get_directory("source")`

### 具体修改点
1. 在`_process_existing_chinese_src`函数中
2. 在`_process_no_chinese_src`函数中
3. 在`_process_existing_english_src`函数中
4. 在`_process_no_english_src`函数中
5. 在`_process_existing_chinese_rules`函数中
6. 在`_process_existing_english_rules`函数中

## 修复后效果
- Extend模式能够成功获取源目录
- 映射流程能够正常执行
- 不再依赖`mapping_config`中的`source_mappings`配置

## 验证方案
1. 运行Extend模式，选择"中文映射到英文"流程
2. 确认流程能够成功获取源目录
3. 确认映射流程能够正常完成
4. 检查输出结果是否正确