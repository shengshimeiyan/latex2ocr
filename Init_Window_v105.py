# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Init_Window.ui'
#
# Created by: PyQt5 UI code generator 5.9.2

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QSize


class MainWindowUI(object):
    """主窗口的用户界面类

    负责设置和管理主窗口的界面组件和布局。
    """
    def __init__(self):
        """初始化主窗口的用户界面"""
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
        """设置主窗口的用户界面

        Args:
            mainwindow: 主窗口对象
        """
        mainwindow.setObjectName("MainWindow")
        mainwindow.resize(800, 600)

        # 设置窗口的最小尺寸
        mainwindow.setMinimumSize(QSize(800, 600))

        # 创建主窗口的中心部件
        self.centralwidget = QtWidgets.QWidget(mainwindow)
        self.centralwidget.setObjectName("centralwidget")

        # 创建顶部按钮布局
        self.top_button_layout = QtWidgets.QHBoxLayout()
        self.top_button_layout.setObjectName("topButtonLayout")

        # 上传文件按钮
        self.uploadButton = QtWidgets.QPushButton("上传文件", self.centralwidget)
        self.top_button_layout.addWidget(self.uploadButton)

        # 截屏识别按钮
        self.screenshotButton = QtWidgets.QPushButton("截屏识别", self.centralwidget)
        self.top_button_layout.addWidget(self.screenshotButton)

        # 设置按钮
        self.settingsButton = QtWidgets.QPushButton("设置", self.centralwidget)
        self.top_button_layout.addWidget(self.settingsButton)

        # 关于按钮（带下拉菜单）
        self.aboutButton = QtWidgets.QPushButton("关于", self.centralwidget)
        self.aboutMenu = QtWidgets.QMenu(self.aboutButton)
        self.aboutMenu.addAction("帮助文档")
        self.aboutMenu.addAction("联系我们")
        self.aboutButton.setMenu(self.aboutMenu)
        self.top_button_layout.addWidget(self.aboutButton)

        # 图片显示预览模块
        self.previewLayout = QtWidgets.QHBoxLayout()
        self.previewLayout.setObjectName("previewLayout")

        # 左边：LaTeX 公式显示
        self.latexLabel = QtWidgets.QLabel("LaTeX 公式", self.centralwidget)
        self.latexLabel.setFrameShape(QtWidgets.QFrame.Box)
        self.latexLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.latexLabel.setFont(QtGui.QFont("Arial", 12))
        self.previewLayout.addWidget(self.latexLabel)

        # 右边：图片显示
        self.imageLabel = QtWidgets.QLabel("图片预览", self.centralwidget)
        self.imageLabel.setFrameShape(QtWidgets.QFrame.Box)
        self.imageLabel.setMinimumSize(400, 100)
        self.imageLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.previewLayout.addWidget(self.imageLabel)

        # 底部按钮布局
        self.bottom_button_layout = QtWidgets.QHBoxLayout()
        self.bottom_button_layout.setObjectName("bottomButtonLayout")

        # 模型选择下拉列表
        self.model_selector = QtWidgets.QComboBox(self.centralwidget)
        self.model_selector.addItems(["DeepSeek", "Google Gemini", "GPT", "Qwen3-VL", "讯飞API"])
        self.bottom_button_layout.addWidget(self.model_selector)

        # 识别公式按钮
        self.recognize_button = QtWidgets.QPushButton("识别公式", self.centralwidget)
        self.bottom_button_layout.addWidget(self.recognize_button)

        # 复制文本按钮
        self.copy_button = QtWidgets.QPushButton("复制文本", self.centralwidget)
        self.bottom_button_layout.addWidget(self.copy_button)

        # 文本编辑框，用于显示公式识别结果
        self.plain_text_edit = QtWidgets.QPlainTextEdit(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Arial")
        self.plain_text_edit.setFont(font)
        self.plain_text_edit.setPlainText("")

        # 主布局
        self.mainLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.mainLayout.addLayout(self.top_button_layout)
        self.mainLayout.addLayout(self.previewLayout)
        self.mainLayout.addLayout(self.bottom_button_layout)
        self.mainLayout.addWidget(self.plain_text_edit)

        # 状态标签
        self.Copy_Status_Label = QtWidgets.QLabel(self.centralwidget)
        self.Copy_Status_Label.setObjectName("Copy_Status_Label")
        self.Copy_Status_Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Copy_Status_Label.setStyleSheet("color: #666666; font-size: 12px;")

        # 输出标签
        self.outputLabel = QtWidgets.QLabel(self.centralwidget)
        self.outputLabel.setObjectName("outputLabel")
        self.outputLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.outputLabel.setStyleSheet("color: #666666; font-size: 12px;")

        self.mainLayout.addWidget(self.Copy_Status_Label)
        self.mainLayout.addWidget(self.outputLabel)

        mainwindow.setCentralWidget(self.centralwidget)
