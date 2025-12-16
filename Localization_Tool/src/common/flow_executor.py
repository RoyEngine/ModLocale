#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
流程执行器模块

提供统一的流程执行框架，用于协调和管理所有功能模块的执行流程。该模块：
- 提供统一的流程配置和结果处理
- 管理报告生成和日志记录
- 处理通用的流程执行逻辑
- 支持灵活的流程配置
- 实现了清晰的模块间通信机制

所有功能模块（Extract、Extend、Decompile）都应通过该框架执行，确保执行流程的一致性和可维护性
"""

import os
import sys
from typing import Any, Callable, Dict, List, Optional, TypeVar, Generic
from dataclasses import dataclass

from src.common import (
    create_folders, generate_report, save_report,
    get_timestamp, rename_mod_folders, restore_backup,
    setup_logger, get_logger, log_progress, log_result
)
from src.common.config_utils import get_directory, get_source_directory, get_backup_directory

# 设置日志记录器
logger = setup_logger("flow_executor")

# 定义泛型类型变量
T = TypeVar('T')

@dataclass
class FlowConfig:
    """流程配置类"""
    mode: str
    sub_flow: str
    base_path: str
    require_report: bool = True

@dataclass
class FlowResult(Generic[T]):
    """流程结果类"""
    status: str
    data: T
    message: str
    output_path: str = ""
    error_details: Optional[str] = None

class FlowExecutor:
    """流程执行器"""
    
    def __init__(self, config: FlowConfig):
        """
        初始化流程执行器
        
        Args:
            config: 流程配置
        """
        self.config = config
        self.timestamp = get_timestamp()
        self.process_id = f"{self.timestamp}_{self.config.mode.lower()}_{self.config.sub_flow.lower().replace(' ', '_')}"
        self.logger = get_logger(f"flow_executor.{self.config.mode.lower()}")
        
        # 初始化报告
        self.report = generate_report(
            process_id=self.process_id,
            mode=self.config.mode,
            sub_flow=self.config.sub_flow,
            status="running",
            data={
                "total_count": 0,
                "success_count": 0,
                "fail_count": 0,
                "fail_reasons": [],
            },
        )
    
    def validate_input(self, validator: Callable[[], bool]) -> bool:
        """
        验证输入
        
        Args:
            validator: 验证函数
            
        Returns:
            bool: 验证结果
        """
        try:
            self.logger.info("开始验证输入")
            result = validator()
            if result:
                self.logger.info("输入验证通过")
            else:
                self.logger.error("输入验证失败")
            return result
        except Exception as e:
            self.logger.error(f"输入验证时发生错误: {str(e)}")
            self._update_report_status("fail", [f"输入验证失败: {str(e)}"])
            return False
    

    

    
    def execute_flow(self, flow_func: Callable[[], FlowResult]) -> FlowResult:
        """
        执行流程
        
        Args:
            flow_func: 流程函数
            
        Returns:
            FlowResult: 流程结果
        """
        try:
            self.logger.info(f"开始执行{self.config.mode}模式的{self.config.sub_flow}流程")
            
            # 执行核心流程
            result = flow_func()
            
            # 更新报告
            self._update_report_status(result.status, result.data.get("fail_reasons", []))
            
            return result
        except Exception as e:
            self.logger.error(f"执行流程时发生错误: {str(e)}")
            self._update_report_status("fail", [f"执行流程失败: {str(e)}"])
            return FlowResult(
                status="fail",
                data={},
                message=f"执行流程失败: {str(e)}",
                error_details=str(e)
            )
    
    def _update_report_status(self, status: str, fail_reasons: List[str]) -> None:
        """
        更新报告状态
        
        Args:
            status: 状态
            fail_reasons: 失败原因列表
        """
        self.report["status"] = status
        if fail_reasons:
            self.report["data"]["fail_reasons"] = fail_reasons
            self.report["data"]["fail_count"] = len(fail_reasons)
    
    def save_flow_report(self, result: FlowResult) -> None:
        """
        保存流程报告
        
        Args:
            result: 流程结果
        """
        if not self.config.require_report:
            return
        
        try:
            self.logger.info("开始保存流程报告")
            
            # 更新报告数据
            self.report["data"].update(result.data)
            
            # 添加output_path到报告
            if result.output_path:
                self.report["output_path"] = result.output_path
                
                # 保存报告到输出路径
                save_report(
                    self.report, 
                    result.output_path, 
                    self.timestamp, 
                    rule_type="regular", 
                    mod_name=os.path.basename(result.output_path)
                )
            
            self.logger.info("流程报告保存完成")
        except Exception as e:
            self.logger.error(f"保存流程报告时发生错误: {str(e)}")
    
    def run(self, flow_func: Callable[[], FlowResult]) -> Dict[str, Any]:
        """
        运行完整流程
        
        Args:
            flow_func: 流程函数
            
        Returns:
            Dict[str, Any]: 执行结果
        """
        try:
            self.logger.info(f"开始运行完整流程: {self.config.mode} - {self.config.sub_flow}")
            
            # 执行流程
            result = self.execute_flow(flow_func)
            
            # 保存报告
            self.save_flow_report(result)
            
            # 构建最终结果
            final_result = {
                "status": result.status,
                "data": result.data,
                "mode": self.config.mode,
                "output_path": result.output_path
            }
            
            self.logger.info(f"流程运行完成，状态: {result.status}")
            return final_result
        except Exception as e:
            self.logger.error(f"运行完整流程时发生错误: {str(e)}")
            return {
                "status": "fail",
                "data": {
                    "total_count": 0,
                    "success_count": 0,
                    "fail_count": 1,
                    "fail_reasons": [f"运行流程失败: {str(e)}"],
                },
                "mode": self.config.mode,
                "output_path": ""
            }

class FlowManager:
    """流程管理器类"""
    
    @staticmethod
    def create_executor(mode: str, sub_flow: str, base_path: str, **kwargs) -> FlowExecutor:
        """
        创建流程执行器
        
        Args:
            mode: 模式名称
            sub_flow: 子流程名称
            base_path: 基础路径
            **kwargs: 其他配置参数
            
        Returns:
            FlowExecutor: 流程执行器实例
        """
        config = FlowConfig(
            mode=mode,
            sub_flow=sub_flow,
            base_path=base_path,
            require_report=kwargs.get("require_report", True)
        )
        return FlowExecutor(config)
    
    @staticmethod
    def execute_flow(
        mode: str, 
        sub_flow: str, 
        base_path: str, 
        flow_func: Callable[[], FlowResult],
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行流程(静态方法)
        
        Args:
            mode: 模式名称
            sub_flow: 子流程名称
            base_path: 基础路径
            flow_func: 流程函数
            **kwargs: 其他配置参数
            
        Returns:
            Dict[str, Any]: 执行结果
        """
        executor = FlowManager.create_executor(mode, sub_flow, base_path, **kwargs)
        return executor.run(flow_func)

# 添加到__all__
__all__ = [
    "FlowConfig",
    "FlowResult",
    "FlowExecutor",
    "FlowManager"
]