# -*- coding: utf-8 -*-
"""
Tree-sitter AST解析和字符串提取工具

该模块包含使用Tree-sitter进行AST解析、字符串提取和上下文信息提取的功能。
支持Java和Kotlin语言。
"""

import os
import sys
from typing import List, Dict, Any, Optional, Iterator

# 添加虚拟环境的site-packages目录到Python搜索路径
# 获取当前文件的绝对路径
current_file_path = os.path.abspath(__file__)
# 计算虚拟环境的site-packages目录路径
# 路径结构：legacy/.venv/Lib/site-packages
venv_site_packages = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))),
    '.venv', 'Lib', 'site-packages'
)
sys.path.insert(0, venv_site_packages)
print(f"[DEBUG] 添加虚拟环境site-packages目录到Python搜索路径: {venv_site_packages}")
print(f"[DEBUG] 虚拟环境目录是否存在: {os.path.exists(venv_site_packages)}")

# 动态导入tree_sitter，避免导入错误
TREE_SITTER_AVAILABLE = False
tree_sitter = None
Language = None
Parser = None

# 尝试导入语言绑定包
tree_sitter_java = None
tree_sitter_kotlin = None

# 加载Tree-sitter语言
JAVA_LANGUAGE = None
KOTLIN_LANGUAGE = None

# 初始化状态跟踪
tree_sitter_initialized = False

# 模块级初始化，确保只执行一次
if not tree_sitter_initialized:
    try:
        import tree_sitter
        from tree_sitter import Language, Parser
        TREE_SITTER_AVAILABLE = True
        print("[OK] Tree-sitter库导入成功")
    except ImportError as e:
        print(f"[WARN] Tree-sitter库导入失败: {e}")
        print("[WARN] 将使用备用方案")

    # 尝试导入语言绑定包
    try:
        import tree_sitter_java
        print("[OK] tree_sitter_java库导入成功")
    except ImportError as e:
        print(f"[WARN] tree_sitter_java库导入失败: {e}")

    try:
        import tree_sitter_kotlin
        print("[OK] tree_sitter_kotlin库导入成功")
    except ImportError as e:
        print(f"[WARN] tree_sitter_kotlin库导入失败: {e}")

    tree_sitter_initialized = True

# 初始化标志位，防止重复初始化
_LANGUAGES_INITIALIZED = False


