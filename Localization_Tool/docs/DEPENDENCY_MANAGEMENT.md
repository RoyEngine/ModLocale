# 依赖管理文档与开发流程指南

## 1. 项目概述

本项目是一个游戏模组本地化工具，用于提取和管理游戏模组的本地化字符串。本文档旨在规范项目的依赖管理和开发流程，确保项目的可维护性和稳定性。

## 2. 依赖结构

### 2.1 核心依赖

核心依赖是项目运行所必需的依赖，位于 `requirements.txt` 和 `requirements.in` 文件中：

| 依赖包 | 用途 |
|--------|------|
| requests | 网络请求，用于下载反编译工具 |
| PyYAML | YAML文件处理，用于管理本地化映射规则 |
| tree-sitter | AST解析，用于提取源代码中的字符串 |
| tree-sitter-java | Java语言支持，用于解析Java源代码 |
| tree-sitter-kotlin | Kotlin语言支持，用于解析Kotlin源代码 |

### 2.2 开发依赖

开发依赖是开发过程中必需的依赖，位于 `dev-requirements.txt` 和 `dev-requirements.in` 文件中：

| 依赖类别 | 用途 | 主要依赖包 |
|----------|------|------------|
| 测试工具 | 运行单元测试和集成测试 | pytest, pytest-cov, pytest-mock |
| 代码检查工具 | 检查代码质量和风格 | flake8, pylint, mypy |
| 代码格式化工具 | 自动格式化代码 | black, isort |
| 文档生成工具 | 生成项目文档 | sphinx, sphinx-rtd-theme |
| Git钩子工具 | 自动运行代码检查 | pre-commit |
| 依赖管理工具 | 管理项目依赖 | pip-tools |
| 调试工具 | 调试代码 | ipython |

## 3. 依赖管理工具

### 3.1 pip-tools

项目使用 `pip-tools` 进行依赖管理，具有以下优点：

- 支持声明式依赖定义（通过 `.in` 文件）
- 生成锁定版本的依赖文件（通过 `.txt` 文件）
- 自动解析依赖关系
- 支持开发环境和生产环境分离

### 3.2 安装 pip-tools

```bash
pip install pip-tools
```

## 4. 依赖管理流程

### 4.1 添加新依赖

1. **添加到 `.in` 文件**：
   - 对于核心依赖，添加到 `requirements.in`
   - 对于开发依赖，添加到 `dev-requirements.in`

2. **生成锁定版本的依赖文件**：
   ```bash
   # 生成核心依赖文件
   pip-compile requirements.in
   
   # 生成开发依赖文件
   pip-compile dev-requirements.in
   ```

3. **安装更新后的依赖**：
   ```bash
   pip install -r requirements.txt
   pip install -r dev-requirements.txt
   ```

### 4.2 更新现有依赖

1. **更新特定依赖**：
   ```bash
   # 更新核心依赖中的 requests
   pip-compile --upgrade-package requests requirements.in
   
   # 更新开发依赖中的 pytest
   pip-compile --upgrade-package pytest dev-requirements.in
   ```

2. **更新所有依赖**：
   ```bash
   # 更新所有核心依赖
   pip-compile --upgrade requirements.in
   
   # 更新所有开发依赖
   pip-compile --upgrade dev-requirements.in
   ```

3. **安装更新后的依赖**：
   ```bash
   pip install -r requirements.txt
   pip install -r dev-requirements.txt
   ```

### 4.3 移除未使用的依赖

1. **运行依赖分析**：
   ```bash
   python ../analyze_dependencies.py
   ```

2. **查看分析报告**：
   打开生成的 `dependency_analysis_report.md` 文件，查看未使用的依赖列表。

3. **移除未使用的依赖**：
   - 从 `.in` 文件中删除未使用的依赖
   - 重新生成锁定版本的依赖文件
   - 卸载未使用的依赖：
     ```bash
     pip uninstall <package_name>
     ```

## 5. 开发环境设置

### 5.1 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境（Windows）
.venv\Scripts\activate

# 激活虚拟环境（Linux/macOS）
source .venv/bin/activate
```

### 5.2 安装依赖

```bash
# 安装核心依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -r dev-requirements.txt
```

### 5.3 配置Git钩子

```bash
pre-commit install
```

## 6. 代码质量检查

### 6.1 运行代码检查

```bash
# 运行flake8检查代码风格
flake8 src/

# 运行pylint检查代码质量
pylint src/

# 运行mypy检查类型注解
mypy src/
```

### 6.2 自动格式化代码

```bash
# 使用black格式化代码
black src/

