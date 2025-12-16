## 问题分析

导致生成嵌套 `File/File` 文件夹的根本原因是路径拼接错误：

1. **main.py** 中调用 `run_init_tasks(mod_root)`，其中 `mod_root` 已经是包含 `File` 目录的完整路径，例如：`C:\Users\Roki\Documents\GitHub\Tool\legacy\Localization_Tool\File`

2. **init_mode/core.py** 中 `init_project_structure` 函数接收这个 `base_path` 参数，并遍历 `REQUIRED_FOLDERS` 列表创建文件夹

3. **REQUIRED_FOLDERS** 列表中的路径都以 `File/` 开头，例如 `File/source/Chinese`

4. 当执行 `os.path.join(base_path, folder_rel_path)` 时，就会产生重复的 `File` 目录，例如：
   ```
   C:\Users\Roki\Documents\GitHub\Tool\legacy\Localization_Tool\File + File/source/Chinese
   = C:\Users\Roki\Documents\GitHub\Tool\legacy\Localization_Tool\File\File\source\Chinese
   ```

## 修复方案

修改 `init_mode/core.py` 中的 `REQUIRED_FOLDERS` 列表，移除所有路径前的 `File/` 前缀，直接使用相对路径：

```python
# 项目所需的基础文件夹结构
REQUIRED_FOLDERS = [
    "source/Chinese",
    "source/English",
    "source_backup/Chinese",
    "source_backup/English",
    "output/Extract_Chinese",
    "output/Extract_English",
    "output/Extend_en2zh",
    "output/Extend_zh2en",
    "rule/Chinese",
    "rule/English",
]
```

这样，当 `init_project_structure` 函数执行时，路径拼接就会正确生成：
```
C:\Users\Roki\Documents\GitHub\Tool\legacy\Localization_Tool\File + source/Chinese
= C:\Users\Roki\Documents\GitHub\Tool\legacy\Localization_Tool\File\source\Chinese
```

## 修复理由

1. **路径逻辑一致性**：`run_init_tasks` 函数接收的 `base_path` 参数已经是正确的 `mod_root` 路径，包含了 `File` 目录，因此 `REQUIRED_FOLDERS` 列表中的路径不应再包含 `File/` 前缀

2. **避免重复路径**：移除 `File/` 前缀后，路径拼接不会产生重复的目录结构

3. **代码简洁性**：直接使用相对路径更简洁，也更符合函数的设计意图

4. **易于维护**：修改后路径逻辑更清晰，便于后续维护和扩展