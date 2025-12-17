# 安装指南

## 环境要求

- **Python 3.8+**：确保系统已安装Python 3.8或更高版本
- **pip包管理工具**：Python默认自带pip，用于安装依赖
- **操作系统**：支持Windows、Linux和macOS

## 检查Python版本

在安装前，建议先检查系统中已安装的Python版本：

```bash
# 检查Python版本
python --version

# 或使用python3（某些系统）
python3 --version
```

## 安装步骤

### 1. 克隆项目仓库

使用Git克隆项目到本地：

```bash
git clone https://github.com/your-username/Localization_Tool.git
cd Localization_Tool
```

### 2. 创建并激活虚拟环境

为了避免依赖冲突，建议在虚拟环境中安装和运行工具：

#### Windows

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
.venv\Scripts\activate
```

#### Linux/macOS

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
source .venv/bin/activate
```

### 3. 安装依赖

使用pip安装项目所需的依赖：

```bash
# 安装生产依赖
pip install -r requirements.txt

# （可选）安装开发依赖（用于测试和开发）
pip install -r dev-requirements.txt
```

## 验证安装

安装完成后，可以运行工具来验证是否安装成功：

```bash
# 查看工具版本
python main_workflow.py --help
```

如果看到工具的帮助信息，则说明安装成功。

## 升级工具

当有新版本发布时，可以通过以下命令升级：

```bash
# 更新代码
cd Localization_Tool
git pull origin main

# 升级依赖
pip install --upgrade -r requirements.txt
```

## 常见安装问题

### 1. Python版本不兼容

**问题**：
```
ERROR: This package requires Python >=3.8, but you're running Python 3.7.4
```

**解决方案**：
- 升级Python到3.8或更高版本
- 使用pyenv或类似工具管理多个Python版本

### 2. 依赖安装失败

**问题**：
```
ERROR: Could not install packages due to an OSError: [Errno 13] Permission denied
```

**解决方案**：
- 使用虚拟环境避免权限问题
- 或使用`--user`参数安装到用户目录：
  ```bash
  pip install --user -r requirements.txt
  ```

### 3. Tree-sitter相关依赖安装失败

**问题**：
```
ERROR: Failed building wheel for tree-sitter
```

**解决方案**：
- 确保系统已安装编译工具：
  - Windows：安装Visual Studio Build Tools
  - Linux：安装gcc和make
  - macOS：安装Xcode Command Line Tools

### 4. 虚拟环境激活失败

**问题**：
- Windows：
  ```
  .venv\Scripts\activate : 无法加载文件 .venv\Scripts\activate，因为在此系统上禁止运行脚本。
  ```

**解决方案**：
- 以管理员身份运行PowerShell
- 执行以下命令修改执行策略：
  ```powershell
  Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

## 卸载工具

如果需要卸载工具，只需删除项目目录和虚拟环境：

```bash
# 退出虚拟环境
deactivate

# 删除项目目录
rm -rf Localization_Tool
```

## 下一步

安装完成后，可以继续阅读[使用指南](usage.md)来了解如何使用本地化工具。
