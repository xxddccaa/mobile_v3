# encoding=utf-8
"""
Mobile Agent v3 FastAPI Server
提供执行移动设备自动化任务的 API 接口
"""
import asyncio
import json
import os
import re
import subprocess
import sys
import time
import traceback
from typing import Optional, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field
import logging
from utils.call_mobile_agent_e import GUIOwlWrapper

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="Mobile Agent v3 API",
    description="移动设备自动化任务执行 API",
    version="1.0.0"
)


class CustomErrorResponse:
    """自定义错误响应"""
    def __init__(self, description: str, error_code: int, detail: str):
        self.description = description
        self.error_code = error_code
        self.detail = detail

    def to_response_dict(self):
        return {
            "description": self.description,
            "content": {
                "application/json": {
                    "example": {
                        "error_code": self.error_code,
                        "detail": self.detail,
                        "code": self.error_code,
                        "message": self.detail
                    }
                }
            },
        }

    def __call__(self, extra_detail=None):
        detailx = ""
        if extra_detail is not None:
            detailx = f"detail:{self.detail}, extra_detail:{extra_detail}"
        else:
            detailx = self.detail
        return JSONResponse(
            content={
                "code": self.error_code,
                "message": "发生了错误：" + detailx,
                "data": None,
                "error_code": self.error_code,
                "detail": "发生了错误：" + detailx
            },
            status_code=self.error_code
        )


# 定义错误响应
ExecutionErrorResponse = CustomErrorResponse("执行任务失败", 500, "执行任务失败")
TimeoutErrorResponse = CustomErrorResponse("任务执行超时", 504, "任务执行超时")
ParseErrorResponse = CustomErrorResponse("解析输出失败", 502, "解析输出失败")


# 定义接管 RequestValidationError 的方法
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    message = ""
    for error in exc.errors():
        message += ".".join(str(loc) for loc in error.get("loc")) + ":" + error.get("msg") + ";"
    return JSONResponse(
        content={
            "code": 422,
            "message": "传入参数不符合要求:" + str(message),
            "error_code": 422,
            "detail": "传入参数不符合要求:" + str(message),
            "data": None
        },
        status_code=422
    )


class MobileAgentRequest(BaseModel):
    """Mobile Agent 任务请求模型"""
    adb_path: str = Field(
        default=r"D:\platform-tools\adb.exe",
        title="ADB 路径",
        description="Android Debug Bridge 工具的路径"
    )
    api_key: str = Field(
        default="123",
        title="API Key",
        description="LLM API 密钥"
    )
    base_url: str = Field(
        default="http://10.142.18.204:8006/v1",
        title="API Base URL",
        description="LLM API 的基础 URL"
    )
    model: str = Field(
        default="owl32b",
        title="模型名称",
        description="使用的 LLM 模型名称"
    )
    instruction: str = Field(
        ...,
        title="任务指令",
        description="要执行的任务指令",
        max_length=1000
    )
    add_info: str = Field(
        default="整理某东西的微博动态的操作：1. 微博应用图标不在可见范围内, 使用 open_app 微博 动作直接打开微博应用（无需滑动），2. 点击发现按钮。 3. 输入搜索词，但不要打开智搜开关。 4. 点击搜索按钮。 5. 在搜索结果里再去点击智搜按钮，进入到智搜的结果页面。 6. 点击左下角的 继续问智搜。 7. 点击右下方的'向下箭头'的按钮。 8. 点击复制按钮，点击复制按钮的动作描述要写成 点击复制按钮，点击后就不需要任何操作了，退出agent。",
        title="附加信息",
        description="任务执行的附加信息和步骤说明",
        max_length=5000
    )
    timeout: int = Field(
        default=600,
        title="超时时间",
        description="任务执行超时时间（秒）",
        ge=60,
        le=1800
    )
    requestId: Optional[str] = Field(
        None,
        title="请求 ID",
        description="请求的唯一标识符"
    )


