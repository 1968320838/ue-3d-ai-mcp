"""配置管理模块"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """应用配置类"""

    # API配置
    FAL_API_KEY: str = os.getenv("FAL_API_KEY", "")
    FAL_API_BASE: str = os.getenv("FAL_API_BASE", "https://queue.fal.run")

    # TripoAI模型配置
    TRIPO_MODEL_ID: str = os.getenv("TRIPO_MODEL_ID", "tripo3d/tripo/v2.5/text-to-3d")

    # 输出配置
    OUTPUT_DIR: Path = Path(os.getenv("OUTPUT_DIR", "./output"))

    # 轮询配置
    POLL_INTERVAL: float = 2.0  # 轮询间隔(秒)
    MAX_POLL_TIME: int = 120    # 最大轮询时间(秒)

    @classmethod
    def validate(cls) -> None:
        """验证必需的配置项"""
        if not cls.FAL_API_KEY:
            raise ValueError(
                "FAL_API_KEY is required. Get it from https://fal.ai/\n"
                "Create a .env file with: FAL_API_KEY=your_key_here"
            )

        # 确保输出目录存在
        cls.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_headers(cls) -> dict:
        """获取API请求头"""
        return {
            "Authorization": f"Key {cls.FAL_API_KEY}",
            "Content-Type": "application/json"
        }


# 创建全局配置实例
def get_config() -> Config:
    """获取配置实例并验证"""
    Config.validate()
    return Config


config = get_config()
