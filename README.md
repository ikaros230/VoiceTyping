# VoiceTyping — 语音输入法

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform: Windows](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

**VoiceTyping** 是一款 Windows 本地语音输入法。按住全局快捷键说话，松开后自动将识别文字插入任意应用的光标处。基于 faster-whisper 本地推理，**零 API 成本、可离线使用、数据不出本机**。


---

## 特性一览

| 特性 | 说明 |
|------|------|
| 🎙️ **Push-to-Talk** | 按住说话、松开输入，默认 `Ctrl+Shift+Space`，可自定义热键 |
| 🧠 **本地识别** | faster-whisper 离线推理，无需 API 密钥 |
| 📝 **任意应用输入** | 剪贴板粘贴，支持 Word、浏览器、微信、IDE 等 |
| 🈲 **简繁切换** | 识别结果一键切换简体 / 繁体 |
| 📋 **历史剪贴板** | 保存转写记录，支持搜索、复制、重新插入 |
| 🔊 **麦克风选择** | 支持切换系统内不同输入设备 |
| 📊 **录音提示** | 悬浮条显示「麦克风使用中」+ 实时音量条 |
| ⚠️ **音量警告** | 声音过小时自动提醒 |
| 🔔 **系统托盘** | 后台运行，三色状态指示（就绪 / 录音 / 识别） |

---

## 快速开始

### 环境要求

- Windows 10 / 11
- Python 3.10+
- 麦克风
- （可选）NVIDIA GPU + CUDA

### 安装

```powershell
git clone https://github.com/ikaros230/VoiceTyping.git
cd VoiceTyping
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

### 运行

```powershell
python -m voicetyping.main
```

首次运行会自动下载 Whisper `base` 模型（约 145 MB，需联网）。模型缓存后**后续可完全离线使用**。

### 预下载模型（可选）

```powershell
python scripts/download_model.py
```

---

## 使用说明

1. 启动后，系统托盘出现 VoiceTyping 图标
2. 在任意文本框中聚焦光标
3. **按住** `Ctrl+Shift+Space` 开始说话
4. 屏幕底部显示 **「🎤 麦克风使用中」** 及音量条
5. **松开** 快捷键，识别结果自动插入光标处

### 托盘菜单

| 操作 | 说明 |
|------|------|
| 左键点击图标 | 打开历史剪贴板 |
| 历史剪贴板 | 查看 / 搜索 / 复制 / 重新插入历史记录 |
| 文字输出 | 切换简体中文 / 繁體中文 |
| 修改热键 | 录制自定义快捷键（立即生效） |
| 选择麦克风 | 切换录音输入设备 |
| 退出 | 关闭程序 |

> **提示**：若热键无效，请以**管理员身份**运行。

---

## 配置

配置文件：`%APPDATA%\VoiceTyping\config.json`

```powershell
python -m voicetyping.main --config       # 查看配置
python -m voicetyping.main --init-config  # 生成默认配置
```

| 字段 | 说明 | 默认值 |
|------|------|--------|
| `model_size` | 模型大小（tiny/base/small/medium） | `base` |
| `language` | 识别语言 | `zh` |
| `chinese_script` | 输出字体（simplified/traditional） | `simplified` |
| `hotkey` | 全局快捷键 | `ctrl+shift+space` |
| `input_device` | 麦克风索引（null=系统默认） | `null` |
| `history_max_items` | 历史记录上限 | `100` |
| `show_recording_indicator` | 录音悬浮提示 | `true` |
| `low_volume_rms_threshold` | 音量过小阈值 | `0.015` |
| `hf_endpoint` | 模型下载镜像 | `https://hf-mirror.com` |
| `restore_clipboard` | 插入后恢复剪贴板 | `true` |

完整配置说明见 [docs/PROJECT.md#7-配置说明](docs/PROJECT.md#7-配置说明)。

---

## 离线使用

| 场景 | 联网 |
|------|------|
| 首次运行（下载模型） | 需要 |
| 日常使用 | **不需要** |
| 更换模型 | 需要 |

---

## 打包发布

```powershell
# 构建绿色版
.\scripts\build.ps1
# 输出：dist\VoiceTyping\VoiceTyping.exe

# 制作安装包：用 Inno Setup 编译 installer\VoiceTyping.iss
```

| 内容 | 大小 |
|------|------|
| 程序（不含模型） | ~350 MB |
| base 模型 | ~145 MB |

详见 [docs/PROJECT.md#9-打包与分发](docs/PROJECT.md#9-打包与分发)。

---

## 项目结构

```
src/voicetyping/
├── audio/       # 麦克风采集、设备选择、音量分析
├── stt/         # faster-whisper 语音识别
├── output/      # 文字注入（Windows）
├── hotkey/      # 全局 Push-to-Talk
├── text/        # 简繁体转换
├── history/     # 历史记录
├── config/      # 配置管理
├── ui/          # 托盘、对话框、录音指示器
├── pipeline.py  # 核心编排
└── main.py      # 入口
```

---

## 开发与测试

```powershell
pip install -e ".[dev]"          # 或 pip install pytest
python -m pytest tests/ -v       # 运行测试
python scripts/demo_pipeline.py  # 端到端测试
```

---

## 常见问题

**热键无效？** → 以管理员身份运行。

**识别为空？** → 检查麦克风权限与设备选择，确保说话时间 > 0.3 秒。

**模型下载失败？** → 确认 `hf_endpoint` 为 `https://hf-mirror.com`，或运行 `python scripts/download_model.py`。

**更多问题** → 见 [docs/PROJECT.md#12-常见问题](docs/PROJECT.md#12-常见问题)。

---

## 技术栈

Python · faster-whisper · sounddevice · keyboard · pystray · OpenCC · pydantic · tkinter · PyInstaller

---

## 许可证

[MIT License](LICENSE)

---

## 相关文档

- [功能演示稿（推荐）](docs/DEMO.md) — 照着讲即可完成功能演示
- [完整项目介绍](docs/PROJECT.md)
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
