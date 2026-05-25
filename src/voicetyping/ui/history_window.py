"""Clipboard history window for voice transcription records."""

from __future__ import annotations

import queue
import threading
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk
from typing import Callable, Optional

import pyperclip

from voicetyping.history.store import HistoryEntry, HistoryStore

SCRIPT_LABELS = {
    "simplified": "简体",
    "traditional": "繁体",
}


class _HistoryPanel(tk.Toplevel):
    """History panel as a Toplevel window."""

    def __init__(
        self,
        master: tk.Misc,
        history_store: HistoryStore,
        on_inject: Optional[Callable[[str], None]] = None,
    ) -> None:
        super().__init__(master)
        self.history_store = history_store
        self.on_inject = on_inject
        self._entries: list[HistoryEntry] = []
        self._search_query = tk.StringVar(value="")
        self._search_query.trace_add("write", lambda *_: self.refresh())

        self.title("VoiceTyping 历史剪贴板")
        self.geometry("640x460")
        self.minsize(480, 360)
        self.protocol("WM_DELETE_WINDOW", self.withdraw)

        header = ttk.Label(self, text="语音转换历史记录", padding=(12, 8))
        header.pack(fill="x")

        search_frame = ttk.Frame(self, padding=(12, 0, 12, 8))
        search_frame.pack(fill="x")
        ttk.Label(search_frame, text="搜索：").pack(side="left")
        search_entry = ttk.Entry(search_frame, textvariable=self._search_query)
        search_entry.pack(side="left", fill="x", expand=True, padx=(4, 8))
        ttk.Button(search_frame, text="清除", command=self._clear_search).pack(side="left")

        body = ttk.Panedwindow(self, orient=tk.VERTICAL)
        body.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        list_frame = ttk.Frame(body)
        self._listbox = tk.Listbox(list_frame, height=8, activestyle="dotbox")
        list_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self._listbox.yview)
        self._listbox.configure(yscrollcommand=list_scroll.set)
        self._listbox.pack(side="left", fill="both", expand=True)
        list_scroll.pack(side="right", fill="y")
        self._listbox.bind("<<ListboxSelect>>", self._on_select)
        self._listbox.bind("<Double-Button-1>", lambda _e: self._copy_selected())

        detail_frame = ttk.LabelFrame(body, text="内容预览", padding=8)
        self._detail = tk.Text(detail_frame, height=8, wrap="word")
        detail_scroll = ttk.Scrollbar(detail_frame, orient="vertical", command=self._detail.yview)
        self._detail.configure(yscrollcommand=detail_scroll.set, state="disabled")
        self._detail.pack(side="left", fill="both", expand=True)
        detail_scroll.pack(side="right", fill="y")

        body.add(list_frame, weight=1)
        body.add(detail_frame, weight=2)

        buttons = ttk.Frame(self, padding=(12, 0, 12, 12))
        buttons.pack(fill="x")
        ttk.Button(buttons, text="复制", command=self._copy_selected).pack(side="left")
        ttk.Button(buttons, text="插入到光标", command=self._inject_selected).pack(side="left", padx=(8, 0))
        ttk.Button(buttons, text="删除选中", command=self._delete_selected).pack(side="left", padx=(8, 0))
        ttk.Button(buttons, text="清空历史", command=self._clear_all).pack(side="left", padx=(8, 0))
        ttk.Button(buttons, text="关闭", command=self.withdraw).pack(side="right")

        self.refresh()

    def _clear_search(self) -> None:
        self._search_query.set("")

    def refresh(self, select_first: bool = False) -> None:
        selected_id = None
        if not select_first:
            entry = self._selected_entry()
            selected_id = entry.id if entry else None

        query = self._search_query.get()
        self._entries = self.history_store.search(query)
        self._listbox.delete(0, tk.END)
        select_index = None
        for index, entry in enumerate(self._entries):
            self._listbox.insert(tk.END, self._format_entry(entry))
            if select_first and index == 0:
                select_index = 0
            elif selected_id and entry.id == selected_id:
                select_index = index

        if select_index is not None:
            self._listbox.selection_set(select_index)
            self._listbox.see(select_index)
            self._set_detail(self._entries[select_index].text)
        else:
            self._set_detail("")

    @property
    def is_visible(self) -> bool:
        try:
            return self.winfo_exists() and self.winfo_viewable()
        except tk.TclError:
            return False

    def _format_entry(self, entry: HistoryEntry) -> str:
        try:
            dt = datetime.fromisoformat(entry.created_at)
            time_label = dt.astimezone().strftime("%m-%d %H:%M")
        except ValueError:
            time_label = entry.created_at[:16]
        script = SCRIPT_LABELS.get(entry.script, entry.script)
        preview = entry.text.replace("\n", " ")
        if len(preview) > 48:
            preview = preview[:48] + "..."
        return f"[{time_label}][{script}] {preview}"

    def _selected_entry(self) -> Optional[HistoryEntry]:
        selection = self._listbox.curselection()
        if not selection:
            return None
        index = selection[0]
        if index >= len(self._entries):
            return None
        return self._entries[index]

    def _set_detail(self, text: str) -> None:
        self._detail.configure(state="normal")
        self._detail.delete("1.0", tk.END)
        self._detail.insert(tk.END, text)
        self._detail.configure(state="disabled")

    def _on_select(self, _event=None) -> None:
        entry = self._selected_entry()
        self._set_detail(entry.text if entry else "")

    def _copy_selected(self) -> None:
        entry = self._selected_entry()
        if not entry:
            messagebox.showinfo("提示", "请先选择一条历史记录。", parent=self)
            return
        pyperclip.copy(entry.text)

    def _inject_selected(self) -> None:
        entry = self._selected_entry()
        if not entry:
            messagebox.showinfo("提示", "请先选择一条历史记录。", parent=self)
            return
        if self.on_inject:
            self.on_inject(entry.text)

    def _delete_selected(self) -> None:
        entry = self._selected_entry()
        if not entry:
            messagebox.showinfo("提示", "请先选择一条历史记录。", parent=self)
            return
        self.history_store.delete(entry.id)
        self.refresh()

    def _clear_all(self) -> None:
        if not self._entries:
            return
        if messagebox.askyesno("确认", "确定清空全部历史记录吗？", parent=self):
            self.history_store.clear()
            self.refresh()


