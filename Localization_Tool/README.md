# Starsector Mod 源码本地化工具

## 项目概述

Starsector Mod 源码本地化工具是一个专为 Starsector 游戏模组开发设计的本地化解决方案，支持从英文模组源码中提取字符串，生成映射规则，并将中文模组源码映射为英文，实现高效的模组本地化管理。

## 功能特点

- **多模式支持**：提供 Extract、Extend、Decompile 和文件管理四种模式
- **智能字符串提取**：支持从 Java/Kotlin 源码中自动提取字符串
- **灵活的映射规则**：支持 JSON 和 YAML 两种格式的映射规则文件
- **JAR 文件处理**：支持反编译和提取 JAR 文件内容
- **自动项目结构**：自动创建和维护标准的项目目录结构
- **详细的流程报告**：生成完整的执行报告，便于调试和分析
- **友好的用户界面**：提供交互式菜单和详细的用户引导

## 系统要求

- Python 3.8+ 
- Java 8+（用于 JAR 反编译）
- Windows 操作系统（推荐）
- 足够的磁盘空间（取决于处理的模组大小）

## 安装步骤

1. **克隆或下载项目**
   ```bash
   git clone https://github.com/your-repo/Starsectory-Mod-Localization-Tool.git
   ```

2. **安装依赖**
   ```bash
   cd Localization_Tool
   pip install -r requirements.txt
   ```

3. **配置环境**
   - 确保 Java 已正确安装并添加到系统 PATH
   - 检查 `config.yaml` 文件，根据需要调整配置

## 目录结构

```
Localization_Tool/
├── File/                     # 主目录结构
│   ├── source/               # 源文件存放区
│   │   ├── English/          # 英文源文件
│   │   │   ├── src/          # 英文源码文件夹
│   │   │   └── jars/         # 待反编译的英文 JAR 包
│   │   └── Chinese/          # 中文源文件
│   │       ├── src/          # 中文源码文件夹
│   │       └── jars/         # 待反编译的中文 JAR 包
│   ├── source_backup/        # 源文件备份
│   ├── rule/                 # 映射规则存放区（可选）
│   │   ├── English/          # 英文映射规则
│   │   └── Chinese/          # 中文映射规则
│   └── output/               # 结果输出区
│       ├── Extract_English/  # 英文提取结果
│       ├── Extract_Chinese/  # 中文提取结果
│       ├── Extend_en2zh/     # 英文到中文映射结果
│       └── Extend_zh2en/     # 中文到英文映射结果
├── src/                      # 工具源代码
│   ├── common/               # 通用模块
│   ├── decompile_mode/       # 反编译模式
│   ├── extend_mode/          # 映射模式
│   ├── extract_mode/         # 提取模式
│   ├── init_mode/            # 初始化模式
│   ├── main.py               # 主入口
│   └── run_localization.py   # 运行脚本
├── config.yaml               # 配置文件
├── requirements.txt          # 依赖列表
└── README.md                 # 项目文档
```

## 使用指南

### 运行工具

1. **直接运行**
   ```bash
   python src/main.py
   ```

2. **使用 run_localization.py 脚本**
   ```bash
   python run_localization.py
   ```

### 模式说明

#### 1. Extract 模式

**功能**：从源码或 JAR 文件中提取字符串，生成映射规则文件

**使用场景**：
- 提取英文源码中的字符串，生成英文映射规则
- 提取中文源码中的字符串，生成中文映射规则
- 反编译未汉化的 JAR 包，提取其中的字符串

**子流程**：
- 英文提取流程
- 中文提取流程

**输出文件**：
- `{language}_mappings.json` - 字符串映射规则（JSON 格式）
- `{language}_mappings.yaml` - 字符串映射规则（YAML 格式）
- `extract_{timestamp}_report.json` - 流程报告
- `mod_info.json` - MOD 信息文件

#### 2. Extend 模式

**功能**：使用映射规则将一种语言的源码映射为另一种语言

**使用场景**：
- 将中文源码映射为英文
- 将英文源码映射为中文
- 使用自定义映射规则进行字符串替换

**子流程**：
- 已有中文 src 文件夹映射流程
- 已有英文 src 文件夹映射流程

**输出内容**：
- 映射后的源码文件夹
- 字符串映射规则文件
- 流程报告
- MOD 信息文件

#### 3. Decompile 模式

**功能**：反编译或提取 JAR 文件内容

**使用场景**：
- 反编译单个 JAR 文件
- 反编译目录中所有 JAR 文件
- 提取单个 JAR 文件内容
- 提取目录中所有 JAR 文件内容

**子流程**：
- 反编译单个 JAR 文件
- 反编译目录中所有 JAR 文件
- 提取单个 JAR 文件内容
- 提取目录中所有 JAR 文件内容

#### 4. 文件管理模式