# 使用isort排序导入
isort src/
```

## 7. 测试流程

### 7.1 运行测试

```bash
# 运行所有测试
python -m pytest

# 运行特定测试文件
python -m pytest test/test_file.py

# 运行测试并生成覆盖率报告
python -m pytest --cov=src --cov-report=html
```

### 7.2 测试覆盖率要求

- 核心功能测试覆盖率要求达到 80% 以上
- 新添加的代码必须包含相应的测试用例

## 8. CI/CD工作流

### 8.1 GitHub Actions

项目使用GitHub Actions进行持续集成和持续部署，包含以下工作流：

1. **构建和测试工作流**：
   - 触发条件：代码推送到 main/master 分支、创建/更新 pull request、每周日定期运行
   - 运行环境：Windows
   - Python版本：3.10, 3.11, 3.12, 3.14
   - 执行步骤：
     - 检查代码
     - 设置Python环境
     - 安装依赖
     - 运行测试
     - 运行代码检查
     - 运行依赖分析

2. **依赖分析工作流**：
   - 触发条件：每周一定期运行、手动触发
   - 执行步骤：
     - 检查代码
     - 设置Python环境
     - 运行依赖分析
     - 上传分析报告
     - 如果存在未使用的依赖，自动创建或更新GitHub Issue

### 8.2 查看CI/CD结果

- 进入项目的GitHub仓库
- 点击 "Actions" 标签
- 查看对应的工作流运行结果

## 9. 依赖更新策略

### 9.1 定期更新

- 核心依赖：每季度更新一次
- 开发依赖：每月更新一次
- 安全补丁：立即更新

### 9.2 更新流程

1. **更新依赖**：
   ```bash
   pip-compile --upgrade requirements.in
   pip-compile --upgrade dev-requirements.in
   ```

2. **运行测试**：
   ```bash
   python -m pytest
   ```

3. **运行代码检查**：
   ```bash
   flake8 src/
   pylint src/
   mypy src/
   ```

4. **提交更改**：
   ```bash
   git add requirements.txt dev-requirements.txt
   git commit -m "Update dependencies"
   git push
   ```

## 10. 依赖分析工具

### 10.1 使用依赖分析脚本

项目提供了 `analyze_dependencies.py` 脚本，用于分析项目的依赖使用情况：

```bash
# 运行依赖分析
python ../analyze_dependencies.py
```

### 10.2 分析报告

脚本会生成两份报告：

1. **Markdown报告** (`dependency_analysis_report.md`)：
   - 依赖概览
   - 未使用的依赖列表
   - 代码中使用的外部依赖
   - 项目声明的依赖
   - 建议操作

2. **JSON报告** (`dependency_analysis_report.json`)：
   - 结构化的依赖分析数据，可用于自动化处理

## 11. 最佳实践

### 11.1 依赖管理最佳实践

1. **明确区分核心依赖和开发依赖**
2. **使用锁定版本的依赖文件**
3. **定期运行依赖分析**
4. **及时更新依赖，特别是安全补丁**
5. **避免使用未声明的依赖**
6. **使用虚拟环境隔离项目依赖**

### 11.2 开发流程最佳实践

1. **遵循PEP 8代码风格**
2. **使用类型注解**
3. **编写单元测试**
4. **使用Git分支管理开发**
5. **遵循Conventional Commits提交规范**
6. **定期运行代码检查和测试**

## 12. 常见问题

### 12.1 依赖冲突

**问题**：安装依赖时出现版本冲突

**解决方案**：
1. 检查冲突的依赖版本
2. 调整 `.in` 文件中的版本约束
3. 重新生成锁定版本的依赖文件
4. 如果问题无法解决，考虑使用 `pipdeptree` 工具分析依赖关系：
   ```bash
   pip install pipdeptree
   pipdeptree
   ```

### 12.2 依赖安装失败

**问题**：安装依赖时出现网络错误或其他错误

**解决方案**：
1. 检查网络连接
2. 尝试使用国内镜像源：
   ```bash
   pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
   ```
3. 检查Python版本是否符合要求
4. 检查操作系统是否兼容

### 12.3 依赖分析脚本错误

**问题**：运行依赖分析脚本时出现错误

**解决方案**：
1. 检查Python版本（要求Python 3.10+）
2. 确保已安装所有必要的依赖
3. 查看错误信息，针对性解决问题

## 13. 总结

本文档规范了项目的依赖管理和开发流程，旨在提高项目的可维护性和稳定性。所有开发人员应严格遵循本文档的规定，确保项目的顺利进行。

定期更新依赖、运行测试和代码检查是保证项目质量的重要手段，应作为开发流程的一部分持续执行。
