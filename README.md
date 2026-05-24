# VoiceTyping — 语音输入法

本地语音输入法，帮助用户在任意 Windows 应用中通过语音快速输入文字。

## 特性

- **本地识别**：基于 [faster-whisper](https://github.com/SYSTRAN/faster-whisper)，零 API 成本，离线可用
- **全局快捷键**：Push-to-Talk（默认 `Ctrl+Shift+Space`），按住说话、松开输入
- **任意应用输入**：通过剪贴板 + Ctrl+V 插入文字，支持中文
- **系统托盘**：后台运行，显示录音/识别状态

## 环境要求

- Windows 10/11
- Python 3.10+
- 麦克风
- （可选）NVIDIA GPU + CUDA，可显著加速识别

## 安装

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 运行

```bash
python -m voicetyping.main
```

首次运行会自动下载 Whisper 模型（约 150MB–1.5GB，取决于模型大小），可能需要 10–30 秒。

## 使用说明

1. 启动程序后，系统托盘会出现 VoiceTyping 图标
2. 在任意文本框中点击，将光标定位到输入位置
3. 按住 `Ctrl+Shift+Space` 开始录音
4. 说话完毕后松开快捷键，识别结果自动插入光标处
5. **左键点击**托盘图标，或右键选择 **历史剪贴板**，查看语音转换历史
6. 右键托盘图标 → **文字输出**，可切换 **简体中文** / **繁體中文**

> **注意**：全局快捷键功能可能需要以管理员身份运行。若热键无效，请右键「以管理员身份运行」。

## 配置

配置文件位于 `%APPDATA%\VoiceTyping\config.json`，可修改：

| 字段 | 说明 | 默认值 |
|------|------|--------|
| `model_size` | Whisper 模型大小（tiny/base/small/medium） | `base` |
| `hf_endpoint` | HuggingFace 镜像地址（国内用户推荐️保留） | `https://hf-mirror.com` |
| `model_path` | 本地模型目录（设置后忽略 model_size） | `null` |
| `language` | 识别语言 | `zh` |
| `chinese_script` | 输出文字（`simplified` 简体 / `traditional` 繁体） | `simplified` |
| `history_max_items` | 历史剪贴板最多保存条数 | `100` |
| `hotkey` | 全局快捷键 | `ctrl+shift+space` |
| `restore_clipboard` | 插入后是否恢复原剪贴板内容 | `true` |

## 模型下载（首次运行）

首次运行需下载 Whisper 模型。若网络超时，可先单独下载：

```powershell
python scripts/download_model.py
```

国内用户默认已配置镜像 `https://hf-mirror.com`。若仍失败，可手动设置环境变量后重试：

```powershell
$env:HF_ENDPOINT = "https://hf-mirror.com"
python scripts/download_model.py
```

## 开发路线

本项目按功能点分步开发：

1. 项目脚手架
2. 麦克风录音模块
3. Whisper 语音识别引擎
4. 端到端 CLI 管道
5. Windows 文本注入
6. 全局 Push-to-Talk 快捷键
7. 系统托盘 UI
8. 配置持久化

## 目录结构

```
src/voicetyping/
├── audio/          # 麦克风采集
├── stt/            # 语音识别引擎
├── output/         # 文本注入（跨平台抽象）
├── hotkey/         # 全局快捷键
├── config/         # 配置管理
├── ui/             # 系统托盘
├── pipeline.py     # 核心编排
└── main.py         # 入口
```

## License

MIT
