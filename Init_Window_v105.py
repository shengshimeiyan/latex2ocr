# -*- coding: utf-8 -*-

# 现代 UI 界面 - 参考 SimpleTeX 风格
# 深色蓝紫主题、卡片式布局、圆角按钮、扁平化设计

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QFont, QIcon


# ============ 全局样式表 ============
GLOBAL_STYLESHEET = """
/* ---------- 主窗口 ---------- */
QMainWindow {
    background-color: #1a1b2e;
}

QWidget#centralwidget {
    background-color: #1a1b2e;
}

/* ---------- 顶部工具栏 ---------- */
QFrame#toolbar {
    background-color: #232440;
    border: none;
    border-radius: 12px;
    padding: 6px 12px;
}

/* ---------- 通用按钮 ---------- */
QPushButton {
    background-color: #2d2f52;
    color: #c8c8e0;
    border: 1px solid #3a3c66;
    border-radius: 8px;
    padding: 8px 20px;
    font-size: 13px;
    font-weight: 500;
    min-height: 18px;
}
QPushButton:hover {
    background-color: #3a3c66;
    color: #ffffff;
    border-color: #5a5caa;
}
QPushButton:pressed {
    background-color: #4a4c88;
}
QPushButton:disabled {
    background-color: #1e1f38;
    color: #555570;
    border-color: #2a2a44;
}

/* ---------- 主要操作按钮（截屏 / 识别） ---------- */
QPushButton#screenshotButton {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6c5ce7, stop:1 #a855f7);
    color: #ffffff;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
    padding: 10px 28px;
}
QPushButton#screenshotButton:hover {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #7c6cf7, stop:1 #b865ff);
}
QPushButton#screenshotButton:pressed {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #5c4cd7, stop:1 #9845e7);
}

QPushButton#recognize_button {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #3b82f6, stop:1 #6366f1);
    color: #ffffff;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
    padding: 10px 28px;
}
QPushButton#recognize_button:hover {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #4b92ff, stop:1 #7376f1);
}
QPushButton#recognize_button:disabled {
    background-color: #2a2c4e;
    color: #555570;
}

/* ---------- 下拉框 ---------- */
QComboBox {
    background-color: #2d2f52;
    color: #c8c8e0;
    border: 1px solid #3a3c66;
    border-radius: 8px;
    padding: 8px 14px;
    min-width: 140px;
    font-size: 13px;
}
QComboBox:hover {
    border-color: #5a5caa;
}
QComboBox::drop-down {
    border: none;
    width: 28px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #8888bb;
    margin-right: 8px;
}
QComboBox QAbstractItemView {
    background-color: #2d2f52;
    color: #c8c8e0;
    border: 1px solid #3a3c66;
    border-radius: 8px;
    selection-background-color: #4a4c88;
    selection-color: #ffffff;
    outline: none;
    padding: 4px;
}

/* ---------- 卡片容器 ---------- */
QFrame#card {
    background-color: #232440;
    border: 1px solid #2e3055;
    border-radius: 12px;
}

/* ---------- 预览标签 ---------- */
QLabel#imageLabel {
    background-color: #1e1f38;
    border: 2px dashed #3a3c66;
    border-radius: 10px;
    color: #555580;
    font-size: 14px;
}
QLabel#latexLabel {
    background-color: #1e1f38;
    border: 2px dashed #3a3c66;
    border-radius: 10px;
    color: #555580;
    font-size: 14px;
}

/* ---------- 文本编辑框 ---------- */
QPlainTextEdit {
    background-color: #1e1f38;
    color: #e0e0f0;
    border: 1px solid #2e3055;
    border-radius: 10px;
    padding: 12px 16px;
    font-family: "Consolas", "Fira Code", monospace;
    font-size: 14px;
    selection-background-color: #4a4c88;
}

/* ---------- 状态标签 ---------- */
QLabel#status_label {
    color: #6c5ce7;
    font-size: 12px;
    padding: 4px 8px;
}

/* ---------- 分隔线 ---------- */
QFrame#separator {
    background-color: #2e3055;
    max-height: 1px;
}

/* ---------- 关于菜单按钮 ---------- */
QPushButton#aboutButton {
    background-color: transparent;
    border: 1px solid transparent;
    color: #8888bb;
    padding: 8px 12px;
}
QPushButton#aboutButton:hover {
    color: #c8c8e0;
    background-color: #2d2f52;
    border-color: #3a3c66;
    border-radius: 8px;
}

/* ---------- 设置按钮 ---------- */
QPushButton#settingsButton {
    background-color: transparent;
    border: 1px solid transparent;
    color: #8888bb;
    padding: 8px 12px;
}
QPushButton#settingsButton:hover {
    color: #c8c8e0;
    background-color: #2d2f52;
    border-color: #3a3c66;
    border-radius: 8px;
}

/* ---------- 菜单 ---------- */
QMenu {
    background-color: #2d2f52;
    color: #c8c8e0;
    border: 1px solid #3a3c66;
    border-radius: 8px;
    padding: 6px;
}
QMenu::item {
    padding: 8px 24px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: #4a4c88;
    color: #ffffff;
}

/* ---------- 滚动条 ---------- */
QScrollBar:vertical {
    background: #1a1b2e;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #3a3c66;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #5a5caa;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""


class MainWindowUI(object):
    """主窗口的用户界面类 - SimpleTeX 风格现代深色主题"""

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
        mainwindow.resize(900, 680)
        mainwindow.setMinimumSize(QSize(800, 600))

        # 应用全局样式
        mainwindow.setStyleSheet(GLOBAL_STYLESHEET)

        # 设置窗口标题栏
        mainwindow.setWindowTitle("latex2ocr — 公式识别")

        # 中心部件
        self.centralwidget = QtWidgets.QWidget(mainwindow)
        self.centralwidget.setObjectName("centralwidget")

        # ====== 主垂直布局 ======
        self.mainLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.mainLayout.setContentsMargins(20, 16, 20, 16)
        self.mainLayout.setSpacing(12)

        # ====== 顶部工具栏 ======
        toolbar_frame = QtWidgets.QFrame(self.centralwidget)
        toolbar_frame.setObjectName("toolbar")
        toolbar_frame.setFixedHeight(56)
        self.top_button_layout = QtWidgets.QHBoxLayout(toolbar_frame)
        self.top_button_layout.setContentsMargins(16, 6, 16, 6)
        self.top_button_layout.setSpacing(10)

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
        self.aboutButton.setFixedWidth(40)
        self.aboutMenu = QtWidgets.QMenu(self.aboutButton)
        self.helpAction = self.aboutMenu.addAction("帮助文档")
        self.contactAction = self.aboutMenu.addAction("联系我们")
        self.aboutButton.setMenu(self.aboutMenu)
        self.top_button_layout.addWidget(self.aboutButton)

        self.mainLayout.addWidget(toolbar_frame)

        # ====== 预览区：左右两栏卡片 ======
        self.previewLayout = QtWidgets.QHBoxLayout()
        self.previewLayout.setSpacing(12)

        # 左卡片：图片预览
        image_card = QtWidgets.QFrame(self.centralwidget)
        image_card.setObjectName("card")
        image_layout = QtWidgets.QVBoxLayout(image_card)
        image_layout.setContentsMargins(2, 2, 2, 2)

        image_header = QtWidgets.QLabel("📷 图片预览", image_card)
        image_header.setStyleSheet("color: #8888bb; font-size: 12px; font-weight: 600; padding: 4px 10px; background: transparent; border: none;")
        image_layout.addWidget(image_header)

        self.imageLabel = QtWidgets.QLabel("拖拽或粘贴图片到此处\n或点击「上传图片」「截屏识别」", image_card)
        self.imageLabel.setObjectName("imageLabel")
        self.imageLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.imageLabel.setMinimumSize(350, 180)
        image_layout.addWidget(self.imageLabel)

        self.previewLayout.addWidget(image_card, stretch=1)

        # 右卡片：LaTeX 渲染预览
        latex_card = QtWidgets.QFrame(self.centralwidget)
        latex_card.setObjectName("card")
        latex_layout = QtWidgets.QVBoxLayout(latex_card)
        latex_layout.setContentsMargins(2, 2, 2, 2)

        latex_header = QtWidgets.QLabel("✨ 公式预览", latex_card)
        latex_header.setStyleSheet("color: #8888bb; font-size: 12px; font-weight: 600; padding: 4px 10px; background: transparent; border: none;")
        latex_layout.addWidget(latex_header)

        self.latexLabel = QtWidgets.QLabel("识别结果将在此渲染", latex_card)
        self.latexLabel.setObjectName("latexLabel")
        self.latexLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.latexLabel.setMinimumSize(350, 180)
        self.latexLabel.setFont(QtGui.QFont("Arial", 12))
        latex_layout.addWidget(self.latexLabel)

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
        code_layout.setContentsMargins(2, 2, 2, 2)

        code_header_layout = QtWidgets.QHBoxLayout()
        code_header_layout.setContentsMargins(10, 6, 10, 0)

        code_label = QtWidgets.QLabel("📝 LaTeX 代码", code_card)
        code_label.setStyleSheet("color: #8888bb; font-size: 12px; font-weight: 600; background: transparent; border: none;")
        code_header_layout.addWidget(code_label)

        code_header_layout.addStretch()

        # 复制按钮（小尺寸，放在标题行右侧）
        self.copy_button = QtWidgets.QPushButton("📋 复制", code_card)
        self.copy_button.setStyleSheet("""
            QPushButton {
                background-color: #2d2f52; color: #8888bb;
                border: 1px solid #3a3c66; border-radius: 6px;
                padding: 4px 14px; font-size: 12px; min-height: 14px;
            }
            QPushButton:hover { background-color: #3a3c66; color: #ffffff; }
        """)
        code_header_layout.addWidget(self.copy_button)

        code_layout.addLayout(code_header_layout)

        self.plain_text_edit = QtWidgets.QPlainTextEdit(code_card)
        self.plain_text_edit.setPlaceholderText("识别结果将显示在此处...")
        self.plain_text_edit.setMinimumHeight(80)
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(13)
        self.plain_text_edit.setFont(font)
        self.plain_text_edit.setPlainText("")
        code_layout.addWidget(self.plain_text_edit)

        self.mainLayout.addWidget(code_card, stretch=2)

        # ====== 底部操作栏 ======
        bottom_frame = QtWidgets.QFrame(self.centralwidget)
        bottom_frame.setStyleSheet("QFrame { background: transparent; }")
        self.bottom_button_layout = QtWidgets.QHBoxLayout(bottom_frame)
        self.bottom_button_layout.setContentsMargins(0, 4, 0, 0)
        self.bottom_button_layout.setSpacing(12)

        # 模型选择
        self.model_selector = QtWidgets.QComboBox(bottom_frame)
        self.model_selector.addItems(["DeepSeek", "Google Gemini", "GPT", "Qwen3-VL", "讯飞API"])
        self.bottom_button_layout.addWidget(self.model_selector)

        # 识别按钮（主操作，醒目渐变）
        self.recognize_button = QtWidgets.QPushButton("🚀 识别公式", bottom_frame)
        self.recognize_button.setObjectName("recognize_button")
        self.bottom_button_layout.addWidget(self.recognize_button)

        self.bottom_button_layout.addStretch()

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
