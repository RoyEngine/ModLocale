#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具集成模块，封装ast-grep和jq工具的调用

该模块提供了统一的API接口，用于调用ast-grep和jq工具，处理字符串提取和解析任务。
当Tree-sitter初始化失败时，将作为备用工具链使用。
"""

import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


class ToolsIntegrator:
    """
    工具集成类，封装ast-grep和jq工具的调用

    属性:
        ast_grep_path: Path - ast-grep工具路径
        jq_path: Path - jq工具路径
        supported_languages: List[str] - 支持的语言列表
    """

    def __init__(self, base_path: Optional[str] = None):
        """
        初始化工具集成类

        参数:
            base_path: Optional[str] - 基础路径，用于查找工具
        """
        self.base_path = Path(base_path or os.getcwd())
        self.ast_grep_path = self._find_tool(
            "ast-grep", ["ast-grep.exe", "sg.exe"]
        )
        self.jq_path = self._find_tool("jq", ["jq-win64.exe"])
        self.supported_languages = ["java", "kotlin"]

    def _find_tool(self, tool_name: str, possible_names: List[str]) -> Optional[Path]:
        """
        查找工具路径

        参数:
            tool_name: str - 工具名称
            possible_names: List[str] - 可能的工具文件名列表

        返回:
            Optional[Path] - 工具路径，如果未找到则返回None
        """
        # 首先查找tools目录下的工具
        tools_dir = self.base_path / "tools" / tool_name
        for name in possible_names:
            tool_path = tools_dir / name
            if tool_path.exists():
                logger.info(f"OK 找到{tool_name}工具: {tool_path}")
                return tool_path

        # 然后查找系统PATH中的工具
        for name in possible_names:
            try:
                subprocess.run(
                    [name, "--version"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                logger.info(f"OK 在系统PATH中找到{tool_name}工具: {name}")
                return Path(name)
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue

        logger.warning(f"[ERROR] 未找到{tool_name}工具")
        return None

    def is_ast_grep_available(self) -> bool:
        """
        检查ast-grep工具是否可用

        返回:
            bool - ast-grep工具是否可用
        """
        return self.ast_grep_path is not None

    def is_jq_available(self) -> bool:
        """
        检查jq工具是否可用

        返回:
            bool - jq工具是否可用
        """
        return self.jq_path is not None

    def get_tool_status_report(self) -> Dict[str, Any]:
        """
        获取工具状态报告

        返回:
            Dict[str, Any] - 工具状态报告
        """
        return {
            "ast_grep": {
                "available": self.is_ast_grep_available(),
                "path": str(self.ast_grep_path) if self.ast_grep_path else None,
                "version": self.get_ast_grep_version()
            },
            "jq": {
                "available": self.is_jq_available(),
                "path": str(self.jq_path) if self.jq_path else None,
                "version": self.get_jq_version()
            },
            "base_path": str(self.base_path),
            "supported_languages": self.supported_languages,
        }

    def get_ast_grep_version(self) -> Optional[str]:
        """
        获取ast-grep工具版本

        返回:
            Optional[str] - ast-grep工具版本，如果工具不可用则返回None
        """
        if not self.is_ast_grep_available():
            return None

        try:
            result = subprocess.run(
                [str(self.ast_grep_path), "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"[ERROR] 获取ast-grep版本失败: {e}")
            return None

    def get_jq_version(self) -> Optional[str]:
        """
        获取jq工具版本

        返回:
            Optional[str] - jq工具版本，如果工具不可用则返回None
        """
        if not self.is_jq_available():
            return None

        try:
            result = subprocess.run(
                [str(self.jq_path), "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"[ERROR] 获取jq版本失败: {e}")
            return None

    def _parse_ast_grep_line(self, line: str) -> Optional[Dict[str, Any]]:
        """
        解析ast-grep输出的单行JSON

        参数:
            line: str - JSON行

        返回:
            Optional[Dict[str, Any]] - 解析后的字符串信息，如果解析失败则返回None
        """
        try:
            match = json.loads(line)
            # 提取字符串内容
            string_content = match.get("matches", [{}])[0].get("node", {}).get("text", "")
            if string_content:
                # 去除引号
                if string_content.startswith('"') and string_content.endswith('"'):
                    actual_content = string_content[1:-1]
                else:
                    actual_content = string_content
                return {
                    "content": actual_content,
                    "line_number": match.get("range", {}).get("start", {}).get("line", 0),
                    "context": match.get("context", {}).get("text", "").strip()
                }
        except json.JSONDecodeError as e:
            logger.error(f"[ERROR] 解析ast-grep输出失败: {e}")
        return None

    def _run_ast_grep_command(self, file_path: str, language: str) -> Optional[str]:
        """
        运行ast-grep命令并返回输出

        参数:
            file_path: str - 文件路径
            language: str - 语言类型

        返回:
            Optional[str] - 命令输出，如果失败则返回None
        """
        try:
            # 构建ast-grep命令
            command = [
                str(self.ast_grep_path),
                "--lang",
                language,
                "--pattern",
                '"$STR"',
                "--json",
                file_path,
            ]

            logger.debug(f"执行ast-grep命令: {' '.join(command)}")
            # 执行命令
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"[ERROR] 执行ast-grep命令失败: {e}")
            logger.error(f"错误输出: {e.stderr}")
        except Exception as e:
            logger.error(f"[ERROR] 提取字符串失败: {e}")
        return None

    def extract_strings_with_ast_grep(self, file_path: str, language: str) -> List[Dict[str, Any]]:
        """
        使用ast-grep从文件中提取字符串

        参数:
            file_path: str - 文件路径
            language: str - 语言类型 (java或kotlin)

        返回:
            List[Dict[str, Any]] - 提取的字符串列表
        """
        if not self.is_ast_grep_available():
            logger.error("[ERROR] ast-grep工具不可用, 无法提取字符串")
            return []

        if language not in self.supported_languages:
            logger.error(f"[ERROR] 不支持的语言: {language}")
            return []

        # 运行ast-grep命令
        output = self._run_ast_grep_command(file_path, language)
        if not output:
            return []

        # 解析输出
        extracted_strings = []
        for line in output.splitlines():
            string_info = self._parse_ast_grep_line(line)
            if string_info:
                extracted_strings.append(string_info)

        logger.info(f"OK 使用ast-grep成功提取{len(extracted_strings)}个字符串")
        return extracted_strings

    def process_json_with_jq(self, json_data: str, jq_filter: str) -> Optional[str]:
        """
        使用jq处理JSON数据

        参数:
            json_data: str - JSON数据
            jq_filter: str - jq过滤表达式

        返回:
            Optional[str] - 处理后的JSON数据，如果处理失败则返回None
        """
        if not self.is_jq_available():
            logger.error("[ERROR] jq工具不可用, 无法处理JSON数据")
            return None

        try:
            # 执行jq命令
            logger.debug(f"执行jq命令, 过滤器: {jq_filter}")
            result = subprocess.run(
                [str(self.jq_path), jq_filter],
                input=json_data,
                capture_output=True,
                text=True,
                check=True,
            )

            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"[ERROR] 执行jq命令失败: {e}")
            logger.error(f"错误输出: {e.stderr}")
            return None
        except Exception as e:
            logger.error(f"[ERROR] 处理JSON数据失败: {e}")
            return None

    def extract_strings_from_directory(self, directory: str, language: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        从目录中提取所有支持的文件的字符串

        参数:
            directory: str - 目录路径
            language: str - 语言类型 (java或kotlin)

        返回:
            Dict[str, List[Dict[str, Any]]] - 提取的字符串信息, 键为文件路径, 值为字符串列表
        """
        if not self.is_ast_grep_available():
            logger.error("[ERROR] ast-grep工具不可用, 无法提取字符串")
            return {}

        directory_path = Path(directory)
        if not directory_path.exists():
            logger.error(f"[ERROR] 目录不存在: {directory}")
            return {}

        # 获取所有支持的文件
        supported_extensions = {"java": [".java"], "kotlin": [".kt", ".kts"]}

        extensions = supported_extensions.get(language, [])
        if not extensions:
            logger.error(f"[ERROR] 不支持的语言: {language}")
            return {}

        result = {}
        for ext in extensions:
            for file_path in directory_path.rglob(f"*{ext}"):
                logger.info(f"[SEARCH] 处理文件: {file_path}")
                strings = self.extract_strings_with_ast_grep(str(file_path), language)
                if strings:
                    result[str(file_path)] = strings

        logger.info(f"OK 从目录{directory}中提取了{len(result)}个文件的字符串")
        return result


# 测试代码
if __name__ == "__main__":
    # 初始化工具集成器
    integrator = ToolsIntegrator()

    # 打印工具状态
    logger.info(f"\nast-grep可用: {integrator.is_ast_grep_available()}")
    logger.info(f"jq可用: {integrator.is_jq_available()}")

    if integrator.is_ast_grep_available():
        logger.info(f"ast-grep版本: {integrator.get_ast_grep_version()}")

    if integrator.is_jq_available():
        logger.info(f"jq版本: {integrator.get_jq_version()}")

    # 测试字符串提取
    logger.info("\n测试字符串提取...")
    # 这里可以添加测试代码, 例如:
    # test_file = "test.java"
    # if Path(test_file).exists():
    #     strings = integrator.extract_strings_with_ast_grep(test_file, "java")
    #     logger.info(f"提取到{len(strings)}个字符串")
    #     for s in strings:
    #         logger.info(f"  第{s['line_number']}行: {s['content']}")
