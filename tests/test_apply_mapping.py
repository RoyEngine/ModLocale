#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试翻译回写功能，包括批量回写
"""

import os
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

# 从当前目录导入模块
from src.common.yaml_utils import load_yaml_mappings, apply_yaml_mapping, generate_translation_rules

# 测试单个文件翻译回写功能
def test_single_file_mapping():
    """
    测试单个文件的翻译回写功能
    """
    print("=" * 60)
    print("          测试单个文件翻译回写功能")
    print("=" * 60)
    
    # 创建测试数据
    with tempfile.TemporaryDirectory() as temp_dir:
        # 1. 创建测试英文源文件
        test_source_content = '''
public class TestGame {
    public static void main(String[] args) {
        System.out.println("Start Game");
        System.out.println("Exit Game");
        System.out.println("Settings");
    }
}
        '''
        
        source_file = os.path.join(temp_dir, "TestGame.java")
        with open(source_file, 'w', encoding='utf-8') as f:
            f.write(test_source_content.strip())
        
        print(f"\n[TEST] 原始源文件: {source_file}")
        print("原始内容:")
        print("-" * 40)
        with open(source_file, 'r', encoding='utf-8') as f:
            print(f.read())
        print("-" * 40)
        
        # 2. 创建双语映射数据
        english_mappings = [
            {
                "id": "TestGame.java:3",
                "original": "Start Game",
                "context": "UI/MainMenu",
                "placeholders": []
            },
            {
                "id": "TestGame.java:4",
                "original": "Exit Game",
                "context": "UI/MainMenu",
                "placeholders": []
            },
            {
                "id": "TestGame.java:5",
                "original": "Settings",
                "context": "UI/Settings",
                "placeholders": []
            }
        ]
        
        chinese_mappings = [
            {
                "id": "TestGame.java:3",
                "original": "开始游戏",
                "context": "UI/MainMenu",
                "placeholders": []
            },
            {
                "id": "TestGame.java:4",
                "original": "退出游戏",
                "context": "UI/MainMenu",
                "placeholders": []
            },
            {
                "id": "TestGame.java:5",
                "original": "设置",
                "context": "UI/Settings",
                "placeholders": []
            }
        ]
        
        # 3. 生成翻译规则
        rules_file = os.path.join(temp_dir, "rules.yaml")
        generate_translation_rules(english_mappings, chinese_mappings, rules_file)
        
        # 4. 加载规则文件
        rules = load_yaml_mappings(rules_file)
        print(f"\n[INFO] 加载到 {len(rules)} 条规则")
        for rule in rules:
            print(f"  - {rule['original']} -> {rule['translated']}")
        
        # 5. 应用翻译回写
        print(f"\n[TEST] 应用翻译回写")
        translated_content = apply_yaml_mapping(source_file, rules)
        
        # 6. 保存回写后的内容
        translated_file = os.path.join(temp_dir, "TestGame_translated.java")
        with open(translated_file, 'w', encoding='utf-8') as f:
            f.write(translated_content)
        
        print(f"\n[TEST] 回写后的文件: {translated_file}")
        print("回写内容:")
        print("-" * 40)
        with open(translated_file, 'r', encoding='utf-8') as f:
            print(f.read())
        print("-" * 40)
        
        # 7. 验证回写结果
        print(f"\n[VERIFY] 验证回写结果")
        with open(translated_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查翻译是否正确应用
        expected_translations = [
            ("Start Game", "开始游戏"),
            ("Exit Game", "退出游戏"),
            ("Settings", "设置")
        ]
        
        all_passed = True
        for original, expected in expected_translations:
            if expected in content:
                print(f"  ✓ '{original}' -> '{expected}' 翻译成功")
            else:
                print(f"  ✗ '{original}' -> '{expected}' 翻译失败")
                all_passed = False
        
        if all_passed:
            print(f"\n[SUCCESS] 单个文件翻译回写验证通过!")
        else:
            print(f"\n[ERROR] 单个文件翻译回写验证失败!")
        
        print("\n" + "=" * 60)
        print("          单个文件翻译回写测试完成")
        print("=" * 60)

# 测试批量文件翻译回写功能
def test_batch_mapping():
    """
    测试批量文件的翻译回写功能
    """
    print("\n" + "=" * 60)
    print("          测试批量文件翻译回写功能")
    print("=" * 60)
    
    # 创建测试数据
    with tempfile.TemporaryDirectory() as temp_dir:
        # 1. 创建多个测试源文件
        test_files = [
            {
                "name": "GameMenu.java",
                "content": '''
public class GameMenu {
    public void showMenu() {
        System.out.println("Start Game");
        System.out.println("Load Game");
        System.out.println("Exit Game");
    }
}
                '''
            },
            {
                "name": "Settings.java",
                "content": '''
public class Settings {
    public void showSettings() {
        System.out.println("Settings");
        System.out.println("Graphics");
        System.out.println("Audio");
        System.out.println("Controls");
    }
}
                '''
            },
            {
                "name": "Player.java",
                "content": '''
public class Player {
    public void displayStats() {
        System.out.println("Health: {0}");
        System.out.println("Score: {0}");
        System.out.println("Level: {0}");
    }
}
                '''
            },
            {
                "name": "Enemy.java",
                "content": '''
public class Enemy {
    public void attack() {
        System.out.println("Enemy Attack");
    }
    
    public void die() {
        System.out.println("Enemy Defeated");
    }
}
                '''
            }
        ]
        
        # 保存所有测试文件
        source_files = []
        for test_file in test_files:
            file_path = os.path.join(temp_dir, test_file["name"])
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(test_file["content"].strip())
            source_files.append(file_path)
        
        print(f"\n[INFO] 创建了 {len(source_files)} 个测试源文件:")
        for file_path in source_files:
            print(f"  - {file_path}")
        
        # 2. 创建双语映射数据（包含所有文件的字符串）
        english_mappings = [
            # GameMenu.java
            {
                "id": "GameMenu.java:3",
                "original": "Start Game",
                "context": "UI/GameMenu",
                "placeholders": []
            },
            {
                "id": "GameMenu.java:4",
                "original": "Load Game",
                "context": "UI/GameMenu",
                "placeholders": []
            },
            {
                "id": "GameMenu.java:5",
                "original": "Exit Game",
                "context": "UI/GameMenu",
                "placeholders": []
            },
            # Settings.java
            {
                "id": "Settings.java:3",
                "original": "Settings",
                "context": "UI/Settings",
                "placeholders": []
            },
            {
                "id": "Settings.java:4",
                "original": "Graphics",
                "context": "UI/Settings",
                "placeholders": []
            },
            {
                "id": "Settings.java:5",
                "original": "Audio",
                "context": "UI/Settings",
                "placeholders": []
            },
            {
                "id": "Settings.java:6",
                "original": "Controls",
                "context": "UI/Settings",
                "placeholders": []
            },
            # Enemy.java
            {
                "id": "Enemy.java:3",
                "original": "Enemy Attack",
                "context": "Game/Enemy",
                "placeholders": []
            },
            {
                "id": "Enemy.java:6",
                "original": "Enemy Defeated",
                "context": "Game/Enemy",
                "placeholders": []
            }
        ]
        
        chinese_mappings = [
            # GameMenu.java
            {
                "id": "GameMenu.java:3",
                "original": "开始游戏",
                "context": "UI/GameMenu",
                "placeholders": []
            },
            {
                "id": "GameMenu.java:4",
                "original": "加载游戏",
                "context": "UI/GameMenu",
                "placeholders": []
            },
            {
                "id": "GameMenu.java:5",
                "original": "退出游戏",
                "context": "UI/GameMenu",
                "placeholders": []
            },
            # Settings.java
            {
                "id": "Settings.java:3",
                "original": "设置",
                "context": "UI/Settings",
                "placeholders": []
            },
            {
                "id": "Settings.java:4",
                "original": "图形",
                "context": "UI/Settings",
                "placeholders": []
            },
            {
                "id": "Settings.java:5",
                "original": "音频",
                "context": "UI/Settings",
                "placeholders": []
            },
            {
                "id": "Settings.java:6",
                "original": "控制",
                "context": "UI/Settings",
                "placeholders": []
            },
            # Enemy.java
            {
                "id": "Enemy.java:3",
                "original": "敌人攻击",
                "context": "Game/Enemy",
                "placeholders": []
            },
            {
                "id": "Enemy.java:6",
                "original": "敌人被击败",
                "context": "Game/Enemy",
                "placeholders": []
            }
        ]
        
        # 3. 生成翻译规则
        rules_file = os.path.join(temp_dir, "rules.yaml")
        generate_translation_rules(english_mappings, chinese_mappings, rules_file)
        
        # 4. 加载规则文件
        rules = load_yaml_mappings(rules_file)
        print(f"\n[INFO] 加载到 {len(rules)} 条规则")
        print("翻译规则:")
        for rule in rules:
            print(f"  - {rule['original']} -> {rule['translated']}")
        
        # 5. 批量应用翻译回写（串行处理）
        print(f"\n[TEST] 串行应用翻译回写")
        translated_files_serial = []
        for source_file in source_files:
            print(f"  - 处理文件: {os.path.basename(source_file)}")
            translated_content = apply_yaml_mapping(source_file, rules)
            translated_file = os.path.join(temp_dir, f"{os.path.splitext(os.path.basename(source_file))[0]}_serial.java")
            with open(translated_file, 'w', encoding='utf-8') as f:
                f.write(translated_content)
            translated_files_serial.append(translated_file)
        
        # 6. 批量应用翻译回写（并行处理）
        print(f"\n[TEST] 并行应用翻译回写")
        translated_files_parallel = []
        
        def process_file(source_file, rules, temp_dir):
            """处理单个文件的翻译回写"""
            translated_content = apply_yaml_mapping(source_file, rules)
            translated_file = os.path.join(temp_dir, f"{os.path.splitext(os.path.basename(source_file))[0]}_parallel.java")
            with open(translated_file, 'w', encoding='utf-8') as f:
                f.write(translated_content)
            return translated_file
        
        # 使用线程池并行处理
        with ThreadPoolExecutor() as executor:
            # 提交所有任务
            futures = []
            for source_file in source_files:
                print(f"  - 提交任务: {os.path.basename(source_file)}")
                future = executor.submit(process_file, source_file, rules, temp_dir)
                futures.append(future)
            
            # 收集结果
            for future in futures:
                translated_files_parallel.append(future.result())
        
        # 7. 验证回写结果
        print(f"\n[VERIFY] 验证批量回写结果")
        
        # 定义预期的翻译映射
        expected_translations = {
            "Start Game": "开始游戏",
            "Load Game": "加载游戏",
            "Exit Game": "退出游戏",
            "Settings": "设置",
            "Graphics": "图形",
            "Audio": "音频",
            "Controls": "控制",
            "Enemy Attack": "敌人攻击",
            "Enemy Defeated": "敌人被击败"
        }
        
        # 验证所有文件
        all_files_passed = True
        
        def verify_file(file_path, file_type):
            """验证单个文件的翻译回写结果"""
            print(f"\n[VERIFY] 验证{file_type}文件: {os.path.basename(file_path)}")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_passed = True
            for original, expected in expected_translations.items():
                if original in content:
                    print(f"  ✗ '{original}' 未被翻译")
                    file_passed = False
                if expected in content:
                    print(f"  ✓ '{original}' -> '{expected}' 翻译成功")
            
            # 显示部分内容
            print(f"\n[CONTENT] {os.path.basename(file_path)} 部分内容:")
            print("-" * 40)
            lines = content.split('\n')
            for line in lines[:10]:  # 显示前10行
                print(line)
            if len(lines) > 10:
                print(f"... (共 {len(lines)} 行)")
            print("-" * 40)
            
            return file_passed
        
        # 验证串行处理的文件
        for file_path in translated_files_serial:
            if not verify_file(file_path, "串行处理"):
                all_files_passed = False
        
        # 验证并行处理的文件
        for file_path in translated_files_parallel:
            if not verify_file(file_path, "并行处理"):
                all_files_passed = False
        
        if all_files_passed:
            print(f"\n[SUCCESS] 所有批量文件翻译回写验证通过!")
            print(f"  - 测试文件数: {len(source_files)}")
            print(f"  - 串行处理文件: {len(translated_files_serial)}")
            print(f"  - 并行处理文件: {len(translated_files_parallel)}")
        else:
            print(f"\n[ERROR] 批量文件翻译回写验证失败!")
        
        print("\n" + "=" * 60)
        print("          批量文件翻译回写测试完成")
        print("=" * 60)

# 测试不同语言文件的翻译回写功能
def test_multi_language_mapping():
    """
    测试不同语言文件的翻译回写功能
    """
    print("\n" + "=" * 60)
    print("          测试不同语言文件翻译回写功能")
    print("=" * 60)
    
    # 创建测试数据
    with tempfile.TemporaryDirectory() as temp_dir:
        # 1. 创建不同语言的测试源文件
        test_files = [
            {
                "name": "Game.kt",
                "content": '''
class Game {
    fun start() {
        println("Start Game")
    }
    
    fun exit() {
        println("Exit Game")
    }
}
                '''
            },
            {
                "name": "app.js",
                "content": '''
function showMenu() {
    console.log("Start Game");
    console.log("Exit Game");
    console.log("Settings");
}
                '''
            },
            {
                "name": "app.py",
                "content": '''
def show_menu():
    print("Start Game")
    print("Exit Game")
    print("Settings")
                '''
            }
        ]
        
        # 保存所有测试文件
        source_files = []
        for test_file in test_files:
            file_path = os.path.join(temp_dir, test_file["name"])
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(test_file["content"].strip())
            source_files.append(file_path)
        
        print(f"\n[INFO] 创建了 {len(source_files)} 个不同语言的测试源文件:")
        for file_path in source_files:
            print(f"  - {file_path}")
        
        # 2. 创建双语映射数据
        english_mappings = [
            {
                "id": "Game.kt:3",
                "original": "Start Game",
                "context": "Game",
                "placeholders": []
            },
            {
                "id": "Game.kt:7",
                "original": "Exit Game",
                "context": "Game",
                "placeholders": []
            },
            {
                "id": "app.js:2",
                "original": "Start Game",
                "context": "JS",
                "placeholders": []
            },
            {
                "id": "app.js:3",
                "original": "Exit Game",
                "context": "JS",
                "placeholders": []
            },
            {
                "id": "app.js:4",
                "original": "Settings",
                "context": "JS",
                "placeholders": []
            },
            {
                "id": "app.py:2",
                "original": "Start Game",
                "context": "Python",
                "placeholders": []
            },
            {
                "id": "app.py:3",
                "original": "Exit Game",
                "context": "Python",
                "placeholders": []
            },
            {
                "id": "app.py:4",
                "original": "Settings",
                "context": "Python",
                "placeholders": []
            }
        ]
        
        chinese_mappings = [
            {
                "id": "Game.kt:3",
                "original": "开始游戏",
                "context": "Game",
                "placeholders": []
            },
            {
                "id": "Game.kt:7",
                "original": "退出游戏",
                "context": "Game",
                "placeholders": []
            },
            {
                "id": "app.js:2",
                "original": "开始游戏",
                "context": "JS",
                "placeholders": []
            },
            {
                "id": "app.js:3",
                "original": "退出游戏",
                "context": "JS",
                "placeholders": []
            },
            {
                "id": "app.js:4",
                "original": "设置",
                "context": "JS",
                "placeholders": []
            },
            {
                "id": "app.py:2",
                "original": "开始游戏",
                "context": "Python",
                "placeholders": []
            },
            {
                "id": "app.py:3",
                "original": "退出游戏",
                "context": "Python",
                "placeholders": []
            },
            {
                "id": "app.py:4",
                "original": "设置",
                "context": "Python",
                "placeholders": []
            }
        ]
        
        # 3. 生成翻译规则
        rules_file = os.path.join(temp_dir, "rules.yaml")
        generate_translation_rules(english_mappings, chinese_mappings, rules_file)
        
        # 4. 加载规则文件
        rules = load_yaml_mappings(rules_file)
        print(f"\n[INFO] 加载到 {len(rules)} 条规则")
        
        # 5. 应用翻译回写
        print(f"\n[TEST] 应用翻译回写")
        translated_files = []
        for source_file in source_files:
            print(f"  - 处理文件: {os.path.basename(source_file)}")
            translated_content = apply_yaml_mapping(source_file, rules)
            translated_file = os.path.join(temp_dir, f"{os.path.splitext(os.path.basename(source_file))[0]}_translated{os.path.splitext(source_file)[1]}")
            with open(translated_file, 'w', encoding='utf-8') as f:
                f.write(translated_content)
            translated_files.append(translated_file)
        
        # 6. 验证回写结果
        print(f"\n[VERIFY] 验证不同语言文件回写结果")
        all_passed = True
        
        # 定义预期的翻译映射
        expected_translations = {
            "Start Game": "开始游戏",
            "Exit Game": "退出游戏",
            "Settings": "设置"
        }
        
        for translated_file in translated_files:
            print(f"\n  - 验证文件: {os.path.basename(translated_file)}")
            with open(translated_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_passed = True
            for original, expected in expected_translations.items():
                if expected in content:
                    print(f"    ✓ '{original}' -> '{expected}' 翻译成功")
                elif original in content:
                    print(f"    ✗ '{original}' 未被翻译")
                    file_passed = False
            
            if not file_passed:
                all_passed = False
        
        if all_passed:
            print(f"\n[SUCCESS] 所有不同语言文件翻译回写验证通过!")
        else:
            print(f"\n[ERROR] 不同语言文件翻译回写验证失败!")
        
        print("\n" + "=" * 60)
        print("          不同语言文件翻译回写测试完成")
        print("=" * 60)

if __name__ == "__main__":
    # 运行所有测试
    test_single_file_mapping()
    test_batch_mapping()
    test_multi_language_mapping()
    
    print("\n" + "=" * 60)
    print("          所有翻译回写测试完成")
    print("=" * 60)
