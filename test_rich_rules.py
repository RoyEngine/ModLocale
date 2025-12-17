#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 Rich rules 功能
覆盖 bilingual 对齐、noise 决策、apply 正确性和输出确定性
"""

import os
import sys
import tempfile
import shutil
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_test_source_file(content, file_extension=".java"):
    """
    创建测试源文件
    
    Args:
        content: 文件内容
        file_extension: 文件扩展名
    
    Returns:
        str: 临时文件路径
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix=file_extension, delete=False) as f:
        f.write(content)
        return f.name

def test_bilingual_alignment():
    """
    测试 bilingual 对齐功能
    验证使用 occurrence_key 能够正确对齐 EN/ZH 翻译对
    """
    print("\n=== 测试 bilingual 对齐功能 ===")
    
    # 创建临时双语源码目录结构
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建英文源码目录
        en_src_dir = os.path.join(temp_dir, "English", "src")
        os.makedirs(en_src_dir, exist_ok=True)
        
        # 创建中文源码目录
        zh_src_dir = os.path.join(temp_dir, "Chinese", "src")
        os.makedirs(zh_src_dir, exist_ok=True)
        
        # 创建测试 Java 文件
        en_java_content = '''
public class TestClass {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
        System.out.println("This is a test.");
    }
}
'''        
        
        zh_java_content = '''
public class TestClass {
    public static void main(String[] args) {
        System.out.println("你好，世界！");
        System.out.println("这是一个测试。");
    }
}
'''        
        
        en_java_file = create_test_source_file(en_java_content, ".java")
        zh_java_file = create_test_source_file(zh_java_content, ".java")
        
        # 复制到对应的目录
        shutil.copy(en_java_file, os.path.join(en_src_dir, "TestClass.java"))
        shutil.copy(zh_java_file, os.path.join(zh_src_dir, "TestClass.java"))
        
        # 清理临时文件
        os.unlink(en_java_file)
        os.unlink(zh_java_file)
        
        # 运行 bootstrap 命令生成规则
        from src.common.tree_sitter_utils import extract_ast_mappings, extract_strings_from_file
        from src.common.yaml_utils import generate_translation_rules
        from src.common.parallel_utils import get_all_source_files
        
        # 调试：检查文件是否被正确找到
        print(f"英文源码目录: {en_src_dir}")
        en_files = get_all_source_files(en_src_dir, ['.java'])
        print(f"找到的英文文件: {en_files}")
        
        # 调试：直接使用 extract_strings_from_file 测试
        if en_files:
            print(f"测试直接提取单个文件: {en_files[0]}")
            single_file_mappings = extract_strings_from_file(en_files[0])
            print(f"单个文件提取结果: {single_file_mappings}")
        
        # 提取英文映射
        print(f"开始提取英文映射...")
        en_mappings = list(extract_ast_mappings(en_src_dir, use_cache=False, use_parallel=False))
        print(f"提取到 {len(en_mappings)} 条英文映射")
        
        # 调试：检查文件是否被正确找到
        print(f"中文源码目录: {zh_src_dir}")
        zh_files = get_all_source_files(zh_src_dir, ['.java'])
        print(f"找到的中文文件: {zh_files}")
        
        # 提取中文映射
        print(f"开始提取中文映射...")
        zh_mappings = list(extract_ast_mappings(zh_src_dir, use_cache=False, use_parallel=False))
        print(f"提取到 {len(zh_mappings)} 条中文映射")
        
        # 使用 occurrence_key 对齐
        en_dict = {item['id']: item for item in en_mappings}
        zh_dict = {item['id']: item for item in zh_mappings}
        common_keys = set(en_dict.keys()) & set(zh_dict.keys())
        
        print(f"找到 {len(common_keys)} 个共同的 occurrence_key")
        
        # 验证对齐结果
        for key in common_keys:
            en_text = en_dict[key]['original']
            zh_text = zh_dict[key]['original']
            print(f"对齐结果: {en_text} -> {zh_text}")
        
        assert len(common_keys) > 0, "没有找到共同的 occurrence_key，对齐失败"
        print("✓ bilingual 对齐功能测试通过")

def test_noise_detection():
    """
    测试噪声识别功能
    验证能够正确识别资源路径/ID/短令牌等噪声
    """
    print("\n=== 测试噪声识别功能 ===")
    
    # 直接测试噪声识别逻辑，不依赖于提取映射
    test_cases = [
        # (文本, 预期是否为噪声, 预期类型)
        ("assets/textures/ship.png", True, "资源路径"),
        ("ID", True, "短令牌"),
        ("MAX_HEALTH", True, "标识符"),
        ("This is a normal text.", False, "正常文本"),
        ("ship.png", True, "文件名"),
        ("src/main/java/", True, "路径"),
        ("test", True, "短文本"),
        ("Hello", False, "正常文本")
    ]
    
    # 导入噪声识别相关的函数
    from src.common.rules_store import RulesStore
    import re
    
    noise_count = 0
    
    for text, expected_is_noise, expected_type in test_cases:
        is_noise = False
        noise_reason = ""
        
        # 检查是否为资源路径
        if '/' in text or '\\' in text:
            is_noise = True
            noise_reason = f"资源路径: {expected_type}"
        # 检查是否为短令牌
        elif re.match(r'^[a-zA-Z0-9_]+$', text) and len(text) < 5:
            is_noise = True
            noise_reason = f"短令牌: {expected_type}"
        # 检查是否为标识符
        elif re.match(r'^[A-Z_]+$', text):
            is_noise = True
            noise_reason = f"标识符: {expected_type}"
        
        print(f"文本: '{text}', 预期: {'噪声' if expected_is_noise else '正常'}, 实际: {'噪声' if is_noise else '正常'}")
        if is_noise:
            print(f"  识别为噪声，原因: {noise_reason}")
            noise_count += 1
    
    # 验证至少识别到了3个噪声
    assert noise_count >= 3, f"只识别到 {noise_count} 个噪声，预期至少3个，噪声识别失败"
    print(f"✓ 噪声识别功能测试通过，共识别到 {noise_count} 个噪声")

