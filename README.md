# UE 3D AI MCP

> 通过一句话生成3D模型的MCP工具，专为Unreal Engine优化

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-FastMCP-orange)](https://github.com/jlowin/fastmcp)

## 功能特点

- **文本生成3D**: 输入自然语言描述，AI从零生成独特的3D模型
- **UE优化**: 输出FBX格式，可直接导入Unreal Engine
- **快速生成**: 约15-20秒完成模型生成
- **游戏就绪**: 生成高质量的网格和纹理
- **Claude集成**: 作为MCP工具与Claude Desktop无缝集成

## 工作原理

```
你输入: "一把中世纪火焰剑"
   │
   ▼
Claude调用MCP工具
   │
   ▼
TripoAI扩散模型生成3D (15-20秒)
   │
   ▼
下载FBX到本地
   │
   ▼
导入Unreal Engine使用
```

## 安装

### 1. 获取API密钥

访问 [fal.ai](https://fal.ai/) 注册并获取 `FAL_API_KEY`。

### 2. 克隆仓库

```bash
git clone https://github.com/YOUR_USERNAME/ue-3d-ai-mcp.git
cd ue-3d-ai-mcp
```

### 3. 安装依赖

```bash
# 使用 uv (推荐)
uv sync

# 或使用 pip
pip install -r requirements.txt
```

### 4. 配置环境变量

复制 `.env.example` 为 `.env` 并填入你的API密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
FAL_API_KEY=your_fal_api_key_here
OUTPUT_DIR=./output
```

## 使用方法

### 在Claude Desktop中配置

编辑 Claude Desktop 配置文件：

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "ue-3d-generator": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/ue-3d-ai-mcp",
        "run",
        "ue-3d-generator"
      ],
      "env": {
        "FAL_API_KEY": "your_fal_api_key_here"
      }
    }
  }
}
```

### 使用示例

重启Claude Desktop后，直接对话：

```
你: 生成一个科幻风格的能量剑

Claude: [调用text_to_ue_3d工具]

返回结果:
{
  "status": "success",
  "file_path": "/path/to/output/sci_fi_energy_sword_20250311_143022.fbx",
  "generation_time": "18.5s",
  "ue_import_instructions": "..."
}
```

更多示例提示词：
- "一个中世纪骑士盾牌"
- "赛博朋克风格的霓虹灯牌"
- "一个木制宝箱，有金属装饰"
- "未来派机器人手臂"

## 工具参数

### text_to_ue_3d

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| prompt | string | 是 | 3D模型的文本描述 |
| output_name | string | 否 | 自定义输出文件名（不含扩展名） |
| quality | string | 否 | 质量等级：draft/standard/high (默认: standard) |

## 导入到Unreal Engine

1. 打开Unreal Engine 5
2. 在Content Browser中点击 **Import**
3. 选择生成的 `.fbx` 文件
4. 配置导入设置（如需要）
5. 点击 **Import**

## 项目结构

```
ue-3d-ai-mcp/
├── ue_3d_generator/
│   ├── __init__.py
│   ├── server.py           # MCP服务器入口
│   ├── config.py           # 配置管理
│   └── tools/
│       ├── __init__.py
│       └── text_to_3d.py   # 核心生成工具
├── output/                 # 生成的FBX文件
├── tests/
├── pyproject.toml
├── requirements.txt
├── .env.example
└── README.md
```

## 技术栈

- **Python 3.10+**
- **FastMCP**: MCP框架
- **TripoAI (via fal.ai)**: 3D模型生成服务
- **httpx**: 异步HTTP客户端

## API成本

- **TripoAI via fal.ai**: 约 $0.20-$0.40/模型
- 建议先使用免费额度测试

## 常见问题

### 这是下载现成模型吗？

不是！每次都是AI从零生成的新模型，同一提示词会产生不同结果。

### 生成速度如何？

约15-20秒，取决于模型复杂度。

### 支持其他格式吗？

目前输出FBX（UE推荐格式），可通过工具转换。

## 故障排查

### API密钥错误
```
ValueError: FAL_API_KEY is required
```
检查 `.env` 文件中的 `FAL_API_KEY` 是否正确。

### 网络超时
```
GenerationError: Generation timeout
```
检查网络连接，或增加 `config.py` 中的 `MAX_POLL_TIME`。

### 生成失败
```
GenerationError: Generation failed
```
检查提示词是否符合服务条款，或联系fal.ai支持。

## 后续扩展

- [ ] 批量生成多个模型
- [ ] 添加模型预览图
- [ ] 支持多种风格选项
- [ ] 集成更多3D生成服务

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 相关链接

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [fal.ai](https://fal.ai/)
- [TripoAI](https://www.tripo3d.ai/)
- [FastMCP](https://github.com/jlowin/fastmcp)
