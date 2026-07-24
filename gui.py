"""
Batch Mortal 分析工具 - 图形界面
基于 PySide6 (Qt for Python)
配置项与 config.example.yaml 对应
"""

import json
import os
import sys

from PySide6.QtCore import Qt, QProcess, Signal, Slot
from PySide6.QtGui import QFont, QColor, QTextCursor, QIntValidator
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QCheckBox,
    QComboBox,
    QPushButton,
    QPlainTextEdit,
    QScrollArea,
    QFileDialog,
    QMessageBox,
    QFrame,
    QButtonGroup,
    QStackedWidget,
)

# ============================================================
# 默认配置（与 config.example.yaml 一致）
# ============================================================
DEFAULT_CONFIG = {
    "mode": "mj",
    "mj": {"nickname": "", "limit": 30, "modes": "12"},
    "th": {"nickname": "", "limit": 10, "modes": "4p-south"},
    "model_tag": "4.1b",
    "review_language": "zh-CN",
    "review_ui": "killerducky",
    "analyze_bad_move_rate": True,
    "headless": True,
    "dry_run": False,
    "save_screenshot": False,
    "save_local_paipu": False,
    "output": "xlsx",
    "retry": 3,
    "proxy": "",
    "prewarm_standby": False,
    "unsafe_parallel_review": False,
    "plot": "none",
    "plot_limit": "",
}

MJ_MODE_OPTIONS = [
    ("四人金南", "9"),
    ("四人玉南", "12"),
    ("四人王座南", "16"),
    ("四人金东", "8"),
    ("四人玉东", "11"),
    ("四人王座东", "15"),
]

TH_MODE_OPTIONS = [
    ("四人半庄（南场）", "4p-south"),
    ("四人东风（东场）", "4p-east"),
    ("三人半庄（南场）", "3p-south"),
    ("三人东风（东场）", "3p-east"),
]

# ─── Fluent UI 风格样式表 ───
FLUENT_STYLE = """
QMainWindow {
    background-color: #f5f5f5;
}
QGroupBox {
    background-color: #ffffff;
    border: 1px solid #e8e8e8;
    border-radius: 12px;
    margin-top: 16px;
    padding: 18px 16px 12px 16px;
    font-size: 13px;
    font-weight: 600;
    color: #1a1a1a;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 16px;
    padding: 2px 10px;
    color: #2563eb;
    font-size: 13px;
}
QLabel {
    color: #374151;
    font-size: 13px;
}
QLineEdit {
    background-color: #f9fafb;
    color: #111827;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 13px;
}
QLineEdit:focus {
    border-color: #2563eb;
    background-color: #ffffff;
}
QLineEdit:hover {
    border-color: #d1d5db;
}
QComboBox {
    background-color: #f9fafb;
    color: #111827;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 13px;
}
QComboBox:focus {
    border-color: #2563eb;
    background-color: #ffffff;
}
QComboBox:hover {
    border-color: #d1d5db;
}
QComboBox::drop-down {
    border: none;
    padding-right: 8px;
    width: 20px;
}
QComboBox::down-arrow {
    width: 10px;
    height: 10px;
}
QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #111827;
    selection-background-color: #dbeafe;
    selection-color: #111827;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    padding: 6px;
    outline: none;
    show-decoration-selected: 1;
}
QComboBox QAbstractItemView::item {
    padding: 6px 12px;
    border-radius: 4px;
    min-height: 24px;
}
QComboBox QAbstractItemView::item:hover {
    background-color: #f3f4f6;
}
QComboBox QAbstractItemView::item:selected {
    background-color: #dbeafe;
    color: #1e40af;
}
QCheckBox {
    color: #374151;
    font-size: 13px;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #9ca3af;
    border-radius: 5px;
    background-color: #ffffff;
}
QCheckBox::indicator:checked {
    background-color: #2563eb;
    border-color: #2563eb;
}
QCheckBox::indicator:hover {
    border-color: #4b5563;
}
QPushButton {
    background-color: #f9fafb;
    color: #374151;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    padding: 7px 18px;
    font-size: 13px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #f3f4f6;
    border-color: #d1d5db;
}
QPushButton:pressed {
    background-color: #e5e7eb;
}
QPushButton#runBtn {
    background-color: #2563eb;
    color: #ffffff;
    font-weight: 600;
    font-size: 15px;
    padding: 10px 32px;
    border: none;
    border-radius: 10px;
}
QPushButton#runBtn:hover {
    background-color: #1d4ed8;
}
QPushButton#runBtn:pressed {
    background-color: #1e40af;
}
QPushButton#runBtn:disabled {
    background-color: #e5e7eb;
    color: #9ca3af;
}
QPlainTextEdit {
    background-color: #ffffff;
    color: #1f2937;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    font-family: "Cascadia Code", "Consolas", "Fira Code", monospace;
    font-size: 12px;
    padding: 10px;
}
QPlainTextEdit:focus {
    border-color: #2563eb;
}
QScrollBar:vertical {
    background: transparent;
    width: 8px;
    border-radius: 4px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background: #d1d5db;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #9ca3af;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: transparent;
}
QScrollBar:horizontal {
    background: transparent;
    height: 8px;
    border-radius: 4px;
    margin: 2px;
}
QScrollBar::handle:horizontal {
    background: #d1d5db;
    border-radius: 4px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover {
    background: #9ca3af;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
}
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: transparent;
}
QAbstractScrollArea::corner {
    background: transparent;
}
QToolTip {
    background-color: #ffffff;
    color: #374151;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}
"""