def initialize_languages():
    """
    初始化Tree-sitter语言解析器
    增强兼容性处理，支持多种Tree-sitter版本
    针对Tree-sitter 0.25.2版本优化，添加Windows支持
    """
    global JAVA_LANGUAGE, KOTLIN_LANGUAGE, _LANGUAGES_INITIALIZED
    
    print("[DEBUG] 开始初始化Tree-sitter语言解析器...")
    
    # 检查是否已经初始化过
    if _LANGUAGES_INITIALIZED:
        print("[DEBUG] Tree-sitter语言解析器已经初始化过，跳过初始化")
        return
    
    if not TREE_SITTER_AVAILABLE:
        print("[WARN] Tree-sitter库不可用，跳过语言解析器初始化")
        _LANGUAGES_INITIALIZED = True
        return
    
    # 初始化Java解析器
    JAVA_LANGUAGE = None
    try:
        print("[DEBUG]  开始初始化Java解析器...")
        print("[DEBUG]  尝试获取Java语言对象...")
        java_lang = tree_sitter_java.language()
        print(f"[DEBUG]  语言对象: {java_lang}")
        print(f"[DEBUG]  语言对象类型: {type(java_lang)}")
        
        # 方法1: 尝试直接使用Language构造函数包装PyCapsule (Tree-sitter 0.25.2+)
        try:
            print("[DEBUG]  方法1: 尝试直接使用Language构造函数包装PyCapsule...")
            JAVA_LANGUAGE = Language(java_lang)
            print("[DEBUG]  方法1成功: 成功转换为Language对象")
        except Exception as e1:
            print(f"[DEBUG]  方法1失败: {e1}")
            print(f"[DEBUG]  异常类型: {type(e1).__name__}")
            
            # 方法2: 尝试查找Tree-sitter模块中的转换函数
            try:
                print("[DEBUG]  方法2: 尝试查找Tree-sitter模块中的转换函数...")
                has_convert = hasattr(tree_sitter, '_convert_capsule_to_language')
                print(f"[DEBUG]  有_convert_capsule_to_language函数: {has_convert}")
                
                if has_convert:
                    print("[DEBUG]  调用_convert_capsule_to_language函数...")
                    JAVA_LANGUAGE = tree_sitter._convert_capsule_to_language(java_lang)
                    print("[DEBUG]  方法2成功: 成功使用转换函数")
                else:
                    # 方法3: 直接使用language对象，不转换 (兼容旧版Tree-sitter)
                    print("[DEBUG]  方法3: 尝试直接使用language对象...")
                    JAVA_LANGUAGE = java_lang
                    print("[DEBUG]  方法3成功: 直接使用language对象")
            except Exception as e2:
                print(f"[DEBUG]  方法2失败: {e2}")
                print(f"[DEBUG]  异常类型: {type(e2).__name__}")
                
                # 方法4: 尝试使用tree_sitter.Language.from_capsule (如果可用)
                try:
                    print("[DEBUG]  方法4: 尝试使用tree_sitter.Language.from_capsule...")
                    if hasattr(Language, 'from_capsule'):
                        JAVA_LANGUAGE = Language.from_capsule(java_lang)
                        print("[DEBUG]  方法4成功: 成功使用from_capsule方法")
                    else:
                        print("[DEBUG]  方法4失败: Language类没有from_capsule方法")
                except Exception as e3:
                    print(f"[DEBUG]  方法4失败: {e3}")
                    print(f"[DEBUG]  异常类型: {type(e3).__name__}")
    except Exception as e:
        print(f"[ERROR] Java解析器初始化失败: {e}")
        print(f"[ERROR] 异常类型: {type(e).__name__}")
        import traceback
        traceback.print_exc()
    
    # 初始化Kotlin解析器
    KOTLIN_LANGUAGE = None
    try:
        print("[DEBUG]  开始初始化Kotlin解析器...")
        print("[DEBUG]  尝试获取Kotlin语言对象...")
        kotlin_lang = tree_sitter_kotlin.language()
        print(f"[DEBUG]  语言对象: {kotlin_lang}")
        print(f"[DEBUG]  语言对象类型: {type(kotlin_lang)}")
        
        # 方法1: 尝试直接使用Language构造函数包装PyCapsule (Tree-sitter 0.25.2+)
        try:
            print("[DEBUG]  方法1: 尝试直接使用Language构造函数包装PyCapsule...")
            KOTLIN_LANGUAGE = Language(kotlin_lang)
            print("[DEBUG]  方法1成功: 成功转换为Language对象")
        except Exception as e1:
            print(f"[DEBUG]  方法1失败: {e1}")
            print(f"[DEBUG]  异常类型: {type(e1).__name__}")
            
            # 方法2: 尝试查找Tree-sitter模块中的转换函数
            try:
                print("[DEBUG]  方法2: 尝试查找Tree-sitter模块中的转换函数...")
                has_convert = hasattr(tree_sitter, '_convert_capsule_to_language')
                print(f"[DEBUG]  有_convert_capsule_to_language函数: {has_convert}")
                
                if has_convert:
                    print("[DEBUG]  调用_convert_capsule_to_language函数...")
                    KOTLIN_LANGUAGE = tree_sitter._convert_capsule_to_language(kotlin_lang)
                    print("[DEBUG]  方法2成功: 成功使用转换函数")
                else:
                    # 方法3: 直接使用language对象，不转换 (兼容旧版Tree-sitter)
                    print("[DEBUG]  方法3: 尝试直接使用language对象...")
                    KOTLIN_LANGUAGE = kotlin_lang
                    print("[DEBUG]  方法3成功: 直接使用language对象")
            except Exception as e2:
                print(f"[DEBUG]  方法2失败: {e2}")
                print(f"[DEBUG]  异常类型: {type(e2).__name__}")
                
                # 方法4: 尝试使用tree_sitter.Language.from_capsule (如果可用)
                try:
                    print("[DEBUG]  方法4: 尝试使用tree_sitter.Language.from_capsule...")
                    if hasattr(Language, 'from_capsule'):
                        KOTLIN_LANGUAGE = Language.from_capsule(kotlin_lang)
                        print("[DEBUG]  方法4成功: 成功使用from_capsule方法")
                    else:
                        print("[DEBUG]  方法4失败: Language类没有from_capsule方法")
                except Exception as e3:
                    print(f"[DEBUG]  方法4失败: {e3}")
                    print(f"[DEBUG]  异常类型: {type(e3).__name__}")
    except Exception as e:
        print(f"[ERROR] Kotlin解析器初始化失败: {e}")
        print(f"[ERROR] 异常类型: {type(e).__name__}")
        import traceback
        traceback.print_exc()
    
    # 打印初始化结果
    print("[DEBUG]  初始化结果:")
    print(f"[DEBUG]  Java语言对象: {JAVA_LANGUAGE}")
    print(f"[DEBUG]  Java语言对象类型: {type(JAVA_LANGUAGE) if JAVA_LANGUAGE else 'None'}")
    print(f"[DEBUG]  Kotlin语言对象: {KOTLIN_LANGUAGE}")
    print(f"[DEBUG]  Kotlin语言对象类型: {type(KOTLIN_LANGUAGE) if KOTLIN_LANGUAGE else 'None'}")
    
    # 根据初始化结果输出信息
    if JAVA_LANGUAGE and KOTLIN_LANGUAGE:
        print("[OK] 成功加载Java和Kotlin语言解析器")
    elif JAVA_LANGUAGE:
        print("[OK] 成功加载Java语言解析器，Kotlin解析器加载失败")
    elif KOTLIN_LANGUAGE:
        print("[OK] 成功加载Kotlin语言解析器，Java解析器加载失败")
    else:
        print("[WARN] 无法加载Tree-sitter语言解析器")
        print("[NOTE] 可以尝试安装最新版本的tree_sitter_java和tree_sitter_kotlin包")
    
    # 设置初始化完成标志位
    _LANGUAGES_INITIALIZED = True
    print("[DEBUG] Tree-sitter语言解析器初始化完成")


