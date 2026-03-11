"""MCP服务器入口

这是UE 3D Generator的MCP服务器，用于与Claude Desktop等客户端通信。
"""

import json
from typing import Any

from fastmcp import FastMCP

from ue_3d_generator.tools import generate_3d_model, GenerationError

# 创建MCP服务器实例
mcp = FastMCP("ue-3d-generator")


@mcp.tool()
async def text_to_ue_3d(
    prompt: str,
    output_name: str | None = None,
    quality: str = "standard"
) -> str:
    """
    Generate a 3D model from text description for Unreal Engine.

    This tool uses TripoAI to generate game-ready FBX models optimized for UE5.
    The generated model will be saved to the output directory and can be directly
    imported into Unreal Engine.

    Args:
        prompt: Text description of the 3D model to generate
            Examples:
            - "A fantasy sword with glowing runes"
            - "A sci-fi crate with metal panels"
            - "A medieval wooden shield"
        output_name: Optional custom filename for the output FBX (without extension)
        quality: Generation quality level - "draft", "standard", or "high" (default: "standard")

    Returns:
        JSON string with generation results including file path and import instructions
    """
    try:
        result = await generate_3d_model(prompt, output_name, quality)
        return json.dumps(result, indent=2, ensure_ascii=False)
    except GenerationError as e:
        error_result = {
            "status": "error",
            "message": str(e),
            "prompt": prompt
        }
        return json.dumps(error_result, indent=2)
    except Exception as e:
        error_result = {
            "status": "error",
            "message": f"Unexpected error: {str(e)}",
            "prompt": prompt
        }
        return json.dumps(error_result, indent=2)


@mcp.resource("ue-3d-generator://config")
def get_config_info() -> str:
    """获取当前配置信息"""
    from ue_3d_generator.config import config

    return json.dumps({
        "model_id": config.TRIPO_MODEL_ID,
        "output_dir": str(config.OUTPUT_DIR.absolute()),
        "api_base": config.FAL_API_BASE,
        "api_key_configured": bool(config.FAL_API_KEY)
    }, indent=2)


def main() -> None:
    """启动MCP服务器"""
    mcp.run()


if __name__ == "__main__":
    main()
