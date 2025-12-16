# Procyon 反编译工具说明

## 概述

Procyon 是一个功能强大的 Java 反编译工具，以生成高质量、易读的 Java 源代码而闻名。在本项目中，Procyon 主要用于反编译 JAR 文件，提取其中的源代码进行字符串本地化处理。

## 工具信息

- **工具名称**：Procyon Decompiler
- **版本**：0.6.0
- **用途**：Java 反编译工具，用于反编译 JAR 文件
- **许可证**：Apache License 2.0
- **来源**：[Procyon GitHub 仓库](https://github.com/mstrobel/procyon)

## 目录结构

```
procyon-decompiler-0.6.0/
├── procyon-decompiler-0.6.0.jar  # 主程序 JAR 文件
└── README.md                    # 本说明文件
```

## 安装说明

该工具已经预先下载并放置在当前目录中，无需额外安装。使用前请确保已安装 Java 运行时环境(JRE 8+)。

## 使用方法

### 基本用法

```bash
# 反编译单个 JAR 文件
java -jar procyon-decompiler-0.6.0.jar path/to/your.jar

# 反编译单个 JAR 文件并输出到指定目录
java -jar procyon-decompiler-0.6.0.jar -o path/to/output path/to/your.jar

# 反编译单个类文件
java -jar procyon-decompiler-0.6.0.jar path/to/your.class
```

### 常用命令行参数

| 参数 | 描述 | 示例 |
|------|------|------|
| `-o`, `--output-directory` | 指定输出目录 | `-o decompiled` |
| `-f`, `--flat` | 扁平化输出目录结构 | `-f` |
| `-r`, `--recursive` | 递归反编译目录 | `-r` |
| `-j`, `--java-version` | 指定目标 Java 版本 | `-j 8` |
| `-l`, `--line-numbers` | 保留行号 | `-l` |
| `-c`, `--clobber` | 覆盖现有文件 | `-c` |
| `-v`, `--verbose` | 显示详细输出 | `-v` |
| `-h`, `--help` | 显示帮助信息 | `-h` |

## 示例

### 反编译 JAR 文件

```bash
# 简单反编译
java -jar procyon-decompiler-0.6.0.jar MyApp.jar

# 反编译到指定目录
java -jar procyon-decompiler-0.6.0.jar -o decompiled MyApp.jar

# 扁平化输出目录结构
java -jar procyon-decompiler-0.6.0.jar -o decompiled -f MyApp.jar

# 保留行号
java -jar procyon-decompiler-0.6.0.jar -o decompiled -l MyApp.jar
```

### 反编译多个文件

```bash
# 反编译多个 JAR 文件
java -jar procyon-decompiler-0.6.0.jar -o decompiled jar1.jar jar2.jar jar3.jar

# 递归反编译目录中的所有 JAR 文件
java -jar procyon-decompiler-0.6.0.jar -o decompiled -r lib/
```

### 反编译特定类

```bash
# 反编译单个类文件
java -jar procyon-decompiler-0.6.0.jar com/example/MyClass.class

# 从 JAR 文件中反编译特定类
java -jar procyon-decompiler-0.6.0.jar -o decompiled MyApp.jar com.example.MyClass
```

## 注意事项

1. Procyon 是一个纯 Java 工具，需要 Java 运行时环境才能运行
2. 支持反编译 Java 5 到 Java 11 的字节码
3. 生成的代码质量高，易于阅读和理解
4. 可以反编译单个类文件或整个 JAR 文件
5. 支持复杂的 Java 语言特性，如泛型、枚举、注解等
6. 可以保留原始代码的行号信息
7. 支持扁平化输出目录结构，适合简单项目
8. 对于非常复杂的代码，生成的代码可能会有一些小问题

## 与其他反编译工具的比较

| 工具 | 优点 | 缺点 |
|------|------|------|
| Procyon | 生成的代码可读性好，支持复杂的 Java 特性 | 支持的 Java 版本相对较少 |
| CFR | 支持最新 Java 版本，免费开源 | 对于复杂代码生成的可读性较差 |
| JD-GUI | 图形界面，易于使用 | 商业软件，功能有限 |
| Fernflower | 开源，生成的代码质量高 | 配置复杂 |

## 帮助信息

```bash
# 查看帮助信息
java -jar procyon-decompiler-0.6.0.jar --help
```

## 许可证

Apache License 2.0

## 来源链接

- [Procyon GitHub 仓库](https://github.com/mstrobel/procyon)
- [Procyon 官方网站](https://bitbucket.org/mstrobel/procyon/wiki/Home)