class ASTNode:
    """
    AST节点封装类
    """
    def __init__(self, node: tree_sitter.Node, file_path: str):
        self.node = node
        self.file_path = file_path
    
    @property
    def type(self) -> str:
        """获取节点类型"""
        return self.node.type
    
    @property
    def text(self) -> str:
        """获取节点文本"""
        try:
            return self.node.text.decode('utf-8')
        except UnicodeDecodeError:
            # 尝试使用gbk编码，处理中文文件常见编码问题
            return self.node.text.decode('gbk')
        except UnicodeDecodeError:
            # 最后尝试使用replace模式，避免程序崩溃
            return self.node.text.decode('utf-8', errors='replace')
    
    @property
    def start_line(self) -> int:
        """获取节点起始行号(1-based)"""
        return self.node.start_point[0] + 1
    
    @property
    def end_line(self) -> int:
        """获取节点结束行号(1-based)"""
        return self.node.end_point[0] + 1
    
    @property
    def start_column(self) -> int:
        """获取节点起始列号"""
        return self.node.start_point[1]
    
    @property
    def end_column(self) -> int:
        """获取节点结束列号"""
        return self.node.end_point[1]
    
    def get_parent_types(self) -> List[str]:
        """
        获取父节点类型列表
        
        Returns:
            List[str]: 父节点类型列表，从直接父节点开始向上
        """
        parent_types = []
        current = self.node.parent
        while current:
            parent_types.append(current.type)
            current = current.parent
        return parent_types
    
    def get_context_metadata(self) -> Dict[str, Any]:
        """
        获取节点上下文元数据
        
        Returns:
            Dict[str, Any]: 上下文元数据，包含父节点类型和节点类型
        """
        return {
            "parent_types": self.get_parent_types(),
            "node_type": self.type
        }