class MobileAgentResponse(BaseModel):
    """Mobile Agent 任务响应模型"""
    code: int = Field(200, title="状态码", description="响应状态码")
    message: str = Field("success", title="消息", description="响应消息")
    error_code: int = Field(200, title="错误码", description="和 code 一样，为了保持一致")
    detail: str = Field("success", title="详情", description="和 message 一样，为了保持一致")
    
    data: Optional[Dict[str, Any]] = Field(
        None,
        title="返回数据",
        description="任务执行结果数据"
    )
    requestId: Optional[str] = Field(None, title="请求 ID", description="请求的唯一标识符")
    execution_time: Optional[float] = Field(None, title="执行时间", description="任务执行耗时（秒）")


def parse_clipboard_content(output: str) -> Optional[str]:
    """
    从输出中解析粘贴板内容
    
    Args:
        output: 命令行输出
        
    Returns:
        粘贴板内容，如果未找到则返回 None
    """
    try:
        # 查找粘贴板内容的标记
        pattern = r"检测到复制操作，粘贴板内容如下：\n={80}\n(.*?)\n={80}"
        match = re.search(pattern, output, re.DOTALL)
        
        if match:
            clipboard_content = match.group(1).strip()
            return clipboard_content
        
        # 如果没有找到标准格式，尝试查找"已获取粘贴板内容并停止操作"之前的内容
        if "已获取粘贴板内容并停止操作" in output:
            # 提取最后一个分隔符块之间的内容
            lines = output.split('\n')
            content_lines = []
            in_content = False
            separator_count = 0
            
            for line in lines:
                if "检测到复制操作，粘贴板内容如下：" in line:
                    in_content = False
                    separator_count = 0
                    content_lines = []
                    continue
                    
                if '=' * 80 in line:
                    separator_count += 1
                    if separator_count == 1:
                        in_content = True
                    elif separator_count == 2:
                        in_content = False
                        break
                    continue
                
                if in_content:
                    content_lines.append(line)
            
            if content_lines:
                return '\n'.join(content_lines).strip()
        
        return None
        
    except Exception as e:
        logger.error(f"解析粘贴板内容失败: {str(e)}")
        return None


async def summarize_clipboard_content(
    api_key: str,
    base_url: str,
    model: str,
    instruction: str,
    clipboard_content: str,
    max_chars: int = 500
) -> Optional[str]:
    """
    使用同一大模型对粘贴板内容做精简总结
    
    Args:
        api_key: LLM API Key
        base_url: LLM Base URL
        model: 模型名称
        instruction: 用户原始指令
        clipboard_content: 原始粘贴板内容
        max_chars: 期望的最大字数上限（非硬限制）
    Returns:
        总结文本；失败返回 None
    """
    if not clipboard_content:
        return None
    
    prompt_messages = [
        {
            "role": "user",
            "content": [
                {"text": (
                    "你是信息压缩助手。请基于用户原始指令与已获取的完整内容，"
                    "输出一段更短、更清晰的总结：\n\n"
                    "- 保留关键信息、事实、时间、数据与结论；\n"
                    "- 合并去重、去噪，避免口水话；\n"
                    "- 禁止虚构；\n"
                    f"- 目标不超过约{max_chars}字；\n"
                    "- 可用简短小标题或要点列表；\n"
                    "请只输出总结正文，不要附加任何前后缀。\n\n"
                    f"【用户指令】\n{instruction}\n\n"
                    f"【完整内容】\n{clipboard_content}"
                )}
            ]
        }
    ]
    
    def _call_llm():
        try:
            bot = GUIOwlWrapper(api_key=api_key, base_url=base_url, model_name=model)
            text, _, _ = bot.predict_mm("", [], messages=prompt_messages)
            return text
        except Exception as e:
            logger.error(f"调用大模型生成精简内容失败: {str(e)}")
            return None
    
    # 在线程中执行同步 LLM 调用，避免阻塞事件循环
    result = await asyncio.to_thread(_call_llm)
    return result


