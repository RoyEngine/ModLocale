1. **问题分析**：程序启动时，`init_mode` 应该被自动初始化，但目前只有在执行特定文件管理操作时才会初始化，导致后续操作因依赖未初始化的 `init_mode` 而失败。

2. **修复方案**：在 `main()` 函数中添加 `init_mode` 初始化调用，确保在执行任何模式之前，`init_mode` 已被正确初始化。

3. **具体修改**：

   * 修改 `src/main.py` 文件，在 `main()` 函数中，在执行任何模式之前，添加 `init_mode` 初始化代码

   * 调用 `init_mode` 中的 `run_init_tasks()` 函数，确保完整的初始化流程被执行

4. **验证方案**：

   * 运行 `python src/main.py extract "中文提取流程"`，验证 Extract 模式能否正常执行

   * 运行 `python src/main.py extend "已有中文src文件夹映射流程"`，验证 Extend 模式能否正常执行

   * 检查生成的输出文件，确保 `init_mode` 初始化成功，mod 映射关系正确构建

5. **预期结果**：

   * 程序启动时，`init_mode` 被自动初始化

   * Extract、Extend 和 Decompile 模式能够正常执行，不再因 `init_mode` 未初始化而失败

   * 生成的 YAML 和 JSON 文件中包含正确的 `id` 字段，使用 mod\_info.json 中的实际 id 值

6. **修改文件**：

   * `src/main.py`：添加 `init_mode` 初始化调用

7. **测试用例**：

   * 执行 Extract 模式，验证能否正确提取字符串并生成映射文件

   * 执行 Extend 模式，验证能否正确使用映射规则进行字符串映射

   * 检查生成的映射文件，验证 `id` 字段是否正确

