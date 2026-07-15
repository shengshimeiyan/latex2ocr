# -*- coding: utf-8 -*-

# 现代 UI 界面 - SimpleTeX 风格白色主题
# 简洁白色、卡片式布局、圆角按钮、蓝色强调色

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QFont, QIcon
from PyQt5 import QtWebEngineWidgets


# ============ 全局样式表 ============
GLOBAL_STYLESHEET = """
/* ---------- 主窗口 ---------- */
QMainWindow {
    background-color: #f5f6fa;
}

QWidget#centralwidget {
    background-color: #f5f6fa;
}

/* ---------- 卡片区域标题 ---------- */
QLabel#section_header {
    color: #8888aa;
    font-weight: 600;
    background: transparent;
    border: none;
    padding: 0px;
    margin: 0px;
    line-height: 1;
}

/* ---------- 顶部工具栏 ---------- */
QFrame#toolbar {
    background-color: #ffffff;
    border: 1px solid #e8e8ef;
    border-radius: 12px;
    padding: 8px 16px;
}

/* ---------- 通用按钮 ---------- */
QPushButton {
    background-color: #ffffff;
    color: #333344;
    border: 1px solid #d8d8e3;
    border-radius: 8px;
    padding: 10px 24px;
    font-weight: 500;
    min-height: 24px;
}
QPushButton:hover {
    background-color: #f0f0f8;
    color: #1a1a2e;
    border-color: #b0b0cc;
}
QPushButton:pressed {
    background-color: #e8e8f0;
}
QPushButton:disabled {
    background-color: #f5f5f8;
    color: #b0b0c0;
    border-color: #e0e0e8;
}

/* ---------- 主要操作按钮（截屏） ---------- */
QPushButton#screenshotButton {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4f6ef7, stop:1 #6c5ce7);
    color: #ffffff;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 12px 32px;
}
QPushButton#screenshotButton:hover {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #5f7eff, stop:1 #7c6cf7);
}
QPushButton#screenshotButton:pressed {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #3f5ee7, stop:1 #5c4cd7);
}

QPushButton#recognize_button {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #3b82f6, stop:1 #6366f1);
    color: #ffffff;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 12px 32px;
}
QPushButton#recognize_button:hover {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4b92ff, stop:1 #7376f1);
}
QPushButton#recognize_button:disabled {
    background-color: #e0e0e8;
    color: #a0a0b0;
}

/* ---------- 下拉框 ---------- */
QComboBox {
    background-color: #ffffff;
    color: #333344;
    border: 1px solid #d8d8e3;
    border-radius: 8px;
    padding: 10px 16px;
    min-width: 160px;
}
QComboBox:hover {
    border-color: #4f6ef7;
}
QComboBox::drop-down {
    border: none;
    width: 32px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 7px solid #8888aa;
    margin-right: 10px;
}
QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #333344;
    border: 1px solid #d8d8e3;
    border-radius: 8px;
    selection-background-color: #eef0ff;
    selection-color: #1a1a2e;
    outline: none;
    padding: 4px;
}

/* ---------- 卡片容器 ---------- */
QFrame#card {
    background-color: #ffffff;
    border: 1px solid #e8e8ef;
    border-radius: 12px;
}

/* ---------- 预览标签 ---------- */
QLabel#imageLabel {
    background-color: #fafafc;
    border: 2px dashed #d0d0dd;
    border-radius: 10px;
    color: #a0a0b8;
}
QLabel#latexLabel {
    background-color: #fafafc;
    border: 2px dashed #d0d0dd;
    border-radius: 10px;
    color: #a0a0b8;
}

/* ---------- 文本编辑框 ---------- */
QPlainTextEdit {
    background-color: #fafafc;
    color: #1a1a2e;
    border: 1px solid #e8e8ef;
    border-radius: 10px;
    padding: 12px 16px;
    font-family: "Consolas", "Fira Code", monospace;
    selection-background-color: #dce0ff;
}

/* ---------- 状态标签 ---------- */
QLabel#status_label {
    color: #4f6ef7;
    padding: 4px 8px;
}

/* ---------- 分隔线 ---------- */
QFrame#separator {
    background-color: #e8e8ef;
    max-height: 1px;
}

/* ---------- 关于菜单按钮 ---------- */
QPushButton#aboutButton {
    background-color: transparent;
    border: 1px solid transparent;
    color: #8888aa;
    padding: 8px 14px;
}
QPushButton#aboutButton:hover {
    color: #333344;
    background-color: #f0f0f8;
    border-color: #d8d8e3;
    border-radius: 8px;
}

/* ---------- 设置按钮 ---------- */
QPushButton#settingsButton {
    background-color: transparent;
    border: 1px solid transparent;
    color: #8888aa;
    padding: 8px 14px;
}
QPushButton#settingsButton:hover {
    color: #333344;
    background-color: #f0f0f8;
    border-color: #d8d8e3;
    border-radius: 8px;
}

/* ---------- 菜单 ---------- */
QMenu {
    background-color: #ffffff;
    color: #333344;
    border: 1px solid #e8e8ef;
    border-radius: 8px;
    padding: 6px;
}
QMenu::item {
    padding: 10px 28px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: #eef0ff;
    color: #1a1a2e;
}

/* ---------- 滚动条 ---------- */
QScrollBar:vertical {
    background: #f5f6fa;
    width: 10px;
    border-radius: 5px;
}
QScrollBar::handle:vertical {
    background: #d0d0dd;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #b0b0cc;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""


class MainWindowUI(object):
    """主窗口的用户界面类 - SimpleTeX 风格白色主题"""

    def __init__(self):
        self.centralwidget = None
        self.top_button_layout = None
        self.bottom_button_layout = None
        self.model_selector = None
        self.recognize_button = None
        self.copy_button = None
        self.plain_text_edit = None
        self.imageLabel = None
        self.latexLabel = None
        self.Copy_Status_Label = None
        self.outputLabel = None
        self.mainLayout = None

    def setup_ui(self, mainwindow):
        """设置主窗口的用户界面"""
        mainwindow.setObjectName("MainWindow")
        mainwindow.resize(960, 720)
        mainwindow.setMinimumSize(QSize(860, 660))

        # 应用全局样式
        mainwindow.setStyleSheet(GLOBAL_STYLESHEET)

        # 设置窗口标题栏
        mainwindow.setWindowTitle("latex2ocr — 公式识别")

        # 中心部件
        self.centralwidget = QtWidgets.QWidget(mainwindow)
        self.centralwidget.setObjectName("centralwidget")

        # ====== 主垂直布局 ======
        self.mainLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.mainLayout.setContentsMargins(24, 18, 24, 18)
        self.mainLayout.setSpacing(14)

        # ====== 顶部工具栏 ======
        toolbar_frame = QtWidgets.QFrame(self.centralwidget)
        toolbar_frame.setObjectName("toolbar")
        toolbar_frame.setMinimumHeight(52)
        self.top_button_layout = QtWidgets.QHBoxLayout(toolbar_frame)
        self.top_button_layout.setContentsMargins(18, 10, 18, 10)
        self.top_button_layout.setSpacing(12)

        # 上传按钮
        self.uploadButton = QtWidgets.QPushButton("  📁 上传图片", toolbar_frame)
        self.top_button_layout.addWidget(self.uploadButton)

        # 截屏按钮（主操作，醒目渐变）
        self.screenshotButton = QtWidgets.QPushButton("  ✂ 截屏识别", toolbar_frame)
        self.screenshotButton.setObjectName("screenshotButton")
        self.top_button_layout.addWidget(self.screenshotButton)

        self.top_button_layout.addStretch()

        # 设置按钮
        self.settingsButton = QtWidgets.QPushButton("⚙ 设置", toolbar_frame)
        self.settingsButton.setObjectName("settingsButton")
        self.top_button_layout.addWidget(self.settingsButton)

        # 关于按钮（下拉菜单）
        self.aboutButton = QtWidgets.QPushButton("⋯", toolbar_frame)
        self.aboutButton.setObjectName("aboutButton")
        self.aboutButton.setFixedWidth(44)
        self.aboutMenu = QtWidgets.QMenu(self.aboutButton)
        self.helpAction = self.aboutMenu.addAction("帮助文档")
        self.contactAction = self.aboutMenu.addAction("联系我们")
        self.aboutButton.setMenu(self.aboutMenu)
        self.top_button_layout.addWidget(self.aboutButton)

        self.mainLayout.addWidget(toolbar_frame)

        # ====== 预览区：左右两栏卡片 ======
        self.previewLayout = QtWidgets.QHBoxLayout()
        self.previewLayout.setSpacing(14)

        # 左卡片：图片预览
        image_card = QtWidgets.QFrame(self.centralwidget)
        image_card.setObjectName("card")
        image_layout = QtWidgets.QVBoxLayout(image_card)
        image_layout.setContentsMargins(6, 2, 6, 2)
        image_layout.setSpacing(0)

        image_header = QtWidgets.QLabel("📷 图片预览", image_card)
        image_header.setObjectName("section_header")
        image_header.setContentsMargins(8, 0, 0, 0)
        image_header.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        image_layout.addWidget(image_header)

        self.imageLabel = QtWidgets.QLabel("点击「上传图片」或「截屏识别」\n也可拖拽图片到此处 / Ctrl+V 粘贴", image_card)
        self.imageLabel.setObjectName("imageLabel")
        self.imageLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.imageLabel.setMinimumSize(380, 200)
        image_layout.addWidget(self.imageLabel)

        self.previewLayout.addWidget(image_card, stretch=1)

        # 右卡片：LaTeX 渲染预览
        latex_card = QtWidgets.QFrame(self.centralwidget)
        latex_card.setObjectName("card")
        latex_layout = QtWidgets.QVBoxLayout(latex_card)
        latex_layout.setContentsMargins(6, 2, 6, 2)
        latex_layout.setSpacing(0)

        latex_header = QtWidgets.QLabel("✨ 公式预览", latex_card)
        latex_header.setObjectName("section_header")
        latex_header.setContentsMargins(8, 0, 0, 0)
        latex_header.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        latex_layout.addWidget(latex_header)

        self.latexWebView = QtWebEngineWidgets.QWebEngineView(latex_card)
        self.latexWebView.setMinimumSize(380, 200)
        self.latexWebView.setStyleSheet("background: #ffffff; border: none;")
        latex_layout.addWidget(self.latexWebView, stretch=1)

        self.previewLayout.addWidget(latex_card, stretch=1)

        self.mainLayout.addLayout(self.previewLayout, stretch=3)

        # ====== 分隔线 ======
        separator = QtWidgets.QFrame(self.centralwidget)
        separator.setObjectName("separator")
        separator.setFixedHeight(1)
        self.mainLayout.addWidget(separator)

        # ====== LaTeX 代码输出区 ======
        code_card = QtWidgets.QFrame(self.centralwidget)
        code_card.setObjectName("card")
        code_layout = QtWidgets.QVBoxLayout(code_card)
        code_layout.setContentsMargins(6, 2, 6, 2)
        code_layout.setSpacing(0)

        code_header_layout = QtWidgets.QHBoxLayout()
        code_header_layout.setContentsMargins(8, 2, 8, 0)

        code_label = QtWidgets.QLabel("📝 LaTeX 代码", code_card)
        code_label.setObjectName("section_header")
        code_label.setContentsMargins(0, 0, 0, 0)
        code_label.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        code_header_layout.addWidget(code_label)

        code_header_layout.addStretch()

        # 复制按钮（小尺寸，放在标题行右侧）
        self.copy_button = QtWidgets.QPushButton("📋 复制", code_card)
        self.copy_button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff; color: #8888aa;
                border: 1px solid #d8d8e3; border-radius: 6px;
                padding: 6px 16px; font-size: 25px; min-height: 16px;
            }
            QPushButton:hover { background-color: #f0f0f8; color: #333344; }
        """)
        code_header_layout.addWidget(self.copy_button)

        code_layout.addLayout(code_header_layout)

        self.plain_text_edit = QtWidgets.QPlainTextEdit(code_card)
        self.plain_text_edit.setPlaceholderText("识别结果将显示在此处...")
        self.plain_text_edit.setMinimumHeight(90)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(24)
        self.plain_text_edit.setFont(font)
        self.plain_text_edit.setPlainText("")
        code_layout.addWidget(self.plain_text_edit)

        self.mainLayout.addWidget(code_card, stretch=2)

        # ====== 底部操作栏 ======
        bottom_frame = QtWidgets.QFrame(self.centralwidget)
        bottom_frame.setStyleSheet("QFrame { background: transparent; }")
        self.bottom_button_layout = QtWidgets.QHBoxLayout(bottom_frame)
        self.bottom_button_layout.setContentsMargins(0, 6, 0, 0)
        self.bottom_button_layout.setSpacing(14)

        # 模型选择（动态加载，由 MainWindow._load_models_from_config() 填充）
        self.model_selector = QtWidgets.QComboBox(bottom_frame)
        self.bottom_button_layout.addWidget(self.model_selector)

        # 识别按钮（主操作，醒目渐变）
        self.recognize_button = QtWidgets.QPushButton("🚀 识别公式", bottom_frame)
        self.recognize_button.setObjectName("recognize_button")
        self.bottom_button_layout.addWidget(self.recognize_button)

        self.bottom_button_layout.addStretch()

        # 历史记录下拉框
        self.history_combo = QtWidgets.QComboBox(bottom_frame)
        self.history_combo.setMinimumWidth(200)
        self.history_combo.addItem("📋 历史记录")
        self.bottom_button_layout.addWidget(self.history_combo)

        # 清空历史按钮
        self.clear_history_btn = QtWidgets.QPushButton("🗑", bottom_frame)
        self.clear_history_btn.setFixedWidth(36)
        self.clear_history_btn.setToolTip("清空历史记录")
        self.clear_history_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; color: #8888aa;
                border: 1px solid transparent; border-radius: 6px;
                padding: 4px 8px; font-size: 20px;
            }
            QPushButton:hover { background-color: #f0f0f8; color: #333344; border-color: #d8d8e3; }
        """)
        self.bottom_button_layout.addWidget(self.clear_history_btn)

        # 状态标签
        self.Copy_Status_Label = QtWidgets.QLabel("", bottom_frame)
        self.Copy_Status_Label.setObjectName("status_label")
        self.Copy_Status_Label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.bottom_button_layout.addWidget(self.Copy_Status_Label)

        # 输出标签（隐藏，保留兼容）
        self.outputLabel = QtWidgets.QLabel("", bottom_frame)
        self.outputLabel.setObjectName("outputLabel")
        self.outputLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.outputLabel.setStyleSheet("color: transparent;")

        self.mainLayout.addWidget(bottom_frame)

        mainwindow.setCentralWidget(self.centralwidget)
