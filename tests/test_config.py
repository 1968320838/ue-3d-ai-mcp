"""测试配置模块"""

import pytest
from pathlib import Path
from ue_3d_generator.config import config


def test_output_dir_exists():
    """测试输出目录是否存在"""
    assert config.OUTPUT_DIR.exists()


def test_config_attributes():
    """测试配置属性"""
    assert hasattr(config, "FAL_API_BASE")
    assert hasattr(config, "TRIPO_MODEL_ID")
    assert hasattr(config, "OUTPUT_DIR")
    assert hasattr(config, "POLL_INTERVAL")


def test_headers():
    """测试API请求头生成"""
    headers = config.get_headers()
    assert "Authorization" in headers
    assert "Content-Type" in headers
    assert headers["Content-Type"] == "application/json"
