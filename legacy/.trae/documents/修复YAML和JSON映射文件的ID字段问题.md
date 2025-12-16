# 修复init_mode模块的mod_id生成逻辑

## 问题分析
1. 当前实现中，当mod_info.json缺少id字段时，会直接跳过该mod，导致一些有效mod被忽略
2. 这会影响后续的文件夹匹配和映射功能
3. 需要优化mod_id生成逻辑，确保每个mod都能获得唯一的标识

## 修复方案
1. 修改build_mod_mappings函数中的mod_id生成逻辑
2. 当mod_info.json缺少id字段时，使用文件夹名称作为mod_id
3. 更新mod_info对象的mod_id属性
4. 重新验证mod_info对象的有效性

## 具体修改
修改build_mod_mappings函数，在第521-529行添加以下逻辑：
- 当mod_id为空时，使用文件夹名称作为mod_id
- 更新mod_info对象的mod_id属性
- 重新验证mod_info对象

## 预期效果
1. 每个mod都会获得唯一的mod_id
2. 即使mod_info.json缺少id字段，也能正确处理
3. 提高了模块的鲁棒性和容错能力
4. 确保后续的文件夹匹配和映射功能正常工作

## 验证方案
1. 运行init_mode，构建mod映射关系
2. 检查日志，确认没有因为缺少id字段而跳过的mod
3. 检查mod_mappings全局变量，确认所有mod都有对应的映射
4. 运行Extend模式，验证文件夹匹配功能正常工作