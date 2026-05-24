"""VoiceTyping entry point."""

from __future__ import annotations

import argparse
import json
import sys
import threading

from voicetyping.config.settings import ChineseScript, Settings, config_path, load_settings, save_settings
from voicetyping.hotkey.listener import HotkeyListener
from voicetyping.output.windows import WindowsTextInjector
from voicetyping.pipeline import PipelineState, VoicePipeline
from voicetyping.stt.whisper_engine import WhisperEngine
from voicetyping.ui.tray import TrayApp


def _build_pipeline(settings: Settings) -> VoicePipeline:
    engine = WhisperEngine(
        model_size=settings.model_size,
        device=settings.device,
        language=settings.language,
        hf_endpoint=settings.hf_endpoint,
        model_path=settings.model_path,
    )
    injector = WindowsTextInjector(restore_clipboard=settings.restore_clipboard)
    return VoicePipeline(
        engine=engine,
        injector=injector,
        min_record_seconds=settings.min_record_seconds,
        chinese_script=settings.chinese_script,
    )


def _open_settings_dialog(settings: Settings) -> None:
    """Print current config path and contents; user can edit manually."""
    path = config_path()
    print(f"\nConfig file: {path}")
    print(json.dumps(settings.model_dump(), indent=2, ensure_ascii=False))
    print("Edit the file above and restart VoiceTyping to apply changes.\n")


def run_app(settings: Settings | None = None) -> None:
    settings = settings or load_settings()
    pipeline = _build_pipeline(settings)

    def set_chinese_script(script: ChineseScript) -> None:
        settings.chinese_script = script
        pipeline.chinese_script = script
        save_settings(settings)
        label = "简体中文" if script == "simplified" else "繁體中文"
        print(f"[VoiceTyping] 文字输出已切换为: {label}")

    tray = TrayApp(
        get_chinese_script=lambda: settings.chinese_script,
        on_chinese_script_change=set_chinese_script,
        on_quit=_shutdown,
        on_open_settings=lambda: _open_settings_dialog(settings),
    )

    listener = HotkeyListener(
        hotkey=settings.hotkey,
        on_press=pipeline.start_recording,
        on_release=pipeline.stop_and_inject,
    )

    def on_state_change(state: PipelineState) -> None:
        tray.update_state(state)

    pipeline.set_state_callback(on_state_change)

    threading.Thread(target=pipeline.engine.warmup, daemon=True).start()

    listener.start()
    print(f"VoiceTyping running. Hotkey: {settings.hotkey}")
    print("Press Ctrl+C or use tray menu to quit.")

    try:
        tray.run()
    finally:
        listener.stop()


def _shutdown() -> None:
    pass


def show_config() -> None:
    settings = load_settings()
    path = config_path()
    print(f"Config: {path}")
    print(json.dumps(settings.model_dump(), indent=2, ensure_ascii=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="VoiceTyping — local voice input")
    parser.add_argument("--config", action="store_true", help="Show current configuration")
    parser.add_argument("--init-config", action="store_true", help="Write default config file")
    args = parser.parse_args()

    if args.config:
        show_config()
        return

    if args.init_config:
        settings = Settings()
        save_settings(settings)
        print(f"Default config written to {config_path()}")
        return

    try:
        run_app()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