**功能**：管理项目文件结构，包括创建文件夹、重命名模组文件夹、恢复备份等

**使用场景**：
- 初始化项目文件夹结构
- 重命名模组文件夹
- 恢复备份文件
- 执行完整文件管理流程

## 配置说明

配置文件 `config.yaml` 包含以下主要配置项：

```yaml
# 工具根目录
tool_root: "c:\\Users\\Roki\\Documents\\GitHub\\Tool\\Localization_Tool"

# 源文件目录
source: "c:\\Users\\Roki\\Documents\\GitHub\\Tool\\Localization_Tool\\File\\source"

# 输出目录
output: "c:\\Users\\Roki\\Documents\\GitHub\\Tool\\Localization_Tool\\File\\output"

# 映射规则目录
rules: "c:\\Users\\Roki\\Documents\\GitHub\\Tool\\Localization_Tool\\File\\rule"

# 源文件备份目录
source_backup: "c:\\Users\\Roki\\Documents\\GitHub\\Tool\\Localization_Tool\\File\\source_backup"

# 显示欢迎引导
show_welcome_guide: true

# 自动打开输出文件夹
auto_open_output_folder: false
```

## 使用示例

### 示例 1：提取英文源码字符串

1. 将英文模组源码放入 `File/source/English/src` 目录
2. 运行工具，选择 "1. Extract模式"
3. 选择 "1. 英文提取流程"
4. 提取完成后，结果将保存到 `File/output/Extract_English/` 目录

### 示例 2：中文到英文映射

1. 将中文模组源码放入 `File/source/Chinese/src` 目录
2. 将映射规则文件放入 `File/rule/Chinese/` 目录
3. 运行工具，选择 "2. Extend模式"
4. 选择 "1. 中文映射到英文"
5. 映射完成后，结果将保存到 `File/output/Extend_zh2en/` 目录

### 示例 3：反编译 JAR 文件

1. 将待反编译的 JAR 文件放入 `File/source/English/jars` 目录
2. 运行工具，选择 "3. Decompile模式"
3. 选择 "2. 反编译目录中所有JAR文件"
4. 反编译完成后，结果将保存到相应的输出目录

## 命令行使用

工具支持命令行参数，便于自动化和脚本调用：

### Extract 模式
```bash
python main.py extract "英文提取流程"
python main.py extract "中文提取流程"
```

### Extend 模式
```bash
python main.py extend "已有中文src文件夹映射流程"
python main.py extend "已有英文src文件夹映射流程"
```

### Decompile 模式
```bash
python main.py decompile "反编译单个JAR文件"
python main.py decompile "反编译目录中所有JAR文件"
python main.py decompile "提取单个JAR文件内容"
python main.py decompile "提取目录中所有JAR文件内容"
```

### 测试模式
```bash
python main.py --test-mode "1,1,1"  # 测试 Extract 模式-简洁模式-提取英文
```

## 日志和报告

- **日志文件**：位于 `logs/` 目录下，记录工具运行的详细信息
- **流程报告**：每个操作完成后，在输出目录生成 `extract_{timestamp}_report.json` 或 `extend_{timestamp}_report.json`
- **报告内容**：包含检测结果、执行步骤、耗时统计、错误信息等

## 常见问题

1. **问题**：工具无法找到源文件
   **解决方法**：确保源文件已按要求放入 `File/source/` 目录下的正确位置

2. **问题**：JAR 反编译失败
   **解决方法**：检查 Java 是否正确安装，确保 JAR 文件没有损坏

3. **问题**：映射规则不生效
   **解决方法**：检查映射规则文件格式是否正确，确保文件名和路径符合要求

4. **问题**：工具运行缓慢
   **解决方法**：处理大型模组时，工具可能需要较长时间，请耐心等待

## 贡献方法

1. Fork 本项目
2. 创建功能分支 `git checkout -b feature/AmazingFeature`
3. 提交更改 `git commit -m 'Add some AmazingFeature'`
4. 推送到分支 `git push origin feature/AmazingFeature`
5. 提交 Pull Request

## 许可证信息

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 联系方式

- 项目地址：https://github.com/your-repo/Starsectory-Mod-Localization-Tool
- 问题反馈：https://github.com/your-repo/Starsectory-Mod-Localization-Tool/issues

## 更新日志

### v1.0.0 (2025-12-16)
- 初始版本
- 支持 Extract、Extend、Decompile 和文件管理四种模式
- 支持 JSON 和 YAML 两种映射规则格式
- 提供交互式菜单和命令行接口
- 生成详细的流程报告

## 致谢

- 感谢所有为本项目做出贡献的开发者
- 感谢 Starsector 社区的支持和反馈

---

**使用本工具前，请确保你已经阅读并理解了上述文档。如有任何问题或建议，欢迎提交 Issue 或 Pull Request。**
