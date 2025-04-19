# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Init_Window.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QSizePolicy, QWidget, QHBoxLayout
from PyQt5.QtCore import QSize

class MainWindowUI(object):
    """主窗口的用户界面类

    负责设置和管理主窗口的界面组件和布局。
    """
    def __init__(self):
        """初始化主窗口的用户界面

        创建主窗口的实例，并调用setupUi方法进行界面设置。
        """
        self.centralwidget = None
        self.top_button_layout = None
        self.preview_layout = QHBoxLayout()
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

        初始化主窗口的组件和布局，并设置对象名和其他属性。

        Args:
            MainWindow: 主窗口对象
        """
        # 设置主窗口的对象名
        mainwindow.setObjectName("MainWindow")

        # 设置主窗口的初始大小为 650x460 像素
        mainwindow.resize(800, 600)

        # 创建窗口大小策略对象，设置为固定大小（不可调整）
        # size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # size_policy.setHorizontalStretch(0)  # 设置水平拉伸为0
        # size_policy.setVerticalStretch(0)  # 设置垂直拉伸为0
        # size_policy.setHeightForWidth(mainwindow.sizePolicy().hasHeightForWidth()) #根据宽带调整高度
        # mainwindow.setSizePolicy(size_policy) # 应用窗口大小策略

        # 设置窗口的最小和最大尺寸
        mainwindow.setMinimumSize(QSize(800, 600))
        mainwindow.setMaximumSize(QSize(800, 600))

        # 设置窗口的透明度为1.25
        mainwindow.setWindowOpacity(1.25)

        # 设置窗口的文档模式为False
        mainwindow.setDocumentMode(False)

        # 创建主窗口的中心部件
        self.centralwidget = QWidget(mainwindow)
        self.centralwidget.setObjectName("centralwidget")

        # 创建顶部按钮布局
        self.top_button_layout = QHBoxLayout()
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
        self.latexLabel.setAlignment(QtCore.Qt.AlignCenter)  # 居中对齐
        self.latexLabel.setFont(QtGui.QFont("Arial", 12))  # 设置字体和大小
        self.preview_layout.addWidget(self.latexLabel)

        # 右边：图片显示
        self.imageLabel = QtWidgets.QLabel("图片预览", self.centralwidget)
        self.imageLabel.setFrameShape(QtWidgets.QFrame.Box)
        self.imageLabel.setMinimumSize(400, 100)  # 设置最小尺寸
        self.imageLabel.setMaximumSize(800, 200)  # 设置最大尺寸
        self.imageLabel.setScaledContents(True)  # 允许图片缩放以适应标签大小
        self.preview_layout.addWidget(self.imageLabel)

        # 右侧下方按钮布局
        self.bottom_button_layout = QtWidgets.QHBoxLayout()
        self.bottom_button_layout.setObjectName("bottomButtonLayout")

        # 模型选择下拉列表
        self.model_selector = QtWidgets.QComboBox(self.centralwidget)
        self.model_selector.addItems(["DeepSeek", "Google Gemini", "GPT", "讯飞API"])
        self.bottom_button_layout.addWidget(self.model_selector)

        # 识别公式按钮
        self.recognize_button = QtWidgets.QPushButton("识别公式", self.centralwidget)
        self.bottom_button_layout.addWidget(self.recognize_button)

        # 复制文本按钮
        self.copy_button = QtWidgets.QPushButton("复制文本", self.centralwidget)
        self.bottom_button_layout.addWidget(self.copy_button)

        # 创建文本编辑框，用于显示公式识别结果，并设置其位置、大小和字体
        self.plain_text_edit = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.plain_text_edit.setGeometry(QtCore.QRect(25, 260, 600, 155))
        font = QtGui.QFont()
        font.setFamily("Arial")
        self.plain_text_edit.setFont(font)
        self.plain_text_edit.setPlainText("")
        self.plain_text_edit.setObjectName("plainTextEdit")

        # 主布局
        self.mainLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.mainLayout.addLayout(self.top_button_layout)
        self.mainLayout.addLayout(self.preview_layout)
        self.mainLayout.addLayout(self.bottom_button_layout)
        self.mainLayout.addWidget(self.plain_text_edit)

        # 创建状态标签（新增代码段）
        self.Copy_Status_Label = QtWidgets.QLabel(self.centralwidget)
        self.Copy_Status_Label.setObjectName("Copy_Status_Label")
        self.Copy_Status_Label.setAlignment(QtCore.Qt.AlignCenter)
        self.Copy_Status_Label.setStyleSheet("color: #666666; font-size: 12px;")

        # 创建输出标签（新增代码段）
        self.outputLabel = QtWidgets.QLabel(self.centralwidget)
        self.outputLabel.setObjectName("outputLabel")
        self.outputLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.outputLabel.setStyleSheet("color: #666666; font-size: 12px;")

        # 将标签添加到主布局（在已有布局之后）
        self.mainLayout.addWidget(self.Copy_Status_Label)
        self.mainLayout.addWidget(self.outputLabel)

        mainwindow.setCentralWidget(self.centralwidget)

        # # 调用 retranslateUi 方法，翻译界面文本
        # self.retranslateUi(MainWindow)

        # # 设置顶部标签页的默认选中索引为 2（第三个标签页）
        # self.TopTabWidget.setCurrentIndex(2)

        # # 绑定按钮点击事件到对应的方法
        # self.DOCPage_LoadButton.clicked.connect(MainWindow.img_Load_From_Doc)
        # self.DOCPage_LoadButton.clicked.connect(MainWindow.img_Display_In_Doc_Label)
        # self.Setting_ConfirmButton.clicked.connect(MainWindow.Setting_API_Values)
        # self.DOCPage_InfoButton.clicked.connect(MainWindow.Get_img_Info)
        # self.Setting_CopyButton.clicked.connect(MainWindow.Copy_Formula_Result)
        # self.DOCPage_ConfirmButton.clicked.connect(MainWindow.Formula_OCR_Execute_Gemini)
        # self.Setting_HelpButton.clicked.connect(MainWindow.Get_API_Tutorial)
        # self.action_GiteeTutorial.triggered.connect(MainWindow.Link_To_Gitee_Tutorial)
        # self.action_GithubTutorial.triggered.connect(MainWindow.Link_To_Github_Tutorial)

        # # 自动连接槽函数
        # QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # # 创建 API 提示标签，并设置其位置和大小
        # self.lblAPINote = QtWidgets.QLabel(self.centralwidget)
        # self.lblAPINote.setGeometry(QtCore.QRect(20, 300, 200, 20))
        # self.lblAPINote.setObjectName("lblAPINote")

    # def retranslateUi(self, MainWindow):
    #     _translate = QtCore.QCoreApplication.translate
    #     self.Setting_Label_Gemini.setText(_translate("MainWindow", "Gemini Key:"))
    #     self.APISelector.setItemText(0, _translate("MainWindow", "讯飞API"))
    #     self.APISelector.setItemText(1, _translate("MainWindow", "Google Gemini"))
    #     MainWindow.setWindowTitle(_translate("MainWindow", "Formula-Translate - 公式 OCR"))
    #     self.DOCPage_LoadButton.setText(_translate("MainWindow", "选择图片..."))
    #     self.DOCPage_InfoButton.setText(_translate("MainWindow", "图片信息"))
    #     self.DOCPage_ConfirmButton.setText(_translate("MainWindow", "识别公式"))
    #     self.DOCPage_ImageLabel.setText(_translate("MainWindow", "公式预览"))
    #     self.TopTabWidget.setTabText(self.TopTabWidget.indexOf(self.tab_2), _translate("MainWindow", "从文件导入"))
    #     self.URLPage_label_1.setText(_translate("MainWindow", "图片网址："))
    #     self.URLPage_ConfirmButton.setText(_translate("MainWindow", "识别公式"))
    #     self.URLPage_LoadButton.setText(_translate("MainWindow", "载入图片"))
    #     # 在retranslateUi方法中添加按钮文本翻译（约第209行附近）
    #     self.DOCPage_ScreenshotButton.setText(_translate("MainWindow", "截图识别"))
    #     self.DOCPage_ImageLabel_2.setText(_translate("MainWindow", "URL 导入功能开发中...\n""https://qingchen1995.gitee.io 了解开发进度"))
    #     self.TopTabWidget.setTabText(self.TopTabWidget.indexOf(self.tab), _translate("MainWindow", "从 URL 导入"))
    #     self.Setting_Label_1.setText(_translate("MainWindow", "公式识别 API 设置"))
    #     self.Setting_Label_2.setText(_translate("MainWindow", "APPID:"))
    #     self.Setting_Label_3.setText(_translate("MainWindow", "APISecret:"))
    #     self.Setting_Label_4.setText(_translate("MainWindow", "APIKey:"))
    #     self.Setting_ConfirmButton.setText(_translate("MainWindow", "确定"))
    #     self.Setting_HelpButton.setText(_translate("MainWindow", "获取 API"))
    #     self.Setting_WebsiteButton.setText(_translate("MainWindow", "访问官网"))
    #     self.TopTabWidget.setTabText(self.TopTabWidget.indexOf(self.tab_3), _translate("MainWindow", "公式识别设置"))
    #     self.Setting_Label_5.setText(_translate("MainWindow", "公式识别结果 (LaTeX 格式)："))
    #     self.Setting_CopyButton.setText(_translate("MainWindow", "复制文本"))
    #     self.Copy_Status_Label.setText(_translate("MainWindow", "复制完成！"))
    #     self.menu.setTitle(_translate("MainWindow", "帮助菜单"))
    #     self.actionAPI.setText(_translate("MainWindow", "API"))
    #     self.action_GiteeTutorial.setText(_translate("MainWindow", "从码云查看教程"))
    #     self.action_GiteeTutorial.setToolTip(_translate("MainWindow", "从码云查看教程"))
    #     self.action_GithubTutorial.setText(_translate("MainWindow", "从 Github 查看教程"))
    #     self.action_About.setText(_translate("MainWindow", "关于."))


    #     self.Setting_CopyButton.setText(_translate("MainWindow", "复制文本"))
    #     self.Copy_Status_Label.setText(_translate("MainWindow", "复制完成！"))
    #     self.menu.setTitle(_translate("MainWindow", "帮助菜单"))
    #     self.actionAPI.setText(_translate("MainWindow", "API"))
    #     self.action_GiteeTutorial.setText(_translate("MainWindow", "从码云查看教程"))
    #     self.action_GiteeTutorial.setToolTip(_translate("MainWindow", "从码云查看教程"))
    #     self.action_GithubTutorial.setText(_translate("MainWindow", "从 Github 查看教程"))
    #     self.action_About.setText(_translate("MainWindow", "关于."))

