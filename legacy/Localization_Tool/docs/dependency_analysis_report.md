# 依赖分析报告

## 1. 项目概述

该项目是一个本地化工具，用于提取和管理游戏模组的本地化字符串。本报告分析了项目的依赖使用情况，识别了未被使用的冗余依赖。

## 2. 分析方法

- **依赖收集**：获取所有已安装的Python包及其版本信息
- **代码扫描**：扫描项目源代码，识别所有导入的包
- **依赖关系分析**：分析包之间的依赖关系
- **使用情况检测**：检查每个包是否被项目代码直接使用或作为其他已使用包的依赖

## 3. 分析结果

### 3.1 依赖概览

| 类别 | 数量 |
|------|------|
| 已安装的包总数 | 93 |
| 项目声明的核心依赖 | 6 |
| 项目声明的开发依赖 | 34 |
| 代码中直接使用的外部依赖 | 5 |
| 未使用的核心依赖 | 1 |
| 未声明但已安装的依赖 | 53 |

### 3.2 核心依赖使用情况

| 包名 | 版本 | 使用状态 | 用途 |
|------|------|----------|------|
| colorama | 0.4.6 | 未使用 | 终端颜色输出（未在代码中直接使用） |
| requests | 2.32.0 | 已使用 | 网络请求（在jar_utils.py中用于下载文件） |
| PyYAML | 6.0.3 | 已使用 | YAML文件处理（在yaml_utils.py中使用） |
| tree-sitter | 0.25.2 | 已使用 | AST解析（在tree_sitter_utils.py中使用） |
| tree-sitter-java | 0.23.5 | 已使用 | Java语言支持（在tree_sitter_utils.py中使用） |
| tree-sitter-kotlin | 1.1.0 | 已使用 | Kotlin语言支持（在tree_sitter_utils.py中使用） |

### 3.3 开发依赖使用情况

开发依赖主要用于测试、代码检查、格式化和文档生成，这些依赖在开发过程中是必要的，但在生产环境中可能不需要。

### 3.4 未声明但已安装的依赖

以下是已安装但未在任何requirements文件中声明的依赖：

| 包名 | 版本 | 备注 |
|------|------|------|
| alabaster | 0.7.16 | Sphinx主题 |
| astroid | 3.3.11 | pylint依赖 |
| asttokens | 3.0.1 | ipython依赖 |
| attrs | 25.4.0 | pytest依赖 |
| babel | 2.17.0 | Sphinx依赖 |
| build | 1.3.0 | 构建工具 |
| cachetools | 6.2.4 | 缓存工具 |
| cfgv | 3.5.0 | pre-commit依赖 |
| chardet | 5.2.0 | 字符编码检测 |
| charset-normalizer | 3.4.4 | requests依赖 |
| decorator | 5.2.1 | ipython依赖 |
| dill | 0.4.0 | 序列化工具 |
| distlib | 0.4.0 | virtualenv依赖 |
| docutils | 0.20.1 | Sphinx依赖 |
| executing | 2.2.1 | ipython依赖 |
| filelock | 3.20.1 | virtualenv依赖 |
| identify | 2.6.15 | pre-commit依赖 |
| idna | 3.11 | requests依赖 |
| imagesize | 1.4.1 | Sphinx依赖 |
| ipdb | 0.13.13 | 调试工具 |
| ipython_pygments_lexers | 1.1.0 | ipython依赖 |
| jedi | 0.19.2 | ipython依赖 |
| Jinja2 | 3.1.6 | Sphinx依赖 |
| markdown-it-py | 4.0.0 | rich依赖 |
| MarkupSafe | 3.0.3 | Jinja2依赖 |
| matplotlib-inline | 0.2.1 | ipython依赖 |
| mdurl | 0.1.2 | markdown-it-py依赖 |
| mypy_extensions | 1.1.0 | mypy依赖 |
| nodeenv | 1.9.1 | pre-commit依赖 |
| parso | 0.8.5 | jedi依赖 |
| pathspec | 0.12.1 | black依赖 |
| pockets | 0.9.1 | pylint依赖 |
| prompt_toolkit | 3.0.52 | ipython依赖 |
| pure_eval | 0.2.3 | ipython依赖 |
| pyproject-api | 1.10.0 | pip-tools依赖 |
| pyproject_hooks | 1.2.0 | build依赖 |
| rich | 14.2.0 | 富文本输出 |
| snowballstemmer | 3.0.1 | Sphinx依赖 |
| sphinxcontrib-applehelp | 2.0.0 | Sphinx依赖 |
| sphinxcontrib-devhelp | 2.0.0 | Sphinx依赖 |
| sphinxcontrib-htmlhelp | 2.1.0 | Sphinx依赖 |
| sphinxcontrib-jquery | 4.1 | Sphinx依赖 |
| sphinxcontrib-jsmath | 1.0.1 | Sphinx依赖 |
| sphinxcontrib-qthelp | 2.0.0 | Sphinx依赖 |
| sphinxcontrib-serializinghtml | 2.0.0 | Sphinx依赖 |
| stack-data | 0.6.3 | ipython依赖 |
| stevedore | 5.6.0 | bandit依赖 |
| tomlkit | 0.13.13 | black依赖 |
| urllib3 | 2.6.2 | requests依赖 |
| virtualenv | 20.35.4 | tox依赖 |
| wcwidth | 0.2.14 | prompt_toolkit依赖 |
| wmctrl | 0.5 | 窗口管理工具（可能是误安装） |