class BatchMortalGUI(QMainWindow):
    """Batch Mortal 主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🀄  Batch Mortal - 雀魂 / 天凤牌谱批量分析")
        self._set_app_icon()
        self.resize(720, 780)
        self.setMinimumSize(640, 700)

        self._process: QProcess | None = None

        # ── 控件引用 ──
        # 数据源切换
        self._btn_mj: QPushButton = None
        self._btn_th: QPushButton = None
        self._source_stack: QStackedWidget = None

        # 雀魂字段
        self._mj_nickname: QLineEdit = None
        self._mj_limit: QLineEdit = None
        self._mj_mode_combo: QComboBox = None

        # 天凤字段
        self._th_nickname: QLineEdit = None
        self._th_limit: QLineEdit = None
        self._th_mode_combo: QComboBox = None

        # 通用字段
        self._model_combo: QComboBox = None
        self._lang_combo: QComboBox = None
        self._ui_combo: QComboBox = None
        self._retry_edit: QLineEdit = None
        self._proxy_edit: QLineEdit = None
        self._output_combo: QComboBox = None
        self._plot_combo: QComboBox = None
        self._plot_limit_edit: QLineEdit = None

        # 布尔复选框
        self._bool: dict[str, QCheckBox] = {}

        # 日志和按钮
        self._output_text: QPlainTextEdit = None
        self._run_btn: QPushButton = None
        self._btn_load: QPushButton = None
        self._btn_save: QPushButton = None
        self._btn_default: QPushButton = None

        self._build_ui()
        self._apply_config(self._load_settings())
        self._center()

    # ===================== 构建 UI =====================

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 12, 16, 12)
        root.setSpacing(0)

        title = QLabel("🀄  Batch Mortal — 雀魂 / 天凤牌谱批量分析")
        title.setFont(QFont("Microsoft YaHei UI", 15, QFont.Bold))
        title.setStyleSheet("color: #111827; padding-bottom: 6px;")
        title.setAlignment(Qt.AlignCenter)
        root.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        sw = QWidget()
        sw.setStyleSheet("background: transparent;")
        sl = QVBoxLayout(sw)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setSpacing(8)

        sl.addWidget(self._build_source_group())
        sl.addWidget(self._build_analysis_group())
        sl.addWidget(self._build_browser_group())
        sl.addWidget(self._build_output_group())

        self._advanced_group = self._build_advanced_group()
        self._advanced_group.setVisible(False)
        sl.addWidget(self._advanced_group)
        sl.addStretch()

        scroll.setWidget(sw)
        root.addWidget(scroll, 1)
        root.addLayout(self._build_button_bar())
        root.addWidget(self._build_log_area())

        # 工程署名
        footer = QLabel("Powered by <a href='https://github.com/myouo/batchmortal' style='color:#2563eb;'>BatchMortal</a> · GitHub")
        footer.setAlignment(Qt.AlignCenter)
        footer.setOpenExternalLinks(True)
        footer.setStyleSheet("color: #9ca3af; font-size: 11px; padding-top: 2px;")
        root.addWidget(footer)

        # 所有下拉框弹出宽度自适应内容
        for attr in ("_mj_mode_combo", "_th_mode_combo", "_model_combo",
                     "_lang_combo", "_ui_combo", "_output_combo", "_plot_combo"):
            cb: QComboBox = getattr(self, attr, None)
            if cb:
                cb.setSizeAdjustPolicy(QComboBox.AdjustToContents)

    def _make_group(self, title: str) -> QGroupBox:
        gb = QGroupBox(title)
        gb.setFont(QFont("Microsoft YaHei UI", 10, QFont.Bold))
        return gb

    def _hint(self, text: str) -> QLabel:
        lb = QLabel(text)
        lb.setStyleSheet("color: #9ca3af; font-size: 12px;")
        return lb

    # ─── 数据源 ───

    def _build_source_group(self) -> QGroupBox:
        gb = self._make_group("数据源")
        v = QVBoxLayout(gb)

        radio_row = QHBoxLayout()
        self._btn_mj = QPushButton("雀魂 (Mahjong Soul)")
        self._btn_mj.setCheckable(True)
        self._btn_mj.setChecked(True)
        self._btn_mj.setCursor(Qt.PointingHandCursor)
        self._btn_mj.setStyleSheet(
            "QPushButton { color: #6b7280; font-size: 13px; font-weight: 600;"
            "background-color: #f9fafb; border: 2px solid #d1d5db;"
            "border-radius: 10px; padding: 8px 24px; }"
            "QPushButton:checked { color: #ffffff; background-color: #2563eb;"
            "border-color: #2563eb; }"
            "QPushButton:hover:!checked { background-color: #f3f4f6;"
            "border-color: #9ca3af; color: #374151; }"
        )
        self._btn_th = QPushButton("天凤 (Tenhou)")
        self._btn_th.setCheckable(True)
        self._btn_th.setCursor(Qt.PointingHandCursor)
        self._btn_th.setStyleSheet(
            "QPushButton { color: #6b7280; font-size: 13px; font-weight: 600;"
            "background-color: #f9fafb; border: 2px solid #d1d5db;"
            "border-radius: 10px; padding: 8px 24px; }"
            "QPushButton:checked { color: #ffffff; background-color: #2563eb;"
            "border-color: #2563eb; }"
            "QPushButton:hover:!checked { background-color: #f3f4f6;"
            "border-color: #9ca3af; color: #374151; }"
        )

        group = QButtonGroup(self)
        group.addButton(self._btn_mj, 0)
        group.addButton(self._btn_th, 1)
        group.idClicked.connect(self._on_source_changed)

        radio_row.addWidget(self._btn_mj)
        radio_row.addWidget(self._btn_th)
        radio_row.addStretch()
        v.addLayout(radio_row)

        # Stacked: 雀魂 / 天凤 面板
        self._source_stack = QStackedWidget()
        self._source_stack.addWidget(self._build_mj_panel())
        self._source_stack.addWidget(self._build_th_panel())
        v.addWidget(self._source_stack)
        return gb

    def _build_mj_panel(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 4, 0, 0)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("玩家昵称："))
        self._mj_nickname = QLineEdit()
        self._mj_nickname.setPlaceholderText("雀魂玩家昵称")
        self._mj_nickname.setMinimumWidth(180)
        row1.addWidget(self._mj_nickname)

        row1.addSpacing(16)
        row1.addWidget(QLabel("拉取条数："))
        self._mj_limit = QLineEdit("30")
        self._mj_limit.setValidator(QIntValidator(1, 200))
        self._mj_limit.setFixedWidth(56)
        self._mj_limit.setAlignment(Qt.AlignCenter)
        row1.addWidget(self._mj_limit)

        row1.addSpacing(16)
        row1.addWidget(QLabel("对局模式："))
        self._mj_mode_combo = QComboBox()
        for label, key in MJ_MODE_OPTIONS:
            self._mj_mode_combo.addItem(label, key)
        self._mj_mode_combo.setFixedWidth(140)
        row1.addWidget(self._mj_mode_combo)
        row1.addStretch()
        v.addLayout(row1)
        return w

    def _build_th_panel(self) -> QWidget:
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 4, 0, 0)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("玩家昵称："))
        self._th_nickname = QLineEdit()
        self._th_nickname.setPlaceholderText("天凤玩家昵称")
        self._th_nickname.setMinimumWidth(180)
        row1.addWidget(self._th_nickname)

        row1.addSpacing(16)
        row1.addWidget(QLabel("拉取条数："))
        self._th_limit = QLineEdit("10")
        self._th_limit.setValidator(QIntValidator(1, 200))
        self._th_limit.setFixedWidth(56)
        self._th_limit.setAlignment(Qt.AlignCenter)
        row1.addWidget(self._th_limit)

        row1.addSpacing(16)
        row1.addWidget(QLabel("对局模式："))
        self._th_mode_combo = QComboBox()
        for label, key in TH_MODE_OPTIONS:
            self._th_mode_combo.addItem(label, key)
        self._th_mode_combo.setFixedWidth(160)
        row1.addWidget(self._th_mode_combo)
        row1.addStretch()
        v.addLayout(row1)
        return w

    @Slot(int)
    def _on_source_changed(self, idx: int):
        self._source_stack.setCurrentIndex(idx)

    # ─── 分析选项 ───

    def _build_analysis_group(self) -> QGroupBox:
        gb = self._make_group("分析选项")

        # 模型 + 语言 + UI + 重试
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Mortal 模型："))
        self._model_combo = QComboBox()
        self._model_combo.addItems(["4.1b", "4b"])
        self._model_combo.setFixedWidth(80)
        row1.addWidget(self._model_combo)

        row1.addSpacing(16)
        row1.addWidget(QLabel("页面语言："))
        self._lang_combo = QComboBox()
        self._lang_combo.addItems(["zh-CN (简体中文)", "en (English)", "ja (日本語)", "ko (한국어)"])
        self._lang_combo.setFixedWidth(150)
        row1.addWidget(self._lang_combo)
        row1.addStretch()

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("结果 UI："))
        self._ui_combo = QComboBox()
        self._ui_combo.addItems(["KillerDucky（交互式）", "Classic（经典长页面）"])
        self._ui_combo.setFixedWidth(180)
        row2.addWidget(self._ui_combo)

        row2.addSpacing(16)
        row2.addWidget(QLabel("失败重试："))
        self._retry_edit = QLineEdit("3")
        self._retry_edit.setValidator(QIntValidator(0, 10))
        self._retry_edit.setFixedWidth(56)
        self._retry_edit.setAlignment(Qt.AlignCenter)
        row2.addWidget(self._retry_edit)
        row2.addStretch()

        cb_bad = QCheckBox("分析恶手率（5% / 10%）")
        self._bool["analyze_bad_move_rate"] = cb_bad

        v = QVBoxLayout(gb)
        v.addLayout(row1)
        v.addLayout(row2)
        v.addWidget(cb_bad)
        return gb

    # ─── 浏览器 & 网络 ───

    def _build_browser_group(self) -> QGroupBox:
        gb = self._make_group("浏览器 & 网络")

        row1 = QHBoxLayout()
        cb_h = QCheckBox("无头模式（后台运行浏览器）")
        self._bool["headless"] = cb_h
        row1.addWidget(cb_h)
        cb_d = QCheckBox("Dry Run（只打印 URL，不分析）")
        self._bool["dry_run"] = cb_d
        row1.addWidget(cb_d)
        row1.addStretch()

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("代理服务器："))
        self._proxy_edit = QLineEdit()
        self._proxy_edit.setPlaceholderText("留空则自动检测系统代理")
        self._proxy_edit.setMinimumWidth(260)
        row2.addWidget(self._proxy_edit)
        row2.addWidget(self._hint("例: http://127.0.0.1:7890"))
        row2.addStretch()

        v = QVBoxLayout(gb)
        v.addLayout(row1)
        v.addLayout(row2)
        return gb

    # ─── 输出选项 ───

    def _build_output_group(self) -> QGroupBox:
        gb = self._make_group("输出选项")

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("导出格式："))
        self._output_combo = QComboBox()
        self._output_combo.addItems(["xlsx", "csv"])
        self._output_combo.setFixedWidth(82)
        row1.addWidget(self._output_combo)

        row1.addSpacing(16)
        row1.addWidget(QLabel("绘图方式："))
        self._plot_combo = QComboBox()
        self._plot_combo.addItems(["none", "html", "png", "both"])
        self._plot_combo.setFixedWidth(90)
        row1.addWidget(self._plot_combo)

        row1.addSpacing(16)
        row1.addWidget(QLabel("取最近 N 条："))
        self._plot_limit_edit = QLineEdit()
        self._plot_limit_edit.setPlaceholderText("全部")
        self._plot_limit_edit.setFixedWidth(56)
        self._plot_limit_edit.setAlignment(Qt.AlignCenter)
        row1.addWidget(self._plot_limit_edit)
        row1.addStretch()

        row2 = QHBoxLayout()
        cb_ss = QCheckBox("保存分析结果截图")
        self._bool["save_screenshot"] = cb_ss
        row2.addWidget(cb_ss)
        cb_lp = QCheckBox("保存本地牌谱 HTML")
        self._bool["save_local_paipu"] = cb_lp
        row2.addWidget(cb_lp)
        row2.addStretch()

        v = QVBoxLayout(gb)
        v.addLayout(row1)
        v.addLayout(row2)
        return gb

    # ─── 高级选项 ───

    def _build_advanced_group(self) -> QGroupBox:
        gb = self._make_group("高级选项")
        row = QHBoxLayout()
        cb_pw = QCheckBox("双窗口接力（实验性）")
        self._bool["prewarm_standby"] = cb_pw
        row.addWidget(cb_pw)
        cb_pr = QCheckBox("跳过受控提交协调（易触发 Cloudflare）")
        self._bool["unsafe_parallel_review"] = cb_pr
        row.addWidget(cb_pr)
        row.addStretch()
        gb.setLayout(row)
        return gb

    # ─── 按钮栏 ───

    def _build_button_bar(self) -> QHBoxLayout:
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 8, 0, 4)

        self._btn_load = QPushButton("📂 加载配置")
        self._btn_load.clicked.connect(self._load_config_file)
        layout.addWidget(self._btn_load)

        self._btn_save = QPushButton("💾 保存配置")
        self._btn_save.clicked.connect(self._save_config_file)
        layout.addWidget(self._btn_save)

        self._btn_default = QPushButton("🔄 恢复默认")
        self._btn_default.clicked.connect(self._load_defaults)
        layout.addWidget(self._btn_default)

        self._btn_advanced_toggle = QPushButton("⚙ 高级选项")
        self._btn_advanced_toggle.setCheckable(True)
        self._btn_advanced_toggle.setCursor(Qt.PointingHandCursor)
        self._btn_advanced_toggle.setStyleSheet(
            "QPushButton { color: #6b7280; background-color: #f9fafb;"
            "border: 2px solid #e5e7eb; border-radius: 8px; padding: 7px 18px;"
            "font-size: 13px; font-weight: 500; }"
            "QPushButton:checked { color: #ffffff; background-color: #2563eb;"
            "border-color: #2563eb; }"
            "QPushButton:hover:!checked { background-color: #f3f4f6;"
            "border-color: #d1d5db; color: #374151; }"
        )
        self._btn_advanced_toggle.clicked.connect(self._on_advanced_toggle)
        layout.addWidget(self._btn_advanced_toggle)

        layout.addStretch()

        self._run_btn = QPushButton("▶  开始分析")
        self._run_btn.setObjectName("runBtn")
        self._run_btn.clicked.connect(self._run_analysis)
        layout.addWidget(self._run_btn)
        return layout

    @Slot()
    def _on_advanced_toggle(self):
        visible = self._btn_advanced_toggle.isChecked()
        self._advanced_group.setVisible(visible)

    # ─── 日志区域 ───

    def _build_log_area(self) -> QGroupBox:
        gb = self._make_group("运行日志")
        v = QVBoxLayout(gb)
        v.setContentsMargins(4, 4, 4, 6)
        self._output_text = QPlainTextEdit()
        self._output_text.setReadOnly(True)
        self._output_text.setMinimumHeight(140)
        v.addWidget(self._output_text)
        return gb

    # ===================== 逻辑 =====================

    def _set_app_icon(self):
        from PySide6.QtGui import QIcon
        base = self._get_bundle_dir()
        icon_path = os.path.join(base, "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def _center(self):
        screen = self.screen().availableGeometry()
        geo = self.frameGeometry()
        geo.moveCenter(screen.center())
        self.move(geo.topLeft())

    def _settings_path(self) -> str:
        exe_dir = self._get_bundle_dir() if hasattr(self, '_get_bundle_dir') else os.path.dirname(os.path.abspath(__file__))
        # 开发时放项目根目录，打包后放 exe 旁边
        if getattr(sys, "frozen", False):
            exe_dir = os.path.dirname(sys.executable)
        return os.path.join(exe_dir, "_gui_settings.json")

    def _load_settings(self) -> dict:
        path = self._settings_path()
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return dict(DEFAULT_CONFIG)

    def _save_settings(self):
        try:
            config = self._gather_config()
            with open(self._settings_path(), "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def closeEvent(self, event):
        self._save_settings()
        super().closeEvent(event)

    def _log(self, message: str):
        if self._output_text:
            self._output_text.appendPlainText(message)
            c = self._output_text.textCursor()
            c.movePosition(QTextCursor.End)
            self._output_text.setTextCursor(c)

    def _gather_config(self) -> dict:
        is_mj = self._btn_mj.isChecked()

        # 语言映射
        lang_map = {
            "zh-CN (简体中文)": "zh-CN",
            "en (English)": "en",
            "ja (日本語)": "ja",
            "ko (한국어)": "ko",
        }
        ui_map = {
            "KillerDucky（交互式）": "killerducky",
            "Classic（经典长页面）": "classic",
        }

        if is_mj:
            mj_idx = self._mj_mode_combo.currentIndex()
            mj_mode_key = MJ_MODE_OPTIONS[mj_idx][1] if 0 <= mj_idx < len(MJ_MODE_OPTIONS) else "12"
            return {
                "mode": "mj",
                "mj": {
                    "nickname": self._mj_nickname.text().strip(),
                    "limit": int(self._mj_limit.text() or "30"),
                    "modes": mj_mode_key,
                },
                "model_tag": self._model_combo.currentText(),
                "review_language": lang_map.get(self._lang_combo.currentText(), "zh-CN"),
                "review_ui": ui_map.get(self._ui_combo.currentText(), "killerducky"),
                "analyze_bad_move_rate": self._bool["analyze_bad_move_rate"].isChecked(),
                "headless": self._bool["headless"].isChecked(),
                "dry_run": self._bool["dry_run"].isChecked(),
                "save_screenshot": self._bool["save_screenshot"].isChecked(),
                "save_local_paipu": self._bool["save_local_paipu"].isChecked(),
                "output": self._output_combo.currentText(),
                "retry": int(self._retry_edit.text() or "3"),
                "proxy": self._proxy_edit.text().strip() or None,
                "prewarm_standby": self._bool["prewarm_standby"].isChecked(),
                "unsafe_parallel_review": self._bool["unsafe_parallel_review"].isChecked(),
                "plot": self._plot_combo.currentText(),
                "plot_limit": self._plot_limit_edit.text().strip() or None,
            }
        else:
            th_idx = self._th_mode_combo.currentIndex()
            th_mode_key = TH_MODE_OPTIONS[th_idx][1] if 0 <= th_idx < len(TH_MODE_OPTIONS) else "4p-south"
            return {
                "mode": "th",
                "th": {
                    "nickname": self._th_nickname.text().strip(),
                    "limit": int(self._th_limit.text() or "10"),
                    "modes": th_mode_key,
                },
                "model_tag": self._model_combo.currentText(),
                "review_language": lang_map.get(self._lang_combo.currentText(), "zh-CN"),
                "review_ui": ui_map.get(self._ui_combo.currentText(), "killerducky"),
                "analyze_bad_move_rate": self._bool["analyze_bad_move_rate"].isChecked(),
                "headless": self._bool["headless"].isChecked(),
                "dry_run": self._bool["dry_run"].isChecked(),
                "save_screenshot": self._bool["save_screenshot"].isChecked(),
                "save_local_paipu": self._bool["save_local_paipu"].isChecked(),
                "output": self._output_combo.currentText(),
                "retry": int(self._retry_edit.text() or "3"),
                "proxy": self._proxy_edit.text().strip() or None,
                "prewarm_standby": self._bool["prewarm_standby"].isChecked(),
                "unsafe_parallel_review": self._bool["unsafe_parallel_review"].isChecked(),
                "plot": self._plot_combo.currentText(),
                "plot_limit": self._plot_limit_edit.text().strip() or None,
            }

    def _apply_config(self, config: dict):
        is_mj = str(config.get("mode", "mj")).lower() in ("mj", "0")
        self._btn_mj.setChecked(is_mj)
        self._btn_th.setChecked(not is_mj)
        self._source_stack.setCurrentIndex(0 if is_mj else 1)

        # 语言 / UI combo 反向映射
        lang_rev = {"zh-CN": 0, "en": 1, "ja": 2, "ko": 3}
        ui_rev = {"killerducky": 0, "classic": 1}

        lang_val = str(config.get("review_language", "zh-CN"))
        self._lang_combo.setCurrentIndex(lang_rev.get(lang_val, 0))
        ui_val = str(config.get("review_ui", "killerducky"))
        self._ui_combo.setCurrentIndex(ui_rev.get(ui_val, 0))

        self._model_combo.setCurrentIndex(0 if str(config.get("model_tag", "4.1b")) != "4b" else 1)
        self._retry_edit.setText(str(int(config.get("retry", 3))))
        self._proxy_edit.setText(str(config.get("proxy") or ""))
        self._plot_limit_edit.setText(str(config.get("plot_limit") or ""))

        out_idx = self._output_combo.findText(str(config.get("output", "xlsx")))
        if out_idx >= 0:
            self._output_combo.setCurrentIndex(out_idx)
        plot_idx = self._plot_combo.findText(str(config.get("plot", "both")))
        if plot_idx >= 0:
            self._plot_combo.setCurrentIndex(plot_idx)

        for key, cb in self._bool.items():
            cb.setChecked(bool(config.get(key, DEFAULT_CONFIG.get(key, False))))

        # MJ 子配置
        mj = config.get("mj", {}) or {}
        self._mj_nickname.setText(str(mj.get("nickname", "")))
        self._mj_limit.setText(str(int(mj.get("limit", 30))))
        mj_mode = str(mj.get("modes", "12"))
        for i, (_, k) in enumerate(MJ_MODE_OPTIONS):
            if k == mj_mode:
                self._mj_mode_combo.setCurrentIndex(i)
                break

        # TH 子配置
        th = config.get("th", {}) or {}
        self._th_nickname.setText(str(th.get("nickname", "")))
        self._th_limit.setText(str(int(th.get("limit", 10))))
        th_mode = str(th.get("modes", "4p-south"))
        for i, (_, k) in enumerate(TH_MODE_OPTIONS):
            if k == th_mode:
                self._th_mode_combo.setCurrentIndex(i)
                break

    @Slot()
    def _load_defaults(self):
        self._apply_config(DEFAULT_CONFIG)
        self._log("已恢复默认配置。")

    @Slot()
    def _load_config_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择配置文件", "", "YAML 文件 (*.yaml *.yml);;所有文件 (*)"
        )
        if not path:
            return
        try:
            from batchmortal.config import load_config
            config = load_config(path)
            if not config:
                QMessageBox.warning(self, "警告", f"配置文件为空或无法解析：\n{path}")
                return
            self._apply_config(config)
            self._log(f"已加载配置：{path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载配置文件失败：\n{e}")

    @Slot()
    def _save_config_file(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "保存配置文件", "my_config.yaml",
            "YAML 文件 (*.yaml);;所有文件 (*)"
        )
        if not path:
            return
        try:
            config = self._gather_config()
            content = self._config_to_yaml(config)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            self._log(f"配置已保存：{path}")
            QMessageBox.information(self, "成功", f"配置已保存到：\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存配置文件失败：\n{e}")

    @staticmethod
    def _config_to_yaml(config: dict) -> str:
        proxy_val = config.get("proxy")
        proxy_line = f'  proxy: "{proxy_val}"' if proxy_val else "  # proxy: \"\""
        plot_limit_val = config.get("plot_limit")
        plot_limit_line = f"plot_limit: {plot_limit_val}" if plot_limit_val else "# plot_limit: 50"

        is_mj = config["mode"] == "mj"
        if is_mj:
            mj = config.get("mj", {})
            source_block = f"""mj:
  nickname: "{mj.get('nickname', '')}"
  limit: {mj.get('limit', 30)}
  modes: "{mj.get('modes', '12')}" """
        else:
            th = config.get("th", {})
            source_block = f"""th:
  nickname: "{th.get('nickname', '')}"
  limit: {th.get('limit', 10)}
  modes: "{th.get('modes', '4p-south')}" """

        return f'''# ==== Batch Mortal 分析脚本配置文件 ====
# 由 GUI 工具生成

mode: "{config['mode']}"

{source_block}

model_tag: "{config['model_tag']}"
review_language: "{config['review_language']}"
review_ui: "{config['review_ui']}"
analyze_bad_move_rate: {str(config['analyze_bad_move_rate']).lower()}
headless: {str(config['headless']).lower()}
dry_run: {str(config['dry_run']).lower()}
save_screenshot: {str(config['save_screenshot']).lower()}
save_local_paipu: {str(config['save_local_paipu']).lower()}
output: "{config['output']}"
retry: {config['retry']}
{proxy_line}
prewarm_standby: {str(config['prewarm_standby']).lower()}
unsafe_parallel_review: {str(config['unsafe_parallel_review']).lower()}
plot: "{config['plot']}"
{plot_limit_line}
'''

    # ===================== 运行分析 =====================

    @staticmethod
    def _get_bundle_dir() -> str:
        if getattr(sys, "frozen", False):
            return sys._MEIPASS
        return os.path.dirname(os.path.abspath(__file__))

    @Slot()
    def _run_analysis(self):
        config = self._gather_config()

        is_mj = config["mode"] == "mj"
        sub = config.get("mj" if is_mj else "th", {})
        if not sub.get("nickname", "").strip():
            QMessageBox.warning(self, "缺少参数", "请输入玩家昵称！")
            return

        exe_dir = self._get_bundle_dir()
        tmp_config_path = os.path.join(exe_dir, "_gui_config.yaml")
        try:
            content = self._config_to_yaml(config)
            with open(tmp_config_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法写入临时配置文件：\n{e}")
            return

        self._run_btn.setEnabled(False)
        self._run_btn.setText("⏳  分析中...")
        self._btn_load.setEnabled(False)
        self._btn_save.setEnabled(False)
        self._btn_default.setEnabled(False)

        self._output_text.clear()
        self._log("=" * 50)
        self._log(f"数据源：{'雀魂' if is_mj else '天凤'}")
        self._log(f"玩家：{sub.get('nickname', '')}")
        self._log(f"模式：{sub.get('modes', '')}")
        self._log(f"条数：{sub.get('limit', '')}")
        self._log("=" * 50)
        self._log("正在启动分析...\n")

        self._process = QProcess(self)
        self._process.setWorkingDirectory(exe_dir)
        self._process.setProcessChannelMode(QProcess.MergedChannels)
        self._process.readyReadStandardOutput.connect(self._on_process_output)
        self._process.finished.connect(self._on_process_finished)

        if getattr(sys, "frozen", False):
            # 打包后：exe 自身 + --config 触发 CLI 模式
            self._process.start(sys.executable, ["--config", tmp_config_path])
        else:
            # 开发时：python main.py --config
            main_py = os.path.join(exe_dir, "main.py")
            self._process.start(sys.executable, [main_py, "--config", tmp_config_path])

    @Slot()
    def _on_process_output(self):
        if self._process:
            data = self._process.readAllStandardOutput()
            text = data.data().decode("utf-8", errors="replace")
            for line in text.splitlines():
                if line.strip():
                    self._log(line.rstrip())

    @Slot(int)
    def _on_process_finished(self, exit_code: int):
        if exit_code == 0:
            self._log("\n✅ 分析完成！")
            QMessageBox.information(self, "完成", "分析已成功完成！")
        else:
            self._log(f"\n❌ 进程退出，返回码：{exit_code}")
            QMessageBox.critical(self, "错误", f"分析过程出错，返回码：{exit_code}")

        self._run_btn.setEnabled(True)
        self._run_btn.setText("▶  开始分析")
        self._btn_load.setEnabled(True)
        self._btn_save.setEnabled(True)
        self._btn_default.setEnabled(True)


def main():
    # CLI 模式：由 QProcess 子进程带 --config 启动时，直接运行分析
    if "--config" in sys.argv:
        import main as main_module
        main_module.main()
        return

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(FLUENT_STYLE)
    window = BatchMortalGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