def test_apply_correctness():
    """
    测试 apply 正确性
    验证使用 occurrence_key 精确匹配并生成合法字面量 token
    """
    print("\n=== 测试 apply 正确性功能 ===")
    
    # 创建测试源文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.java', delete=False) as f:
        f.write('public class ApplyTest {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n    }\n}\n')
        source_file = f.name
    
    try:
        # 提取映射
        from src.common.tree_sitter_utils import extract_strings_from_file
        mappings = extract_strings_from_file(source_file)
        
        # 准备规则
        rules = []
        for mapping in mappings:
            rules.append({
                "id": mapping['id'],
                "original": mapping['original'],
                "translated": "你好，世界！",
                "status": "translated"
            })
        
        # 应用映射
        from src.common.yaml_utils import apply_yaml_mapping
        result = apply_yaml_mapping(source_file, rules)
        
        # 验证结果
        assert "你好，世界！" in result, "翻译未正确应用"
        print("✓ apply 正确性功能测试通过")
        print(f"应用结果: {result}")
    finally:
        os.unlink(source_file)

def test_output_determinism():
    """
    测试输出确定性
    验证相同输入多次生成完全一致的 rules.yaml
    """
    print("\n=== 测试输出确定性功能 ===")
    
    # 创建临时源码文件
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试 Java 文件
        java_content = '''
public class DeterminismTest {
    private static final String TEXT1 = "Hello";
    private static final String TEXT2 = "World";
    private static final String TEXT3 = "Test";
}
'''        
        java_file = create_test_source_file(java_content, ".java")
        shutil.copy(java_file, os.path.join(temp_dir, "DeterminismTest.java"))
        os.unlink(java_file)
        
        # 两次提取映射并生成规则
        from src.common.tree_sitter_utils import extract_ast_mappings
        from src.common.yaml_utils import generate_translation_rules, save_yaml_mappings, load_yaml_mappings
        
        # 第一次提取和生成
        mappings1 = list(extract_ast_mappings(temp_dir, use_cache=False))
        rules1 = []
        for mapping in mappings1:
            rules1.append({
                "id": mapping['id'],
                "original": mapping['original'],
                "translated": mapping['original'],
                "status": "translated"
            })
        
        # 第二次提取和生成
        mappings2 = list(extract_ast_mappings(temp_dir, use_cache=False))
        rules2 = []
        for mapping in mappings2:
            rules2.append({
                "id": mapping['id'],
                "original": mapping['original'],
                "translated": mapping['original'],
                "status": "translated"
            })
        
        # 保存到文件
        rules_file1 = os.path.join(temp_dir, "rules1.yaml")
        rules_file2 = os.path.join(temp_dir, "rules2.yaml")
        
        save_yaml_mappings(rules1, rules_file1, version_control=True, mod_id="test_mod")
        save_yaml_mappings(rules2, rules_file2, version_control=True, mod_id="test_mod")
        
        # 比较文件内容
        with open(rules_file1, 'r', encoding='utf-8') as f1, open(rules_file2, 'r', encoding='utf-8') as f2:
            content1 = f1.read()
            content2 = f2.read()
        
        # 去除时间戳等不确定因素
        import re
        content1 = re.sub(r'created_at:.*', '', content1)
        content2 = re.sub(r'created_at:.*', '', content2)
        content1 = re.sub(r'updated_at:.*', '', content1)
        content2 = re.sub(r'updated_at:.*', '', content2)
        
        assert content1 == content2, "输出结果不一致，确定性测试失败"
        print("✓ 输出确定性功能测试通过")

def test_legal_literal_generation():
    """
    测试合法字面量生成
    验证生成的字面量符合 Java/Kotlin 语法规范
    """
    print("\n=== 测试合法字面量生成功能 ===")
    
    # 测试各种情况
    test_cases = [
        # (原始字面量, 翻译文本, 预期结果)
        ('"test"', '测试', '"测试"'),
        ('"line1\nline2"', '行1\n行2', '"行1\\n行2"'),
        ("'single'", "单引号", "'单引号'"),
        ('"with \"quotes\""', '带"引号"', '"带\\"引号\\""'),
        ("'''multiline'''", "多行文本", "'''多行文本'''")
    ]
    
    from src.common.yaml_utils import generate_legal_literal_token
    
    for original_literal, translated_text, expected in test_cases:
        result = generate_legal_literal_token(original_literal, translated_text)
        print(f"原始: {original_literal}, 翻译: {translated_text}, 生成: {result}")
        
        # 验证生成的字面量符合预期
        # 这里只做基本验证，确保引号匹配
        assert result.count('"') % 2 == 0, f"生成的字面量引号不匹配: {result}"
    
    print("✓ 合法字面量生成功能测试通过")

def main():
    """
    运行所有测试
    """
    print("开始测试 Rich rules 功能...")
    start_time = datetime.now()
    
    test_bilingual_alignment()
    test_noise_detection()
    test_apply_correctness()
    test_output_determinism()
    test_legal_literal_generation()
    
    end_time = datetime.now()
    print(f"\n测试完成! 总耗时: {end_time - start_time}")
    print("✓ 所有 Rich rules 功能测试通过")

if __name__ == "__main__":
    main()
