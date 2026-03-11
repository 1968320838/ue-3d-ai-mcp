"""文本生成3D模型核心工具"""

import asyncio
import time
from datetime import datetime
from pathlib import Path
from typing import Literal
import httpx

from ue_3d_generator.config import config


# MCP工具配置
TOOL_NAME = "text_to_ue_3d"

TOOL_DESCRIPTION = """
Generate a 3D model from text description for Unreal Engine.

This tool uses TripoAI to generate game-ready FBX models optimized for UE5.
The generated model will be saved to the output directory and can be directly
imported into Unreal Engine.

Typical usage examples:
- "A fantasy sword with glowing runes"
- "A sci-fi crate with metal panels"
- "A medieval wooden shield"
- "A futuristic robot arm"

Generation takes approximately 15-20 seconds.
"""

# 输入Schema (JSON Schema)
INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "prompt": {
            "type": "string",
            "description": "Text description of the 3D model to generate"
        },
        "output_name": {
            "type": "string",
            "description": "Optional: Custom filename for the output FBX (without extension)"
        },
        "quality": {
            "type": "string",
            "enum": ["draft", "standard", "high"],
            "description": "Generation quality level (default: standard)"
        }
    },
    "required": ["prompt"]
}


class GenerationError(Exception):
    """生成错误异常"""
    pass


async def submit_generation_task(prompt: str, quality: str = "standard") -> str:
    """
    提交生成任务到fal.ai

    Args:
        prompt: 文本描述
        quality: 质量等级

    Returns:
        request_id: 任务ID
    """
    url = f"{config.FAL_API_BASE}/{config.TRIPO_MODEL_ID}/requests"

    payload = {
        "prompt": prompt,
        "format": "fbx"
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            url,
            headers=config.get_headers(),
            json=payload
        )
        response.raise_for_status()
        data = response.json()
        return data["request_id"]


async def poll_task_status(request_id: str) -> dict:
    """
    轮询任务状态直到完成

    Args:
        request_id: 任务ID

    Returns:
        完成的任务结果
    """
    url = f"{config.FAL_API_BASE}/{config.TRIPO_MODEL_ID}/requests/{request_id}/status"

    start_time = time.time()

    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            if time.time() - start_time > config.MAX_POLL_TIME:
                raise GenerationError(f"Generation timeout after {config.MAX_POLL_TIME} seconds")

            response = await client.get(
                url,
                headers=config.get_headers()
            )
            response.raise_for_status()
            data = response.json()

            status = data.get("status")

            if status == "COMPLETED":
                # 获取完整结果
                result_url = f"{config.FAL_API_BASE}/{config.TRIPO_MODEL_ID}/requests/{request_id}"
                result_response = await client.get(
                    result_url,
                    headers=config.get_headers()
                )
                result_response.raise_for_status()
                return result_response.json()

            elif status == "FAILED":
                error = data.get("error", "Unknown error")
                raise GenerationError(f"Generation failed: {error}")

            # 等待后继续轮询
            await asyncio.sleep(config.POLL_INTERVAL)


async def download_model(model_url: str, output_path: Path) -> None:
    """
    下载FBX模型文件

    Args:
        model_url: 模型下载URL
        output_path: 输出文件路径
    """
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.get(model_url)
        response.raise_for_status()

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(response.content)


def generate_output_name(prompt: str, custom_name: str | None = None) -> str:
    """
    生成输出文件名

    Args:
        prompt: 原始提示词
        custom_name: 自定义文件名

    Returns:
        文件名(不含扩展名)
    """
    if custom_name:
        return custom_name

    # 从提示词提取关键词
    words = prompt.lower().split()[:5]  # 取前5个词
    safe_words = [w for w in words if w.isalpha() or w.isdigit()]
    base_name = "_".join(safe_words) if safe_words else "model"

    # 添加时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}"


async def generate_3d_model(
    prompt: str,
    output_name: str | None = None,
    quality: Literal["draft", "standard", "high"] = "standard"
) -> dict:
    """
    调用TripoAI API生成3D模型

    Args:
        prompt: 文本描述
        output_name: 自定义输出文件名
        quality: 质量等级

    Returns:
        包含生成结果的字典
    """
    start_time = time.time()

    try:
        # 1. 提交生成任务
        request_id = await submit_generation_task(prompt, quality)

        # 2. 轮询任务状态
        result = await poll_task_status(request_id)

        # 3. 获取模型URL和缩略图
        model_url = result.get("output", {}).get("model_url")
        if not model_url:
            raise GenerationError("No model URL in response")

        # 4. 生成输出文件名
        safe_name = generate_output_name(prompt, output_name)
        output_path = config.OUTPUT_DIR / f"{safe_name}.fbx"

        # 5. 下载模型文件
        await download_model(model_url, output_path)

        # 6. 计算耗时
        elapsed = time.time() - start_time

        return {
            "status": "success",
            "file_path": str(output_path.absolute()),
            "file_name": output_path.name,
            "prompt": prompt,
            "quality": quality,
            "request_id": request_id,
            "generation_time": f"{elapsed:.1f}s",
            "thumbnail_url": result.get("output", {}).get("thumbnail_url"),
            "ue_import_instructions": (
                f"To import into Unreal Engine:\n"
                f"1. Open Content Browser in UE5\n"
                f"2. Click Import → Select '{output_path.name}'\n"
                f"3. Configure import settings if needed\n"
                f"4. Click Import"
            )
        }

    except httpx.HTTPStatusError as e:
        raise GenerationError(f"API request failed: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        raise GenerationError(f"Network error: {str(e)}")
    except Exception as e:
        raise GenerationError(f"Unexpected error: {str(e)}")