## 4. 未使用依赖分析

### 4.1 核心依赖中的未使用依赖

- **colorama**：虽然在requirements.txt中声明，但代码中没有直接导入使用。这可能是一个遗留依赖，或者是计划使用但尚未实现的功能。

### 4.2 开发依赖中的未使用依赖

开发依赖在开发过程中是必要的，但在生产环境中可以移除。以下是一些可能在特定情况下不需要的开发依赖：

- **tox, tox-pyenv**：如果不使用tox进行测试，可以移除
- **pre-commit**：如果不使用Git钩子，可以移除
- **sphinx相关依赖**：如果不需要生成文档，可以移除
- **ipython**：如果不使用交互式调试，可以移除

### 4.3 未声明但已安装的依赖

这些依赖大多是其他依赖的间接依赖，或者是通过pip自动安装的。其中一些可能是不必要的，可以通过清理虚拟环境来移除。

## 5. 安全移除冗余依赖的操作建议

### 5.1 移除未使用的核心依赖

1. **移除colorama**：
   ```bash
   pip uninstall colorama
   ```
2. 从requirements.txt中删除colorama相关行

### 5.2 清理未声明的依赖

1. **重新创建虚拟环境**：
   ```bash
   # 备份当前虚拟环境（可选）
   cp -r .venv .venv_backup
   
   # 删除当前虚拟环境
   rm -rf .venv
   
   # 创建新的虚拟环境
   python -m venv .venv
   
   # 激活虚拟环境
   .venv\Scripts\activate
   
   # 安装核心依赖
   pip install -r Localization_Tool/requirements.txt
   
   # 安装开发依赖（可选）
   pip install -r Localization_Tool/dev-requirements.txt
   ```

### 5.3 更新requirements文件

1. **更新requirements.txt**：移除未使用的依赖，确保只包含生产环境必要的依赖
2. **更新dev-requirements.txt**：确保只包含开发环境必要的依赖
3. **使用pip-tools管理依赖**：
   ```bash
   # 安装pip-tools
   pip install pip-tools
   
   # 从requirements.in生成requirements.txt
   pip-compile Localization_Tool/requirements.in
   
   # 从dev-requirements.in生成dev-requirements.txt
   pip-compile Localization_Tool/dev-requirements.in
   ```

### 5.4 验证依赖移除的安全性

1. **运行项目测试**：确保移除依赖后项目功能正常
   ```bash
   pytest
   ```

2. **手动测试核心功能**：确保本地化工具的主要功能（提取、扩展、初始化等）正常工作

3. **检查依赖关系**：使用pipdeptree工具检查依赖关系
   ```bash
   pip install pipdeptree
   pipdeptree
   ```

## 6. 最佳实践建议

1. **定期清理依赖**：定期运行依赖分析，移除未使用的依赖
2. **区分生产和开发依赖**：明确区分生产环境和开发环境的依赖
3. **使用requirements.in和pip-tools**：使用requirements.in文件声明依赖，使用pip-tools生成锁定版本的requirements.txt
4. **使用虚拟环境**：为每个项目使用独立的虚拟环境，避免依赖冲突
5. **记录依赖变更**：在变更依赖时更新文档，说明变更原因
6. **定期更新依赖**：定期更新依赖到安全的最新版本，避免安全漏洞

## 7. 风险评估

- **依赖关系复杂**：某些依赖可能是间接依赖，移除时需要谨慎
- **版本兼容性问题**：移除依赖可能导致其他依赖的版本冲突
- **开发流程影响**：移除开发依赖可能影响开发流程

通过仔细分析和测试，可以安全地移除冗余依赖，减少项目的复杂性和存储空间占用，同时提高项目的可维护性和安全性。