async def read_stream(stream, stream_name: str, output_buffer: list):
    """
    异步读取流并实时打印
    
    Args:
        stream: 异步流对象
        stream_name: 流名称（stdout/stderr）
        output_buffer: 用于保存输出的列表
    """
    try:
        while True:
            line = await stream.readline()
            if not line:
                break
            
            # 尝试优先使用 UTF-8 解码，失败则回退到 GBK/CP936
            try:
                line_str = line.decode('utf-8').rstrip()
            except UnicodeDecodeError:
                try:
                    line_str = line.decode('gbk').rstrip()
                except UnicodeDecodeError:
                    line_str = line.decode('cp936', errors='ignore').rstrip()
            
            # 实时打印到控制台和日志
            if line_str:
                print(f"[{stream_name}] {line_str}", flush=True)
                logger.info(f"[{stream_name}] {line_str}")
            
            # 保存到缓冲区
            output_buffer.append(line_str)
            
    except Exception as e:
        logger.error(f"读取 {stream_name} 失败: {str(e)}")


async def execute_mobile_agent(
    adb_path: str,
    api_key: str,
    base_url: str,
    model: str,
    instruction: str,
    add_info: str,
    timeout: int
) -> tuple[str, str, int]:
    """
    执行 Mobile Agent 脚本（支持实时输出）
    
    Args:
        adb_path: ADB 路径
        api_key: API 密钥
        base_url: API 基础 URL
        model: 模型名称
        instruction: 任务指令
        add_info: 附加信息
        timeout: 超时时间
        
    Returns:
        (stdout, stderr, returncode)
    """
    # 构建命令
    script_path = os.path.join(os.path.dirname(__file__), "run_mobileagentv3.py")
    
    cmd = [
        sys.executable,  # Python 解释器路径
        "-u",  # 强制子进程无缓冲输出
        script_path,
        "--adb_path", adb_path,
        "--api_key", api_key,
        "--base_url", base_url,
        "--model", model,
        "--instruction", instruction,
        "--add_info", add_info
    ]
    
    logger.info(f"执行命令: {' '.join(cmd)}")
    logger.info("="*80)
    logger.info("开始执行任务，以下是实时输出：")
    logger.info("="*80)
    
    try:
        # 异步执行子进程
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=os.path.dirname(__file__),
            env=env
        )
        
        # 用于保存完整输出
        stdout_lines = []
        stderr_lines = []
        
        # 创建异步任务读取 stdout 和 stderr
        stdout_task = asyncio.create_task(
            read_stream(process.stdout, "stdout", stdout_lines)
        )
        stderr_task = asyncio.create_task(
            read_stream(process.stderr, "stderr", stderr_lines)
        )
        
        # 等待进程完成和流读取完成，设置超时
        try:
            # 等待进程结束
            await asyncio.wait_for(
                process.wait(),
                timeout=timeout
            )
            
            # 等待流读取完成
            await asyncio.gather(stdout_task, stderr_task)
            
            # 合并输出
            stdout_str = '\n'.join(stdout_lines)
            stderr_str = '\n'.join(stderr_lines)
            
            logger.info("="*80)
            logger.info("任务执行完成")
            logger.info("="*80)
            
            return stdout_str, stderr_str, process.returncode
            
        except asyncio.TimeoutError:
            # 超时，终止进程
            logger.warning(f"任务执行超时（{timeout}秒），正在终止进程...")
            process.kill()
            await process.wait()
            
            # 取消流读取任务
            stdout_task.cancel()
            stderr_task.cancel()
            
            raise TimeoutError(f"任务执行超时（{timeout}秒）")
            
    except Exception as e:
        logger.error(f"执行任务失败: {str(e)}")
        raise