def get_parser(file_path: str) -> Optional[Parser]:
    """
    根据文件扩展名获取相应的Tree-sitter解析器
    支持不同Tree-sitter版本，使用兼容的API
    
    Args:
        file_path: 文件路径
    
    Returns:
        Optional[Parser]: Tree-sitter解析器，如果不支持该文件类型则返回None
    """
    if JAVA_LANGUAGE is None or KOTLIN_LANGUAGE is None:
        initialize_languages()
    
    parser = Parser()
    
    try:
        if file_path.endswith('.java'):
            if JAVA_LANGUAGE:
                # 尝试使用属性方式设置语言(Tree-sitter 0.25.2+)
                try:
                    parser.language = JAVA_LANGUAGE
                    return parser
                except AttributeError:
                    # 尝试使用set_language方法(旧版Tree-sitter)
                    try:
                        parser.set_language(JAVA_LANGUAGE)
                        return parser
                    except AttributeError:
                        print(f"[WARN]  无法设置Java语言解析器，API不兼容")
                        return None
        elif file_path.endswith(('.kt', '.kts')):
            if KOTLIN_LANGUAGE:
                # 尝试使用属性方式设置语言(Tree-sitter 0.25.2+)
                try:
                    parser.language = KOTLIN_LANGUAGE
                    return parser
                except AttributeError:
                    # 尝试使用set_language方法(旧版Tree-sitter)
                    try:
                        parser.set_language(KOTLIN_LANGUAGE)
                        return parser
                    except AttributeError:
                        print(f"[WARN]  无法设置Kotlin语言解析器，API不兼容")
                        return None
    except Exception as e:
        print(f"[WARN]  创建解析器失败: {e}")
        return None
    
    return None


def _extract_strings_from_single_file(file_path: str, root_dir: str = None) -> List[Dict[str, Any]]:
    """
    从单个文件中提取字符串
    
    Args:
        file_path: 文件路径
        root_dir: 根目录路径，用于计算相对路径
    
    Returns:
        List[Dict[str, Any]]: 提取的字符串列表
    """
    # 获取解析器
    parser = get_parser(file_path)
    if not parser:
        return []
    
    # 读取文件内容
    try:
        with open(file_path, 'rb') as f:
            code = f.read()
    except Exception as e:
        print(f"[WARN]  读取文件失败: {file_path} - {e}")
        return []
    
    # 解析代码生成AST
    try:
        tree = parser.parse(code)
    except Exception as e:
        print(f"[WARN]  解析文件失败: {file_path} - {e}")
        return []
    
    # 遍历AST，提取字符串节点
    return extract_strings_from_ast(tree, file_path, root_dir)


def extract_ast_mappings(root_dir: str, use_parallel: bool = False, max_workers: int = None, use_cache: bool = True) -> Iterator[Dict[str, Any]]:
    """
    从指定根目录提取AST映射，使用生成器优化内存使用
    
    Args:
        root_dir: 根目录路径
        use_parallel: 是否使用并行处理
        max_workers: 最大工作线程数
        use_cache: 是否使用缓存机制，支持增量更新
    
    Yields:
        Dict[str, Any]: AST映射
    """
    from .parallel_utils import get_all_source_files, ParallelProcessor
    from .cache_utils import FileCacheManager
    
    # 获取所有需要处理的文件
    file_extensions = ['.java', '.kt', '.kts', '.py']
    all_files = get_all_source_files(root_dir, file_extensions)
    
    # 需要处理的文件列表
    files_to_process = all_files
    
    # 缓存管理器
    cache_manager = None
    
    if use_cache:
        # 初始化缓存管理器
        cache_manager = FileCacheManager()
        
        # 获取已变更的文件
        files_to_process = cache_manager.get_changed_files(all_files)
        
        if files_to_process:
            print(f"[INFO] 检测到 {len(files_to_process)} 个文件已变更，开始处理")
            print(f"[INFO] 跳过 {len(all_files) - len(files_to_process)} 个未变更文件")
        else:
            print(f"[INFO] 没有检测到已变更文件，跳过处理")
            return
    
    if use_parallel and len(files_to_process) > 1:
        # 使用并行处理
        processor = ParallelProcessor(max_workers=max_workers, use_multiprocessing=False)
        results = processor.process_files(files_to_process, _extract_strings_from_single_file, root_dir)
        
        # 输出并行处理结果
        print(f"[INFO] 并行处理完成: 成功 {len(results['success'])} 个文件, 失败 {len(results['failed'])} 个文件, 耗时 {results['time']:.2f} 秒")
        
        # 逐个返回所有结果并更新缓存
        for result in results['success']:
            file_path = result['file']
            yield from result['result']
            
            # 更新缓存
            if use_cache and cache_manager:
                cache_manager.update_file_cache(file_path, {
                    'processed': True,
                    'strings_extracted': len(result['result'])
                })
    else:
        # 顺序处理
        for file_path in files_to_process:
            strings = _extract_strings_from_single_file(file_path, root_dir)
            yield from strings
            
            # 更新缓存
            if use_cache and cache_manager:
                cache_manager.update_file_cache(file_path, {
                    'processed': True,
                    'strings_extracted': len(strings)
                })
    
    if use_cache and cache_manager:
        # 输出缓存统计信息
        stats = cache_manager.get_cache_statistics()
        print(f"[INFO] 缓存统计: 总文件 {stats['total_files']}, 缓存大小 {stats['total_size_mb']:.2f} MB")


