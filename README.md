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
5. **左键点击**托盘图标，或右键选择 **历史剪贴板**，查看语音转换历史（支持搜索）
6. 右键托盘图标 → **选择麦克风**，切换录音输入设备
7. 右键托盘图标 → **修改热键**，可录制自定义 Push-to-Talk 快捷键（立即生效）
8. 右键托盘图标 → **文字输出**，可切换 **简体中文** / **繁體中文**

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
| `input_device` | 麦克风设备索引（`null` 为系统默认） | `null` |
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

## 打包发布（开发者）

可将 VoiceTyping 打包为 Windows 可执行程序，分发给无需安装 Python 的用户。

### 方式一：绿色版（文件夹）

```powershell
.\scripts\build.ps1
```

构建完成后，输出目录为 `dist\VoiceTyping\`，其中 `VoiceTyping.exe` 为程序入口。

可将整个 `VoiceTyping` 文件夹压缩为 zip 发给用户，解压后双击运行即可。

### 方式二：安装包（Setup.exe）

1. 先执行 `.\scripts\build.ps1` 完成构建
2. 安装 [Inno Setup 6](https://jrsoftware.org/isinfo.php)
3. 用 Inno Setup 打开 `installer\VoiceTyping.iss` 并编译
4. 安装包输出在 `installer\output\VoiceTyping-Setup-0.1.0.exe`

### 打包体积说明

| 内容 | 大小 |
|------|------|
| 打包后程序（不含模型） | 约 400–600 MB |
| 首次运行下载 base 模型 | 约 145 MB |

模型不会打入安装包，首次运行自动下载（默认使用国内镜像）。

### 用户使用说明（打包版）

1. 安装或解压后运行 `VoiceTyping.exe`
2. 首次启动需联网下载语音识别模型
3. 若全局热键无效，请右键「以管理员身份运行」
4. 配置与历史记录保存在 `%APPDATA%\VoiceTyping\`
