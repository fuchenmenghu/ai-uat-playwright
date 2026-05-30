from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FailureDef:
    failure_type: str
    template: str


ERROR_CATALOG: dict[str, FailureDef] = {
    "ENV_001": FailureDef("环境与依赖类", "配置文件缺失：未找到配置文件 {config_path}。"),
    "ENV_002": FailureDef("环境与依赖类", "配置项缺失：缺少配置项 {config_key}。"),
    "ENV_003": FailureDef("环境与依赖类", "依赖包缺失：缺少依赖 {package_name}。"),
    "ENV_004": FailureDef("环境与依赖类", "浏览器启动失败：{reason}。"),
    "ENV_006": FailureDef("环境与依赖类", "测试脚本不存在：未找到脚本编号 {script_id}。"),
    "AUTH_001": FailureDef("登录与权限类", "未进入登录后页面：{system_name} 登录后页面未出现。"),
    "AUTH_004": FailureDef("登录与权限类", "登录态失效：{system_name} 登录态已失效。"),
    "AUTH_005": FailureDef("登录与权限类", "权限不足：当前账号无权限访问 {target}。"),
    "NAV_001": FailureDef("页面导航类", "页面打开失败：无法打开 {target_url}。"),
    "NAV_002": FailureDef("页面导航类", "菜单路径不存在：未找到菜单路径 {menu_path}。"),
    "NAV_003": FailureDef("页面导航类", "页面加载超时：页面 {page_name} 在 {timeout_seconds} 秒内未加载完成。"),
    "NAV_004": FailureDef("页面导航类", "目标页面不匹配：期望页面 {expected_page}，实际页面 {actual_page}。"),
    "ELEMENT_001": FailureDef("页面元素定位类", "输入框未找到：未找到输入框 {locator_desc}。"),
    "ELEMENT_002": FailureDef("页面元素定位类", "按钮未找到：未找到按钮 {locator_desc}。"),
    "ELEMENT_003": FailureDef("页面元素定位类", "表格未找到：未找到表格 {table_desc}。"),
    "ELEMENT_004": FailureDef("页面元素定位类", "表格列未找到：表格 {table_desc} 中未找到列 {column_name}。"),
    "ELEMENT_006": FailureDef("页面元素定位类", "元素不可点击：元素 {locator_desc} 当前不可点击。"),
    "ELEMENT_009": FailureDef("页面元素定位类", "元素定位不唯一：定位 {locator_desc} 匹配到多个元素。"),
    "DATA_001": FailureDef("数据与变量类", "输入参数缺失：缺少输入参数 {param_name}。"),
    "DATA_002": FailureDef("数据与变量类", "前序变量缺失：缺少前序变量 {variable_name}。"),
    "DATA_003": FailureDef("数据与变量类", "变量提取失败：未能提取变量 {variable_name}。"),
    "DATA_005": FailureDef("数据与变量类", "提取到多个候选值：变量 {variable_name} 匹配到多个候选值。"),
    "ACTION_001": FailureDef("页面操作类", "点击失败：点击 {target} 失败。"),
    "ACTION_002": FailureDef("页面操作类", "输入失败：向 {target} 输入失败。"),
    "ACTION_003": FailureDef("页面操作类", "查询失败：按条件 {condition_name}={condition_value} 查询失败。"),
    "ACTION_004": FailureDef("页面操作类", "保存或提交失败：{action_name} 执行失败。"),
    "ACTION_009": FailureDef("页面操作类", "操作成功提示缺失：未出现成功提示 {success_text}。"),
    "ASSERT_001": FailureDef("页面断言类", "查询无结果：使用查询条件 {condition_name}={condition_value} 未查询到记录。"),
    "ASSERT_002": FailureDef("页面断言类", "字段值不一致：字段 {field_name} 期望值为 {expected_value}，实际值为 {actual_value}。"),
    "ASSERT_003": FailureDef("页面断言类", "状态不符合预期：字段 {status_field} 期望状态为 {expected_status}，实际状态为 {actual_status}。"),
    "ASSERT_004": FailureDef("页面断言类", "数量不一致：{count_name} 期望数量为 {expected_count}，实际数量为 {actual_count}。"),
    "ASSERT_005": FailureDef("页面断言类", "成功提示未出现：未出现成功提示 {success_text}。"),
    "ASSERT_006": FailureDef("页面断言类", "异常提示出现：页面出现异常提示 {error_text}。"),
    "ASSERT_013": FailureDef("页面断言类", "轮询超时：轮询 {retries} 次后仍未满足条件 {condition_desc}。"),
    "SYSTEM_001": FailureDef("系统异常类", "前端系统异常：{reason}。"),
    "SYSTEM_002": FailureDef("系统异常类", "接口请求失败：{request_desc}。"),
    "SYSTEM_003": FailureDef("系统异常类", "页面空白：页面 {page_name} 无有效内容。"),
    "SYSTEM_004": FailureDef("系统异常类", "页面长时间无响应：页面 {page_name} 长时间无响应。"),
    "SYSTEM_006": FailureDef("系统异常类", "未知系统异常：{reason}。"),
    "REPORT_001": FailureDef("报告生成类", "报告模板缺失：未找到报告模板 {template_path}。"),
    "REPORT_002": FailureDef("报告生成类", "报告写入失败：{reason}。"),
    "REPORT_003": FailureDef("报告生成类", "操作日志写入失败：{reason}。"),
    "REPORT_005": FailureDef("报告生成类", "汇总统计失败：{reason}。"),
}


class SafeFormatDict(dict):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def make_failure(code: str, **kwargs: Any) -> dict[str, str]:
    failure_def = ERROR_CATALOG.get(
        code,
        FailureDef("系统异常类", "未知失败编码：{code}，上下文：{context}。"),
    )
    values = SafeFormatDict(kwargs)
    values["code"] = code
    values["context"] = ", ".join(f"{key}={value}" for key, value in kwargs.items())
    detail = failure_def.template.format_map(values)
    return {
        "code": code,
        "failure_type": failure_def.failure_type,
        "message": f"[{code}] {detail}",
    }
