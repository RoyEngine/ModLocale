# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v1.0.0] - 2025-12-17

### Added

- **缓存机制**：实现了文件缓存管理，支持增量更新，只处理已变更文件
- **并行处理**：添加了多线程并行文件处理，加速字符串提取和翻译回写
- **内存优化**：使用生成器替代列表，减少内存占用，支持处理大型项目
- **完整的命令行接口**：提供了generate-rules、update-rules、workflow三个命令
- **安装和使用文档**：编写了详细的installation.md和usage.md文档
- **CLI工具打包**：使用PyInstaller打包为单个可执行文件，方便用户直接运行
- **全面的测试套件**：增强了测试用例，覆盖更多场景和语言

### Changed

- **更新README.md**：详细介绍了工具功能、使用方法和性能优化
- **优化extract_ast_mappings函数**：改为使用生成器，支持缓存机制
- **改进冲突检测算法**：增强了冲突检测和解决功能
- **修复了多个bug**：
  - 修复了import errors in test scripts
  - 修复了command execution directory errors
  - 修复了syntax error in test_string_extract.py
  - 修复了unescaped backslash in pyproject.toml

### Fixed

- 修复了测试脚本中的导入错误
- 修复了命令执行目录错误
- 修复了test_string_extract.py中的语法错误
- 修复了pyproject.toml中的未转义反斜杠问题
- 修复了conflict_resolution函数中的索引错误

### Removed

- 移除了过时的测试文件

## [Unreleased]

### Added

- 支持更多文件格式
- 集成机器翻译API
- 可视化界面
- 支持团队协作

### Changed

### Fixed

### Removed

## [v0.1.0] - 2025-12-01

### Added

- 初始版本发布
- 支持双语数据加载和对齐
- 翻译规则生成和更新
- 冲突检测和解决
- 翻译报告生成
- 翻译回写功能

### Changed

### Fixed

### Removed