class HistoryWindow:
    """Manages a dedicated Tk thread and reusable history panel."""

    _cmd_queue: queue.Queue = queue.Queue()
    _tk_thread: Optional[threading.Thread] = None
    _ready = threading.Event()

    @classmethod
    def open(
        cls,
        history_store: HistoryStore,
        on_inject: Optional[Callable[[str], None]] = None,
    ) -> None:
        cls._ensure_tk_thread()
        cls._cmd_queue.put(("open", history_store, on_inject))

    @classmethod
    def _ensure_tk_thread(cls) -> None:
        if cls._tk_thread and cls._tk_thread.is_alive():
            return
        cls._ready.clear()
        cls._tk_thread = threading.Thread(target=cls._tk_main, daemon=True, name="HistoryWindowTk")
        cls._tk_thread.start()
        if not cls._ready.wait(timeout=5):
            print("[HistoryWindow] Failed to start UI thread.")

    @classmethod
    def _tk_main(cls) -> None:
        root = tk.Tk()
        root.withdraw()
        panel: Optional[_HistoryPanel] = None
        bound_store: Optional[HistoryStore] = None

        def on_store_change(event: str) -> None:
            cls._cmd_queue.put(("refresh", event))

        def bind_store(store: HistoryStore) -> None:
            nonlocal bound_store
            if bound_store is store:
                return
            if bound_store is not None:
                bound_store.remove_listener(on_store_change)
            store.add_listener(on_store_change)
            bound_store = store

        def handle_open(store: HistoryStore, on_inject: Optional[Callable[[str], None]]) -> None:
            nonlocal panel
            bind_store(store)
            if panel is None or not panel.winfo_exists():
                panel = _HistoryPanel(root, store, on_inject)
            else:
                panel.history_store = store
                panel.on_inject = on_inject
                panel.refresh()
            panel.deiconify()
            panel.lift()
            panel.focus_force()

        def handle_refresh(event: str) -> None:
            if panel is None or not panel.is_visible:
                return
            panel.refresh(select_first=event == "add")

        def poll_queue() -> None:
            try:
                while True:
                    cmd, *args = cls._cmd_queue.get_nowait()
                    if cmd == "open":
                        handle_open(*args)
                    elif cmd == "refresh":
                        handle_refresh(args[0] if args else "change")
            except queue.Empty:
                pass
            root.after(100, poll_queue)

        cls._ready.set()
        poll_queue()
        root.mainloop()
