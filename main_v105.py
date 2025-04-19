"""
主程序模块，实现基于PyQt5的公式识别应用程序
包含GUI界面、截图识别、公式转换等功能
作者：QC
版本：v1.05
"""

import sys
import os
import subprocess
import configparser

import pyperclip
from PIL import ImageGrab

from PyQt5.QtCore import Qt, QObject, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QSizePolicy

import pyautogui
import psutil
import pygetwindow as gw
from matplotlib import pyplot as plt

from Init_Window_v105 import MainWindowUI
# from OCR_iFLY_v104 import get_result
from OCR_Gemini import GeminiFormulaRecognizer, GPTFormulaRecognizer, DeepSeekFormulaRecognizer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class ClipboardMonitor(QObject):
    """剪贴板监控类，用于检测剪贴板内容变化

    Attributes:
        callback: 剪贴板变化时的回调函数
        clipboard: 系统剪贴板实例
    """
    def __init__(self, callback):
        """初始化剪贴板监控器"""
        super().__init__()
        self.callback = callback
        self.clipboard = QApplication.clipboard()
        self.clipboard.dataChanged.connect(self.on_clipboard_change)

    def on_clipboard_change(self):
        """剪贴板内容变化时触发"""
        try:
            # 检查剪贴板中是否有图像
            image = ImageGrab.grabclipboard()
            if image:
                print("检测到剪贴板中的截图")
                self.callback(image)

        except (IOError, RuntimeError, ValueError) as e:  # 添加具体异常类型
            print(f"剪贴板监控失败: {str(e)}")