import re
import hashlib
import json

def generate_ast_signature(node: ASTNode) -> str:
    """
    生成稳定的AST签名，包含节点上下文信息和语法结构
    
    Args:
        node: AST节点对象
    
    Returns:
        str: 稳定的AST签名
    """
    # 获取节点的上下文元数据
    context = node.get_context_metadata()
    
    # 生成AST签名，包含父节点类型、节点类型和位置信息
    signature_parts = [
        # 父节点类型链，最多取3层
        ','.join(context['parent_types'][:3]),
        # 节点类型
        context['node_type'],
        # 节点在文件中的相对位置（行号差，而非绝对行号）
        f"{node.start_line % 100}:{node.start_column}"
    ]
    
    return '|'.join(signature_parts)

def generate_occurrence_key(rel_path: str, ast_signature: str, literal_kind: str) -> str:
    """
    生成稳定的occurrence_key
    
    Args:
        rel_path: 相对文件路径
        ast_signature: AST签名
        literal_kind: 字面量类型
    
    Returns:
        str: 稳定的occurrence_key
    """
    # 使用可移植的路径分隔符
    rel_path = rel_path.replace('\\', '/')
    
    # 生成哈希值
    hash_input = f"{rel_path}|{ast_signature}|{literal_kind}"
    return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

def _should_filter_string(text: str) -> bool:
    """
    判断是否应该过滤字符串
    
    Args:
        text: 要判断的字符串
    
    Returns:
        bool: True表示应该过滤，False表示应该保留
    """
    # 过滤空字符串
    if not text:
        return True
    
    # 过滤过短的字符串(长度小于2，除非是特殊字符'%'和'+')
    if len(text) < 2 and text not in ['%', '+']:
        return True
    
    # 通用标识符过滤(包含$开头和普通标识符)
    if re.match(r'^\$?[a-zA-Z0-9_]+$', text):
        return True
    
    # 过滤纯地址或者文件名的字符串
    # 匹配规则：
    # 1. 相对路径：以目录名开头，包含多个/或\分隔的目录，以文件名结尾
    # 2. 绝对路径：以字母开头，包含多个/或\分隔的目录，以文件名结尾
    # 3. 直接以文件名结尾，包含特定扩展名
    is_path = re.match(r'^([a-zA-Z]:?[/\\]|[^/\\\s]+[/\\])[^/\\\s]+([/\\][^/\\\s]+)*$', text) is not None
    is_config_file = re.match(r'^[^/\\]+\.(ini|xml|cfg|json|txt|yaml|yml)$', text) is not None
    # 额外检查：如果包含/且不包含空格，并且路径中至少有一个/，可能是路径
    is_likely_path = '/' in text and ' ' not in text and text.count('/') >= 1 and not re.search(r'[A-Z]', text) and not re.search(r'[^a-zA-Z0-9_./\\-]', text)
    if is_path or is_config_file or is_likely_path:
        return True
    
    # 过滤格式字符串相关
    if text in ['%', '%s', ' sec', 'Level: ', 'DIR: ', 'placeholder_1', 'placeholder_2', 'sec', 'secs', 'second', 'seconds']:
        return True
    
    # 过滤以example_开头的示例技能和属性名
    if text.startswith('example_'):
        return True
    
    # 过滤UI相关标识符
    if 'icon_' in text or 'ui' in text.lower() or 'UI' in text:
        return True
    
    # 过滤配置和设置项
    config_items = ['noDeployCRPercent', 'cr_effect', 'deployCR', 'maxCR', 'minCR', 'cr', 'CR', 'dp', 'DP', 'deployPoints', 'deploy_points']
    if text in config_items:
        return True
    
    # 过滤注释中常见的调试字符串
    debug_strings = ['wefwefwefwefe', 'efwefwefwefe', 'wefwefe', 'test', 'debug', 'DEBUG', 'Test', 'TEST']
    if text in debug_strings:
        return True
    
    # 过滤数值相关字符串
    if re.match(r'^\d+(\.\d+)?$', text):
        return True
    
    # 过滤仅包含特殊字符的字符串（排除%和+）
    if text not in ['%', '+'] and re.match(r'^[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>/?~`]+$', text):
        return True
    
    return False


