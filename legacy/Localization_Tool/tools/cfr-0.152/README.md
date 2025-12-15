# CFR 反编译工具说明

## 概述

CFR 是一个功能强大的 Java 反编译工具，用于将 Java 字节码反编译为可读的 Java 源代码。在本项目中，CFR 主要用于反编译 JAR 文件，提取其中的源代码进行字符串本地化处理。

## 工具信息

- **工具名称**：CFR(Class File Reader)
- **版本**：0.152
- **用途**：Java 反编译工具，用于反编译 JAR 文件
- **许可证**：MIT License
- **来源**：[CFR 官方网站](https://www.benf.org/other/cfr/)

## 目录结构

```
cfr-0.152/
├── cfr-0.152.jar  # 主程序 JAR 文件
└── README.md     # 本说明文件
```

## 安装说明

该工具已经预先下载并放置在当前目录中，无需额外安装。使用前请确保已安装 Java 运行时环境(JRE 8+)。

## 使用方法

### 基本用法

```bash
# 反编译单个 JAR 文件
java -jar cfr-0.152.jar path/to/your.jar

# 反编译单个 JAR 文件并输出到指定目录
java -jar cfr-0.152.jar path/to/your.jar --outputdir path/to/output

# 反编译单个类文件
java -jar cfr-0.152.jar path/to/your.class
```

### 常用命令行参数

| 参数 | 描述 | 示例 |
|------|------|------|
| `--outputdir` | 指定输出目录 | `--outputdir decompiled` |
| `--showversion` | 显示版本信息 | `--showversion` |
| `--help` | 显示帮助信息 | `--help` |
| `--caseinsensitivefs` | 处理大小写不敏感的文件系统 | `--caseinsensitivefs` |
| `--jarfilter` | 过滤 JAR 文件中的类 | `--jarfilter com.example` |
| `--hidebridge` | 隐藏桥接方法 | `--hidebridge` |
| `--hidelangimports` | 隐藏语言导入 | `--hidelangimports` |
| `--hideutf` | 隐藏 UTF 字符 | `--hideutf` |
| `--removebadgenerics` | 移除错误的泛型 | `--removebadgenerics` |

## 示例

### 反编译 JAR 文件

```bash
# 简单反编译
java -jar cfr-0.152.jar MyApp.jar

# 反编译到指定目录
java -jar cfr-0.152.jar MyApp.jar --outputdir decompiled

# 反编译并显示版本信息
java -jar cfr-0.152.jar MyApp.jar --showversion
```

### 反编译特定类

```bash
# 反编译单个类
java -jar cfr-0.152.jar com/example/MyClass.class

# 从 JAR 文件中反编译特定类
java -jar cfr-0.152.jar MyApp.jar --jarfilter com.example.MyClass
```

## 注意事项

1. CFR 是一个纯 Java 工具，需要 Java 运行时环境才能运行
2. 支持反编译 Java 6 到 Java 16 的字节码
3. 可以反编译单个类文件或整个 JAR 文件
4. 输出的代码可能与原始代码有所不同，但功能保持一致
5. 对于复杂的代码，可能会生成一些不太易读的代码
6. 可以通过命令行参数调整反编译行为

## 与其他反编译工具的比较

| 工具 | 优点 | 缺点 |
|------|------|------|
| CFR | 支持最新 Java 版本，免费开源 | 对于复杂代码生成的可读性较差 |
| Procyon | 生成的代码可读性好 | 支持的 Java 版本相对较少 |
| JD-GUI | 图形界面，易于使用 | 商业软件，功能有限 |
| Fernflower | 开源，生成的代码质量高 | 配置复杂 |

## 帮助信息

```bash
# 查看帮助信息
java -jar cfr-0.152.jar --help
```

## 许可证

MIT License

## 来源链接

- [CFR 官方网站](https://www.benf.org/other/cfr/)
- [CFR GitHub 仓库](https://github.com/leibnitz27/cfr)