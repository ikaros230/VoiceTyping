"""VoiceTyping entry point."""

from __future__ import annotations

import argparse
import json
import sys
import threading
import time

from voicetyping.audio.devices import get_device_label
from voicetyping.audio.recorder import AudioRecorder
from voicetyping.config.settings import ChineseScript, Settings, config_path, load_settings, save_settings
from voicetyping.history.store import HistoryStore
from voicetyping.hotkey.listener import HotkeyListener
from voicetyping.output.windows import WindowsTextInjector
from voicetyping.pipeline import PipelineState, VoicePipeline
from voicetyping.stt.whisper_engine import WhisperEngine
from voicetyping.hotkey.utils import format_hotkey
from voicetyping.ui.hotkey_dialog import HotkeyDialog
from voicetyping.ui.history_window import HistoryWindow
from voicetyping.ui.mic_dialog import MicDialog
from voicetyping.ui.recording_indicator import RecordingIndicator
from voicetyping.ui.tray import TrayApp


def _build_pipeline(settings: Settings, injector: WindowsTextInjector) -> VoicePipeline:
    engine = WhisperEngine(
        model_size=settings.model_size,
        device=settings.device,
        language=settings.language,
        hf_endpoint=settings.hf_endpoint,
        model_path=settings.model_path,
    )
    recorder = AudioRecorder(device=settings.input_device)
    return VoicePipeline(
        recorder=recorder,
        engine=engine,
        injector=injector,
        min_record_seconds=settings.min_record_seconds,
        chinese_script=settings.chinese_script,
        low_volume_rms=settings.low_volume_rms_threshold,
    )


def _open_settings_dialog(settings: Settings) -> None:
    """Print current config path and contents; user can edit manually."""
    path = config_path()
    print(f"\nConfig file: {path}")
    print(json.dumps(settings.model_dump(), indent=2, ensure_ascii=False))
    print("Edit the file above and restart VoiceTyping to apply changes.\n")


def run_app(settings: Settings | None = None) -> None:
    settings = settings or load_settings()
    injector = WindowsTextInjector(restore_clipboard=settings.restore_clipboard)
    pipeline = _build_pipeline(settings, injector)
    history_store = HistoryStore(max_items=settings.history_max_items)

    def on_transcription(text: str) -> None:
        history_store.add(text, settings.chinese_script)

    pipeline.set_transcription_callback(on_transcription)

    def open_history() -> None:
        HistoryWindow.open(history_store, on_inject=injector.inject)

    def set_chinese_script(script: ChineseScript) -> None:
        settings.chinese_script = script
        pipeline.chinese_script = script
        save_settings(settings)
        label = "简体中文" if script == "simplified" else "繁體中文"
        print(f"[VoiceTyping] 文字输出已切换为: {label}")

    listener = HotkeyListener(
        hotkey=settings.hotkey,
        on_press=pipeline.start_recording,
        on_release=pipeline.stop_and_inject,
    )

    def change_hotkey() -> None:
        def save_hotkey(new_hotkey: str) -> None:
            settings.hotkey = new_hotkey
            listener.set_hotkey(new_hotkey)
            save_settings(settings)
            tray.refresh_menu()
            print(f"[VoiceTyping] 快捷键已更新为: {format_hotkey(new_hotkey)}")

        HotkeyDialog.open(
            current_hotkey=settings.hotkey,
            on_save=save_hotkey,
            on_pause_listener=listener.stop,
            on_resume_listener=listener.start,
        )

    def select_microphone() -> None:
        def save_device(device_index: int | None) -> None:
            if not pipeline.set_input_device(device_index):
                print("[VoiceTyping] 录音进行中，无法切换麦克风。")
                return
            settings.input_device = device_index
            save_settings(settings)
            tray.refresh_menu()
            print(f"[VoiceTyping] 麦克风已切换为: {get_device_label(device_index)}")

        MicDialog.open(current_device=settings.input_device, on_save=save_device)

    tray = TrayApp(
        get_chinese_script=lambda: settings.chinese_script,
        get_hotkey=lambda: settings.hotkey,
        get_input_device=lambda: settings.input_device,
        on_chinese_script_change=set_chinese_script,
        on_change_hotkey=change_hotkey,
        on_select_microphone=select_microphone,
        on_open_history=open_history,
        on_quit=_shutdown,
        on_open_settings=lambda: _open_settings_dialog(settings),
    )

    low_volume_pending = {"flag": False}

    def on_state_change(state: PipelineState) -> None:
        tray.update_state(state)
        if not settings.show_recording_indicator:
            return
        if state == PipelineState.RECORDING:
            low_volume_pending["flag"] = False
            RecordingIndicator.show()
        elif state == PipelineState.TRANSCRIBING:
            if low_volume_pending["flag"]:
                low_volume_pending["flag"] = False

                def delayed_hide() -> None:
                    time.sleep(2.0)
                    RecordingIndicator.hide()

                threading.Thread(target=delayed_hide, daemon=True, name="IndicatorHide").start()
            else:
                RecordingIndicator.hide()
        elif state == PipelineState.IDLE:
            RecordingIndicator.hide()

    def on_level_update(level: float) -> None:
        if settings.show_recording_indicator:
            RecordingIndicator.update_level(level)

    def on_low_volume(_info) -> None:
        low_volume_pending["flag"] = True
        if settings.show_recording_indicator:
            RecordingIndicator.show_low_volume_warning()
        tray.notify("VoiceTyping", "音量过小，请靠近麦克风或调高系统输入音量。")

    pipeline.set_state_callback(on_state_change)
    pipeline.set_level_callback(on_level_update)
    pipeline.set_low_volume_callback(on_low_volume)

    threading.Thread(target=pipeline.engine.warmup, daemon=True).start()

    listener.start()
    print(f"VoiceTyping running. Hotkey: {settings.hotkey}")
    print("Left-click tray icon to open history clipboard.")
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