def extract_strings_from_ast(tree: tree_sitter.Tree, file_path: str, root_dir: str = None) -> List[Dict[str, Any]]:
    """
    从AST中提取字符串节点
    
    Args:
        tree: AST树
        file_path: 文件路径
        root_dir: 根目录路径，用于计算相对路径
    
    Returns:
        List[Dict[str, Any]]: 提取的字符串列表
    """
    extracted_strings = []
    cursor = tree.walk()
    
    # 遍历AST的所有节点
    while True:
        if cursor.node.type in ['string_literal', 'interpolated_string_expression', 'string_template_expression']:
            # 创建ASTNode对象
            ast_node = ASTNode(cursor.node, file_path)
            
            # 提取字符串内容，去除引号
            text = ast_node.text
            if text.startswith('"') and text.endswith('"'):
                text = text[1:-1]
            elif text.startswith("'") and text.endswith("'"):
                text = text[1:-1]
            
            # 过滤不需要的字符串类型
            if _should_filter_string(text):
                # 跳过不需要的字符串
                pass
            else:
                # 提取上下文元数据
                context = ast_node.get_context_metadata()
                
                # 生成AST签名
                ast_signature = generate_ast_signature(ast_node)
                
                # 确定字面量类型
                literal_kind = cursor.node.type
                
                # 计算相对路径
                rel_path = file_path
                if root_dir:
                    rel_path = os.path.relpath(file_path, root_dir)
                    # 转换为可移植的路径分隔符
                    rel_path = rel_path.replace('\\', '/')
                
                # 生成稳定的occurrence_key
                occurrence_key = generate_occurrence_key(rel_path, ast_signature, literal_kind)
                
                # 获取节点的字节范围
                start_byte = cursor.node.start_byte
                end_byte = cursor.node.end_byte
                
                # 添加到提取结果
                extracted_strings.append({
                    "id": occurrence_key,
                    "original": text,
                    "meta": {
                        "file": file_path,
                        "rel_path": rel_path,
                        "line": ast_node.start_line,
                        "column": ast_node.start_column,
                        "end_line": ast_node.end_line,
                        "end_column": ast_node.end_column,
                        "start_byte": start_byte,
                        "end_byte": end_byte,
                        "ast_signature": ast_signature,
                        "literal_kind": literal_kind
                    },
                    "context": context
                })
        
        # 继续遍历
        if cursor.goto_first_child():
            continue
        while True:
            if cursor.goto_next_sibling():
                break
            if not cursor.goto_parent():
                return extracted_strings
    
    return extracted_strings


def extract_strings_from_file(file_path: str, root_dir: str = None) -> List[Dict[str, Any]]:
    """
    从单个文件中提取字符串
    
    Args:
        file_path: 文件路径
        root_dir: 根目录路径，用于计算相对路径
    
    Returns:
        List[Dict[str, Any]]: 提取的字符串列表
    """
    # 获取解析器
    parser = get_parser(file_path)
    if not parser:
        return []
    
    # 读取文件内容
    try:
        with open(file_path, 'rb') as f:
            code = f.read()
    except Exception as e:
        print(f"[WARN]  读取文件失败: {file_path} - {e}")
        return []
    
    # 解析代码生成AST
    try:
        tree = parser.parse(code)
    except Exception as e:
        print(f"[WARN]  解析文件失败: {file_path} - {e}")
        return []
    
    # 提取字符串
    strings = extract_strings_from_ast(tree, file_path, root_dir)
    
    # 为每个字符串添加原始字面量（包含引号）
    for string in strings:
        # 从文件中提取原始字面量（包含引号）
        start_byte = string["meta"]["start_byte"]
        end_byte = string["meta"]["end_byte"]
        original_literal = code[start_byte:end_byte].decode('utf-8')
        string["meta"]["literal"] = original_literal
    
    return strings

# 注意：不再在模块级别自动初始化，而是在需要时手动调用