@app.post(
    "/mobile_agent/execute",
    summary="执行移动设备自动化任务",
    description="执行 Mobile Agent 自动化任务，并返回粘贴板内容",
    response_model=MobileAgentResponse,
    responses={
        ExecutionErrorResponse.error_code: ExecutionErrorResponse.to_response_dict(),
        TimeoutErrorResponse.error_code: TimeoutErrorResponse.to_response_dict(),
        ParseErrorResponse.error_code: ParseErrorResponse.to_response_dict(),
    }
)
async def execute_task(request: MobileAgentRequest):
    """
    执行移动设备自动化任务接口
    
    接收任务参数，执行 Mobile Agent 脚本，返回粘贴板内容
    """
    start_time = time.time()
    
    logger.info("="*80)
    logger.info(f"收到新任务请求")
    logger.info(f"RequestId: {request.requestId}")
    logger.info(f"Instruction: {request.instruction}")
    logger.info("="*80)
    
    try:
        # 执行任务
        stdout, stderr, returncode = await execute_mobile_agent(
            adb_path=request.adb_path,
            api_key=request.api_key,
            base_url=request.base_url,
            model=request.model,
            instruction=request.instruction,
            add_info=request.add_info,
            timeout=request.timeout
        )
        
        execution_time = time.time() - start_time
        
        # 检查返回码
        if returncode != 0:
            logger.error(f"任务执行失败，返回码: {returncode}")
            logger.error(f"stderr: {stderr}")
            return ExecutionErrorResponse(f"返回码: {returncode}, stderr: {stderr[:500]}")
        
        # 解析粘贴板内容
        clipboard_content = parse_clipboard_content(stdout)
        
        if clipboard_content is None:
            logger.warning("未能从输出中解析到粘贴板内容")
            # 尝试从 stderr 中查找
            clipboard_content = parse_clipboard_content(stderr)
        
        # 准备返回数据
        response_data = {
            "clipboard_content": clipboard_content,
            "has_clipboard": clipboard_content is not None,
            "stdout_preview": stdout[-1000:] if len(stdout) > 1000 else stdout,  # 最后1000字符
            "task_completed": True,
            "timestamp": datetime.now().isoformat()
        }
        
        # 生成精简版本
        clipboard_summary = None
        if clipboard_content:
            clipboard_summary = await summarize_clipboard_content(
                api_key=request.api_key,
                base_url=request.base_url,
                model=request.model,
                instruction=request.instruction,
                clipboard_content=clipboard_content,
                max_chars=500
            )
            if clipboard_summary:
                response_data["clipboard_summary"] = clipboard_summary
            else:
                response_data["clipboard_summary"] = None
        
        # 如果没有找到粘贴板内容，返回警告但不报错
        if clipboard_content is None:
            response_data["warning"] = "未检测到复制操作或粘贴板内容为空"
            logger.warning("未检测到复制操作")
        else:
            logger.info(f"成功获取粘贴板内容，长度: {len(clipboard_content)} 字符")
        
        # 记录日志
        log_str = (
            f"@requestId:{request.requestId}"
            f"@Function:/mobile_agent/execute"
            f"@time-consuming:{execution_time:.2f}"
            f"@instruction:{request.instruction}"
            f"@model:{request.model}"
            f"@clipboard_length:{len(clipboard_content) if clipboard_content else 0}"
        )
        logger.info(log_str)
        
        return {
            "code": 200,
            "message": "success",
            "error_code": 200,
            "detail": "success",
            "data": response_data,
            "requestId": request.requestId,
            "execution_time": execution_time
        }
        
    except TimeoutError as e:
        execution_time = time.time() - start_time
        logger.error(f"任务超时: {str(e)}")
        return TimeoutErrorResponse(str(e))
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"执行任务时发生异常: {str(e)}")
        logger.error(traceback.format_exc())
        return ExecutionErrorResponse(f"{str(e)}\n{traceback.format_exc()[:500]}")


@app.get("/health", summary="健康检查", description="检查服务是否正常运行")
async def health_check():
    """健康检查接口"""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "Mobile Agent v3 API",
            "timestamp": datetime.now().isoformat()
        },
        status_code=200
    )


@app.get("/", summary="API 信息", description="获取 API 基本信息")
async def root():
    """根路径，返回 API 信息"""
    return {
        "service": "Mobile Agent v3 API",
        "version": "1.0.0",
        "description": "移动设备自动化任务执行 API",
        "endpoints": {
            "execute": "/mobile_agent/execute",
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    # 启动服务器
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8003,
        reload=False,
        log_level="info"
    )