class MainWindow(QMainWindow):
    """应用程序主窗口类，负责管理用户界面和核心功能

    Attributes:
        ui (Ui_MainWindow): 自动生成的界面对象
        clipboard_monitor (ClipboardMonitor): 剪贴板监控实例
        conf (ConfigParser): 配置解析器
        img_path (str): 当前处理的图片路径
    """
    def __init__(self, parent=None):
        """初始化主窗口并加载界面组件

        Args:
            parent: 父级窗口对象，默认为None
        """
        super(MainWindow, self).__init__(parent)

        self.ui = MainWindowUI()
        self.ui.setup_ui(self)

        self.ui.Copy_Status_Label.setText("")

        # 绑定按钮事件
        self.ui.uploadButton.clicked.connect(self.upload_image)
        self.ui.screenshotButton.clicked.connect(self.capture_screenshot)
        self.ui.settingsButton.clicked.connect(self.open_settings)
        self.ui.recognize_button.clicked.connect(self.recognize_formula)
        self.ui.copy_button.clicked.connect(self.copy_text)

        self.clipboard_monitor = ClipboardMonitor(self.process_screenshot)

        # 初始化配置
        self.conf = configparser.ConfigParser()
        self.conf.read(os.path.join(BASE_DIR, 'config.ini'), encoding="utf-8-sig")

        self.img_path = None
        self.timer = None

    def load_image(self, image_path):
        """
        加载图片并保持比例显示
        :param image_path: 图片路径
        """
        # 加载图片
        pixmap = QPixmap(image_path)

        # 保持图片比例
        self.ui.imageLabel.setPixmap(QPixmap(self.img_path).scaled(
            self.ui.imageLabel.size(), Qt.KeepAspectRatio  # 使用完整路径引用
        ))
        self.ui.imageLabel.setScaledContents(False)  # 禁用强制拉伸
        self.ui.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        # 调整图片大小以适应标签，同时保持比例
        self.ui.imageLabel.resize(pixmap.width(), pixmap.height())


    def formula2img(self, str_latex, out_file, img_size=(5,3), font_size=16):
        """将LaTeX公式渲染为图片文件

        Args:
            str_latex (str): LaTeX公式字符串
            out_file (str): 输出图片路径
            img_size (tuple): 图片尺寸（宽，高），单位英寸
            font_size (int): 字体大小
        """
        fig = plt.figure(figsize=img_size)
        ax = fig.add_axes([0, 0, 1, 1])
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        ax.set_xticks([])
        ax.set_yticks([])
        plt.text(0.5, 0.5, str_latex, fontsize=font_size, verticalalignment='center', horizontalalignment='center')
        plt.savefig(out_file)

        pixmap = QPixmap(out_file)

        # 保持图片比例
        self.ui.latexLabel.setPixmap(pixmap)
        self.ui.latexLabel.setScaledContents(False)  # 禁用强制拉伸
        self.ui.latexLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        # 调整图片大小以适应标签，同时保持比例
        self.ui.latexLabel.resize(pixmap.width(), pixmap.height())

    def upload_image(self):
        """处理用户上传图片操作

        打开文件对话框选择图片文件，加载并显示到界面
        """
        path = QFileDialog.getOpenFileName(self, "选择文件", ".", "公式图片 (*.png *.bmp *.jpg)")

        self.img_path = path[0]
        if self.img_path:
            self.ui.imageLabel.setPixmap(QPixmap(self.img_path).scaled(self.ui.imageLabel.size(), Qt.KeepAspectRatio))

    def capture_screenshot(self):
        """Windows截图功能实现"""
        try:
            # 调用系统截图工具
            subprocess.run(
                ['powershell', '-Command', 'Start-Process SnippingTool -ArgumentList "/clip"'],
                shell=True,
                check=False,
                capture_output=True,
                text=True
            )
            # 重置定时器
            if self.timer:
                self.timer.stop()
            self.timer = QTimer()
            self.timer.timeout.connect(self.check_snipping_tool)
            self.timer.start(100)

        except (OSError, RuntimeError) as e:  # 捕获特定的异常类型
            QMessageBox.critical(self, "错误", f"截图工具启动失败: {str(e)}")

    def process_screenshot(self, image):
        """处理截图结果"""
        try:
             # 保存截图到临时文件
            self.img_path = "screenshot.png"
            self.load_image(self.img_path)
            image.save(self.img_path, "PNG")

            # 清除剪贴板内容
            QApplication.clipboard().clear()

            # 关闭截图工具
            self.close_snipping_tool()
            print(f"截图已保存到: {self.img_path}")

            # 调用公式识别函数
            # self.Formula_OCR_Execute_Gemini()
            self.recognize_formula()

            # 更新状态提示
            # self.ui.plain_text_edit.appendPlainText("\n[系统] 截图已成功捕获并识别")

        except (IOError, ValueError, RuntimeError) as e:  # 捕获特定的异常类型
            QMessageBox.critical(self, "错误", f"截图处理失败: {str(e)}")

    def close_snipping_tool(self):
        """关闭 SnippingTool 进程"""
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'SnippingTool.exe':
                # proc.terminate()  # 终止进程
                proc.kill()
                print("截图工具已关闭")
                break

    def check_snipping_tool(self):
        """检查SnippingTool进程是否正在运行

        遍历当前进程，查找名为'SnippingTool.exe'的进程。
        如果找到，则执行相应的处理。
        """
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'SnippingTool.exe':
                self.send_ctrl_n()
                self.timer.stop()
                self.hide_snipping_tool()
                break

    def hide_snipping_tool(self):
        """最小化Snipping Tool窗口

        检查当前是否有名为'Snipping Tool'的窗口，如果有，则将其最小化。
        """
        snipping_tool_windows = gw.getWindowsWithTitle("Snipping Tool")
        if snipping_tool_windows:
            snipping_tool_windows[0].minimize()

    def send_ctrl_n(self):
        """模拟按下Ctrl+N组合键

        该方法用于发送Ctrl+N快捷键，通常用于新建窗口或文档。
        """
        pyautogui.hotkey('ctrl', 'n')

    def open_settings(self):
        """打开设置界面

        显示一个信息框，提示用户进入模型参数设置界面。
        """
        QMessageBox.information(self, "设置", "模型参数设置界面")

    def recognize_formula(self):
        """根据选择的模型识别公式

        调用对应的识别方法，依据用户在界面上选择的模型。
        """
        model = self.ui.model_selector.currentText()
        if model == "讯飞API":
            self.Formula_OCR_Execute_iFLY()
        elif model == "Google Gemini":
            self.formula_ocr_execute_gemini()
        elif model == "DeepSeek":
            self.formula_ocr_execute_deepseek_vl2()
        elif model == "GPT":
            self.formula_ocr_execute_gpt()

    def formula_ocr_execute_deepseek_vl2(self):
        """执行DeepSeek-VL2公式识别"""
        self.ui.plain_text_edit.setPlainText("正在使用DeepSeek-VL2识别...")
        QApplication.processEvents()

        try:
            # 获取API Key
            # api_key = self.conf.get('API_Gemini', 'APIKey', fallback='')
            api_key = ""
            base_url = "https://api.siliconflow.cn/v1"
            if not api_key:
                raise ValueError("请先配置DeepSeek-VL2 API Key")

            # 初始化识别器
            recognizer = DeepSeekFormulaRecognizer(api_key, base_url)
            result = recognizer.recognize_formula(self.img_path)

            # 显示结果
            self.ui.plain_text_edit.setPlainText(result)
            pyperclip.copy(result)
            self.ui.Copy_Status_Label.setText("截图已成功捕获并识别，结果已自动复制！")

            # 在左侧 LaTeX 公式显示区域显示结果
            print("正在生成 LaTeX 公式图片...")
            # self.formula2img(result, "temp.png")
            self.ui.latexLabel.setText(result)  # 将识别结果显示在 latexLabel 中

            # 加载图片并保持比例
            self.load_image(self.img_path)

        except (IOError, ValueError, RuntimeError) as e:
            error_msg = f"DeepSeek-VL识别错误: {str(e)}"
            self.ui.plain_text_edit.setPlainText(error_msg)
            QMessageBox.critical(self, "严重错误", error_msg)

    def formula_ocr_execute_gemini(self):
        """执行Gemini公式识别"""
        self.ui.plain_text_edit.setPlainText("正在使用Gemini识别...")
        QApplication.processEvents()

        try:
            # 获取API Key
            # api_key = self.conf.get('API_Gemini', 'APIKey', fallback='')
            api_key = ""
            if not api_key:
                raise ValueError("请先配置Gemini API Key")

            # 初始化识别器
            recognizer = GeminiFormulaRecognizer(api_key)
            result = recognizer.recognize_formula(self.img_path)

            # 显示结果
            self.ui.plain_text_edit.setPlainText(result)
            pyperclip.copy(result)
            self.ui.Copy_Status_Label.setText("截图已成功捕获并识别，结果已自动复制！")

            # 在左侧 LaTeX 公式显示区域显示结果
            print("正在生成 LaTeX 公式图片...")
            # self.formula2img(result, "temp.png")
            self.ui.latexLabel.setText(result)  # 将识别结果显示在 latexLabel 中

            # 加载图片并保持比例
            self.load_image(self.img_path)

        except (IOError, ValueError, RuntimeError) as e:
            error_msg = f"Gemini识别错误: {str(e)}"
            self.ui.plain_text_edit.setPlainText(error_msg)
            QMessageBox.critical(self, "严重错误", error_msg)

    def formula_ocr_execute_gpt(self):
        """执行GPT-4.1-mini公式识别

        更新界面文本，提示用户正在进行识别操作。
        """
        self.ui.plain_text_edit.setPlainText("正在使用 GPT-4.1-mini 识别...")
        QApplication.processEvents()

        try:
            # 获取 API Key 和自定义 API 地址
            # api_key = self.conf.get('API_GPT', 'APIKey', fallback='')
            # api_base = self.conf.get('API_GPT', 'APIBase', fallback=None)  # 读取自定义 API 地址
            api_key = f"sk-xxx"
            # api_base_url = f"https://api.chatanywhere.tech"

            if not api_key:
                raise ValueError("请先配置 GPT API Key")

            # 初始化识别器
            recognizer = GPTFormulaRecognizer(api_key)
            result = recognizer.recognize_formula(self.img_path)

            # 显示结果
            self.ui.plain_text_edit.setPlainText(result)
            pyperclip.copy(result)
            self.ui.outputLabel.setText("结果已自动复制！")

            # 在左侧 LaTeX 公式显示区域显示结果
            self.ui.latexLabel.setText(result)  # 将识别结果显示在 latexLabel 中

            # 加载图片并保持比例
            self.load_image(self.img_path)

        except (IOError, ValueError, RuntimeError) as e:
            error_msg = f"GPT识别错误: {str(e)}"
            self.ui.plain_text_edit.setPlainText(error_msg)
            QMessageBox.critical(self, "严重错误", error_msg)


    def copy_text(self):
        """复制识别结果到剪贴板

        将当前文本编辑框中的内容复制到系统剪贴板。
        """
        pyperclip.copy(self.ui.plain_text_edit.toPlainText())
        self.ui.outputLabel.setText("结果已复制到剪贴板")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainInterface = MainWindow()
    MainInterface.show()
    sys.exit(app.exec_())
