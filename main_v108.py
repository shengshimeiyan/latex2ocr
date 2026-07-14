import sys
import os
import subprocess
import configparser
import platform

import pyperclip
from PIL import ImageGrab
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QObject, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox, QSizePolicy,
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QComboBox, QLabel, QHBoxLayout
)

import pyautogui
import psutil
import pygetwindow as gw
from matplotlib import pyplot as plt

from Init_Window_v105 import MainWindowUI
from OCR_Gemini import GeminiFormulaRecognizer, GPTFormulaRecognizer, DeepSeekFormulaRecognizer

# PyInstaller --onefile 兼容：优先使用 exe 所在目录，否则用脚本目录
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class ClipboardMonitor(QObject):
    """剪贴板监控类，用于检测剪贴板中的新图片

    使用轮询方式检测剪贴板变化（比信号更可靠），
    仅在截屏模式下工作，避免误触发。

    Attributes:
        callback: 检测到新图片时的回调函数
        clipboard: 系统剪贴板实例
        _timer: 轮询定时器
        _last_image_hash: 上次检测到的图片哈希，防止重复触发
    """
    def __init__(self, callback):
        """初始化剪贴板监控器"""
        super().__init__()
        self.callback = callback
        self.clipboard = QApplication.clipboard()
        self._last_image_hash = None
        self._active = False

        # 轮询定时器：每 500ms 检查一次剪贴板
        self._timer = QtCore.QTimer(self)
        self._timer.setInterval(500)
        self._timer.timeout.connect(self._check_clipboard)

    def start_monitoring(self):
        """开始监控剪贴板"""
        # 记录当前剪贴板内容的哈希作为基线
        self._snapshot_baseline()
        self._active = True
        self._timer.start()
        print("剪贴板监控已启动")

    def stop_monitoring(self):
        """停止监控剪贴板"""
        self._active = False
        self._timer.stop()
        print("剪贴板监控已停止")

    def _snapshot_baseline(self):
        """记录当前剪贴板图片哈希作为基线"""
        try:
            image = ImageGrab.grabclipboard()
            if image:
                import hashlib
                buf = __import__('io').BytesIO()
                image.save(buf, format='PNG')
                self._last_image_hash = hashlib.md5(buf.getvalue()).hexdigest()
            else:
                self._last_image_hash = None
        except Exception:
            self._last_image_hash = None

    def _check_clipboard(self):
        """定时检查剪贴板是否有新图片"""
        if not self._active:
            return
        try:
            image = ImageGrab.grabclipboard()
            if image is None:
                return

            import hashlib
            buf = __import__('io').BytesIO()
            image.save(buf, format='PNG')
            current_hash = hashlib.md5(buf.getvalue()).hexdigest()

            if current_hash != self._last_image_hash:
                self._last_image_hash = current_hash
                print(f"检测到剪贴板中的新截图 (hash: {current_hash[:8]}...)")
                self.callback(image)
        except (IOError, RuntimeError, ValueError) as e:
            print(f"剪贴板检测失败: {str(e)}")


class OcrWorker(QObject):
    """OCR 工作线程，负责在后台执行耗时的网络请求"""
    success = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, img_path, model_name, conf):
        super().__init__()
        self.img_path = img_path
        self.model_name = model_name
        self.conf = conf

    def run_ocr(self):
        """在工作线程中执行的函数"""
        try:
            result = ""
            if self.model_name == "Google Gemini":
                section = 'API_Gemini'
                api_key = self.conf.get(section, 'APIKey', fallback='')
                model_name_conf = self.conf.get(section, 'ModelName', fallback='gemini-2.0-flash')
                if not api_key:
                    raise ValueError("请先配置Gemini API Key")
                recognizer = GeminiFormulaRecognizer(api_key, model_name=model_name_conf)
                result = recognizer.recognize_formula(self.img_path)

            elif self.model_name == "GPT":
                section = 'API_GPT'
                api_key = self.conf.get(section, 'APIKey', fallback='')
                api_base = self.conf.get(section, 'APIBase', fallback=None)
                model_name_conf = self.conf.get(section, 'ModelName', fallback='gpt-4o-mini')
                if not api_key:
                    raise ValueError("请先配置 GPT API Key")
                recognizer = GPTFormulaRecognizer(api_key, api_base, model_name=model_name_conf)
                result = recognizer.recognize_formula(self.img_path)

            elif self.model_name == "DeepSeek":
                section = 'API_DeepSeek'
                api_key = self.conf.get(section, 'APIKey', fallback='')
                base_url = self.conf.get(section, 'APIBase', fallback='https://api.siliconflow.cn/v1')
                model_name_conf = self.conf.get(section, 'ModelName', fallback='Pro/deepseek-ai/deepseek-vl2')
                if not api_key:
                    raise ValueError("请先配置DeepSeek-VL2 API Key")
                recognizer = DeepSeekFormulaRecognizer(api_key, base_url, model_name=model_name_conf)
                result = recognizer.recognize_formula(self.img_path)

            elif self.model_name == "Qwen3-VL":
                section = 'API_QWen'
                api_key = self.conf.get(section, 'APIKey', fallback='')
                base_url = self.conf.get(section, 'APIBase', fallback='https://api.siliconflow.cn/v1')
                model_name_conf = self.conf.get(section, 'ModelName', fallback='Qwen/Qwen3-VL-8B-Instruct')
                if not api_key:
                    raise ValueError("请先配置 QWen API Key")
                recognizer = DeepSeekFormulaRecognizer(api_key, base_url, model_name=model_name_conf)
                result = recognizer.recognize_formula(self.img_path)

            elif self.model_name == "讯飞API":
                raise NotImplementedError("讯飞API识别尚未实现")

            else:
                raise ValueError(f"未知的模型: {self.model_name}")

            self.success.emit(result)

        except Exception as e:
            self.error.emit(f"识别错误: {str(e)}")


class ApiTestWorker(QObject):
    """API 连接测试工作线程"""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, provider, api_key, api_base, model_name):
        super().__init__()
        self.provider = provider
        self.api_key = api_key
        self.api_base = api_base
        self.model_name = model_name

    def run_test(self):
        try:
            if self.provider == "Google Gemini":
                recognizer = GeminiFormulaRecognizer(self.api_key, model_name=self.model_name)
            elif self.provider == "GPT":
                recognizer = GPTFormulaRecognizer(self.api_key, self.api_base, model_name=self.model_name)
            elif self.provider == "DeepSeek":
                recognizer = DeepSeekFormulaRecognizer(self.api_key, self.api_base, model_name=self.model_name)
            elif self.provider == "Qwen3-VL":
                recognizer = DeepSeekFormulaRecognizer(self.api_key, self.api_base, model_name=self.model_name)
            elif self.provider == "讯飞API":
                self.error.emit("讯飞API测试尚未实现")
                return
            else:
                self.error.emit(f"未知的模型 {self.provider}")
                return

            recognizer.test_connection()
            self.finished.emit("API连接测试成功!")

        except Exception as e:
            self.error.emit(f"API连接测试失败:\n{str(e)}")


class SettingsDialog(QDialog):
    """模型参数设置对话框 - 深色主题"""

    DIALOG_STYLE = """
        QDialog {
            background-color: #1a1b2e;
        }
        QLabel {
            color: #c8c8e0;
            font-size: 13px;
        }
        QLineEdit {
            background-color: #1e1f38;
            color: #e0e0f0;
            border: 1px solid #3a3c66;
            border-radius: 8px;
            padding: 8px 14px;
            font-size: 13px;
            selection-background-color: #4a4c88;
        }
        QLineEdit:focus {
            border-color: #6c5ce7;
        }
        QLineEdit::placeholder {
            color: #555580;
        }
        QComboBox {
            background-color: #2d2f52;
            color: #c8c8e0;
            border: 1px solid #3a3c66;
            border-radius: 8px;
            padding: 8px 14px;
            min-width: 200px;
            font-size: 13px;
        }
        QComboBox:hover { border-color: #5a5caa; }
        QComboBox::drop-down { border: none; width: 28px; }
        QComboBox::down-arrow {
            image: none; border-left: 5px solid transparent;
            border-right: 5px solid transparent; border-top: 6px solid #8888bb;
            margin-right: 8px;
        }
        QComboBox QAbstractItemView {
            background-color: #2d2f52; color: #c8c8e0;
            border: 1px solid #3a3c66; border-radius: 8px;
            selection-background-color: #4a4c88; selection-color: #ffffff;
            outline: none; padding: 4px;
        }
        QPushButton {
            background-color: #2d2f52; color: #c8c8e0;
            border: 1px solid #3a3c66; border-radius: 8px;
            padding: 8px 20px; font-size: 13px; font-weight: 500;
        }
        QPushButton:hover { background-color: #3a3c66; color: #ffffff; }
        QPushButton:pressed { background-color: #4a4c88; }
        QPushButton#save_btn {
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #6c5ce7, stop:1 #a855f7);
            color: #ffffff; border: none;
        }
        QPushButton#save_btn:hover {
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #7c6cf7, stop:1 #b865ff);
        }
        QPushButton#test_btn {
            background-color: transparent; color: #6c5ce7;
            border: 1px solid #6c5ce7;
        }
        QPushButton#test_btn:hover {
            background-color: #2d2f52; color: #a855f7;
        }
        QPushButton#test_btn:disabled {
            color: #555570; border-color: #2a2a44;
        }
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("⚙ 模型参数设置")
        self.setMinimumWidth(520)
        self.setStyleSheet(self.DIALOG_STYLE)

        self.thread = None
        self.worker = None

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.model_combo = QComboBox()
        self.model_combo.addItems(["Google Gemini", "GPT", "DeepSeek", "Qwen3-VL", "讯飞API"])

        current_main_model = self.parent.ui.model_selector.currentText()
        if current_main_model in [self.model_combo.itemText(i) for i in range(self.model_combo.count())]:
             self.model_combo.setCurrentText(current_main_model)

        form_layout.addRow("配置对象:", self.model_combo)

        self.api_base_edit = QLineEdit()
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.Password)

        self.model_name_edit = QLineEdit()
        self.model_name_edit.setPlaceholderText("例如: gpt-4o-mini, gemini-2.5-flash")

        form_layout.addRow("API地址:", self.api_base_edit)
        form_layout.addRow("API密钥:", self.api_key_edit)
        form_layout.addRow("模型名称:", self.model_name_edit)

        self.load_settings()

        self.model_combo.currentTextChanged.connect(self.update_api_fields)

        self.test_btn = QPushButton("🔗 测试连接")
        self.test_btn.setObjectName("test_btn")
        self.test_btn.clicked.connect(self.test_connection)

        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("💾 保存设置")
        self.save_btn.setObjectName("save_btn")
        self.save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(self.test_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(form_layout)
        status_label = QLabel("状态: 准备就绪")
        layout.addWidget(status_label)
        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.status_label = status_label

    def load_settings(self):
        self.update_api_fields()

    def _get_section_name(self, provider_name=None):
        if not provider_name:
            provider_name = self.model_combo.currentText()

        section_map = {
            "Google Gemini": "API_Gemini",
            "GPT": "API_GPT",
            "DeepSeek": "API_DeepSeek",
            "Qwen3-VL": "API_QWen",
            "讯飞API": "API_iFLY",
        }
        return section_map.get(provider_name, "API_DEFAULT")

    def update_api_fields(self):
        section = self._get_section_name()

        api_base = self.parent.conf.get(section, 'APIBase', fallback='')
        api_key = self.parent.conf.get(section, 'APIKey', fallback='')
        model_name = self.parent.conf.get(section, 'ModelName', fallback='')

        self.api_base_edit.setText(api_base)
        self.api_key_edit.setText(api_key)
        self.model_name_edit.setText(model_name)

    def save_settings(self):
        try:
            section = self._get_section_name()

            if not self.parent.conf.has_section(section):
                self.parent.conf.add_section(section)

            self.parent.conf.set(section, 'APIBase', self.api_base_edit.text())
            self.parent.conf.set(section, 'APIKey', self.api_key_edit.text())
            self.parent.conf.set(section, 'ModelName', self.model_name_edit.text())

            with open(os.path.join(BASE_DIR, 'config.ini'), 'w', encoding='utf-8') as f:
                self.parent.conf.write(f)

            self.status_label.setText("状态: 设置已保存")
        except Exception as e:
            self.status_label.setText("状态: 保存失败")
            QMessageBox.critical(self, "错误", f"保存设置失败: {e}")

    def test_connection(self):
        api_key = self.api_key_edit.text()
        if not api_key:
            self.status_label.setText("状态: 错误 - 请先输入API密钥")
            return

        self.test_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.status_label.setText("状态: 正在测试连接...")

        self.thread = QThread()
        self.worker = ApiTestWorker(
            provider=self.model_combo.currentText(),
            api_key=api_key,
            api_base=self.api_base_edit.text(),
            model_name=self.model_name_edit.text()
        )
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run_test)
        self.worker.finished.connect(self.on_test_success)
        self.worker.error.connect(self.on_test_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)
        self.thread.finished.connect(self.on_thread_finished)
        self.thread.start()

    def on_test_success(self, message):
        self.status_label.setText(f"状态: {message}")
        QMessageBox.information(self, "成功", message)
        self.test_btn.setEnabled(True)
        self.save_btn.setEnabled(True)

    def on_test_error(self, error_message):
        self.status_label.setText(f"状态: {error_message.splitlines()[0]}")
        QMessageBox.critical(self, "错误", error_message)
        self.test_btn.setEnabled(True)
        self.save_btn.setEnabled(True)

    def on_thread_finished(self):
        print("线程已完成，正在清理引用...")
        if self.worker:
            self.worker.deleteLater()
            self.worker = None

        if self.thread:
            self.thread.deleteLater()
            self.thread = None

    def reject(self):
        if self.thread and self.thread.isRunning():
            print("用户取消，正在尝试退出线程...")
            self.thread.quit()
            self.thread.wait(500)
        super().reject()


class MainWindow(QMainWindow):
    """应用程序主窗口类，负责管理用户界面和核心功能"""
    def __init__(self, parent=None):
        """初始化主窗口并加载界面组件"""
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

        # 绑定关于菜单事件
        self.ui.helpAction.triggered.connect(self.show_help)
        self.ui.contactAction.triggered.connect(self.show_contact)

        self.clipboard_monitor = ClipboardMonitor(self.process_screenshot)

        # 截屏模式标志
        self._screenshot_mode = False

        # 初始化配置
        self.conf = configparser.ConfigParser()
        self.conf.read(os.path.join(BASE_DIR, 'config.ini'), encoding="utf-8-sig")

        self.img_path = None

        # 用于存储原始的高清 Pixmap
        self.latex_pixmap = None
        self.source_pixmap = None

        # 持有对 OCR 线程的引用
        self.ocr_thread = None
        self.ocr_worker = None

    def load_image(self, image_path):
        """加载图片并保持比例显示"""
        self.source_pixmap = QPixmap(image_path)
        self.ui.imageLabel.setAlignment(Qt.AlignCenter)
        self.update_pixmaps()

    def update_pixmaps(self):
        """根据标签的当前大小重新缩放并设置 Pixmap"""
        if self.latex_pixmap:
            self.ui.latexLabel.setPixmap(self.latex_pixmap.scaled(
                self.ui.latexLabel.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
        else:
            self.ui.latexLabel.clear()

        if self.source_pixmap:
            self.ui.imageLabel.setPixmap(self.source_pixmap.scaled(
                self.ui.imageLabel.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
        else:
            self.ui.imageLabel.clear()

    def resizeEvent(self, event):
        """覆盖 QMainWindow 的 resizeEvent"""
        super(MainWindow, self).resizeEvent(event)
        self.update_pixmaps()

    def formula2img(self, str_latex, out_file, img_size=(5, 3), font_size=22):
        """将LaTeX公式渲染为图片文件

        优先使用 matplotlib 的 mathtext 渲染，若失败则直接显示纯文本。
        """
        try:
            str_latex = str_latex.strip().strip('$$')
            str_latex_wrapped = f"${str_latex}$"

            fig = plt.figure(figsize=img_size)
            ax = fig.add_axes([0, 0, 1, 1])
            ax.set_axis_off()

            ax.text(0.5, 0.5, str_latex_wrapped, fontsize=font_size,
                    verticalalignment='center', horizontalalignment='center')

            plt.savefig(
                out_file,
                bbox_inches='tight',
                pad_inches=0.1,
                dpi=300,
                transparent=True
            )
            plt.close(fig)

            self.latex_pixmap = QPixmap(out_file)
            # 检查渲染结果是否有效（matplotlib 渲染失败时可能输出空白图片）
            if self.latex_pixmap.width() <= 1 or self.latex_pixmap.height() <= 1:
                raise ValueError("渲染结果为空白图片")
            self.ui.latexLabel.setAlignment(Qt.AlignCenter)
            self.update_pixmaps()

        except Exception as e:
            print(f"LaTeX 渲染失败（{e}），回退为纯文本显示")
            plt.close('all')
            self.latex_pixmap = None
            self.ui.latexLabel.setText(str_latex)
            self.ui.latexLabel.setAlignment(Qt.AlignCenter)
            self.update_pixmaps()

    def upload_image(self):
        """处理用户上传图片操作，包含文件校验"""
        path = QFileDialog.getOpenFileName(self, "选择文件", ".", "公式图片 (*.png *.bmp *.jpg)")

        self.img_path = path[0]
        if not self.img_path:
            return

        # 校验文件大小（4MB 限制）
        try:
            file_size = os.path.getsize(self.img_path)
            if file_size > 4 * 1024 * 1024:
                QMessageBox.warning(
                    self, "提示",
                    f"图片大小为 {file_size / 1024 / 1024:.1f}MB，超过 4MB 限制。\n"
                    "请压缩图片后重试。"
                )
                self.img_path = None
                return
        except OSError:
            QMessageBox.warning(self, "提示", "无法读取图片文件，请检查路径。")
            self.img_path = None
            return

        # 校验是否为有效图片
        try:
            from PIL import Image
            with Image.open(self.img_path) as img:
                img.verify()
        except Exception:
            QMessageBox.warning(self, "提示", "无法识别该文件为有效图片，请重新选择。")
            self.img_path = None
            return

        self.load_image(self.img_path)

    def capture_screenshot(self):
        """跨平台截图功能，最小化窗口后调用系统截图工具"""
        try:
            self._screenshot_mode = True
            self.setWindowState(QtCore.Qt.WindowMinimized)
            current_os = platform.system()

            if current_os == "Windows":
                self.clipboard_monitor.start_monitoring()
                subprocess.run('start ms-screenclip:', shell=True, check=False)
            elif current_os == "Darwin":  # macOS
                self.clipboard_monitor.start_monitoring()
                subprocess.run(['screencapture', '-i', '-c'], check=False)
            else:  # Linux
                # 尝试使用 gnome-screenshot，如不可用则提示用户
                try:
                    self.clipboard_monitor.start_monitoring()
                    subprocess.run(['gnome-screenshot', '-a'], check=False)
                except FileNotFoundError:
                    self._screenshot_mode = False
                    self.clipboard_monitor.stop_monitoring()
                    QMessageBox.warning(
                        self, "提示",
                        "未找到截图工具，请安装 gnome-screenshot\n"
                        "或使用系统快捷键截图后粘贴。"
                    )
                    self.show()
                    return

        except (OSError, RuntimeError) as e:
            self._screenshot_mode = False
            self.clipboard_monitor.stop_monitoring()
            QMessageBox.critical(self, "错误", f"截图工具启动失败: {str(e)}")
            self.show()

    def process_screenshot(self, image):
        """处理截图结果（由 ClipboardMonitor 自动回调）"""
        if not self._screenshot_mode:
            print("process_screenshot：非截屏模式，忽略剪贴板变化。")
            return

        self._screenshot_mode = False
        self.clipboard_monitor.stop_monitoring()

        try:
            self.show()
            self.activateWindow()
            self.setWindowState(QtCore.Qt.WindowActive)

            self.img_path = os.path.join(BASE_DIR, "screenshot.png")
            image.save(self.img_path, "PNG")

            self.load_image(self.img_path)
            QApplication.clipboard().clear()
            print(f"截图已保存到: {self.img_path}")
            self.recognize_formula()

        except (IOError, ValueError, RuntimeError) as e:
            self.clipboard_monitor.stop_monitoring()
            QMessageBox.critical(self, "错误", f"截图处理失败: {str(e)}")
            self.show()
            self.activateWindow()
            self.set_ui_enabled(True)

    def show_help(self):
        """显示帮助文档"""
        QMessageBox.information(
            self, "帮助文档",
            "latex2ocr 使用说明\n\n"
            "1. 点击「上传文件」选择本地公式图片\n"
            "2. 或点击「截屏识别」截取屏幕公式\n"
            "3. 在下拉框中选择识别模型\n"
            "4. 点击「识别公式」获取 LaTeX 结果\n"
            "5. 结果会自动复制到剪贴板\n\n"
            "首次使用请先点击「设置」配置 API Key。"
        )

    def show_contact(self):
        """显示联系方式"""
        QMessageBox.information(
            self, "联系我们",
            "项目主页: https://github.com/shengshimeiyan/latex2ocr\n\n"
            "如遇问题，请在 GitHub 提交 Issue。"
        )

    def open_settings(self):
        """打开设置对话框，配置API参数和模型选择"""
        dialog = SettingsDialog(self)
        dialog.exec_()

    def recognize_formula(self):
        """根据选择的模型识别公式（启动工作线程）"""
        if not self.img_path:
            QMessageBox.warning(self, "提示", "请先上传图片或截图")
            return

        if self.ocr_thread and self.ocr_thread.isRunning():
            QMessageBox.warning(self, "提示", "正在识别中，请稍候...")
            return

        self.set_ui_enabled(False)
        model = self.ui.model_selector.currentText()
        self.ui.plain_text_edit.setPlainText(f"正在使用 {model} 识别...")
        QApplication.processEvents()

        self.ocr_thread = QThread()
        self.ocr_worker = OcrWorker(
            img_path=self.img_path,
            model_name=model,
            conf=self.conf
        )
        self.ocr_worker.moveToThread(self.ocr_thread)

        self.ocr_thread.started.connect(self.ocr_worker.run_ocr)
        self.ocr_worker.success.connect(self.on_ocr_success)
        self.ocr_worker.error.connect(self.on_ocr_error)

        self.ocr_worker.success.connect(self.ocr_thread.quit)
        self.ocr_worker.error.connect(self.ocr_thread.quit)
        self.ocr_thread.finished.connect(self.on_ocr_finished)

        self.ocr_thread.start()

    def set_ui_enabled(self, enabled: bool):
        """启用或禁用所有交互式UI元素"""
        self.ui.uploadButton.setEnabled(enabled)
        self.ui.screenshotButton.setEnabled(enabled)
        self.ui.settingsButton.setEnabled(enabled)
        self.ui.recognize_button.setEnabled(enabled)
        self.ui.copy_button.setEnabled(enabled)
        self.ui.model_selector.setEnabled(enabled)

    def on_ocr_success(self, result_latex):
        """在OCR成功时由信号调用（在主线程上）"""
        print("识别成功！")
        self.ui.plain_text_edit.setPlainText(result_latex)

        pyperclip.copy(result_latex)
        self.ui.Copy_Status_Label.setText("识别成功，结果已自动复制！")

        print("正在生成 LaTeX 公式图片...")
        self.formula2img(result_latex, os.path.join(BASE_DIR, "temp_latex.png"))

        self.set_ui_enabled(True)
        self.activateWindow()

    def on_ocr_error(self, error_message):
        """在OCR失败时由信号调用（在主线程上）"""
        print(f"识别失败: {error_message}")
        self.ui.plain_text_edit.setPlainText(error_message)
        QMessageBox.critical(self, "识别错误", error_message)

        self.set_ui_enabled(True)
        self.activateWindow()

    def on_ocr_finished(self):
        """在 QThread.finished() 信号发出时调用"""
        print("OCR 线程已完成，正在清理引用...")
        if self.ocr_worker:
            self.ocr_worker.deleteLater()
            self.ocr_worker = None

        if self.ocr_thread:
            self.ocr_thread.deleteLater()
            self.ocr_thread = None

    def copy_text(self):
        """复制识别结果到剪贴板"""
        pyperclip.copy(self.ui.plain_text_edit.toPlainText())
        self.ui.Copy_Status_Label.setText("结果已复制到剪贴板")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainInterface = MainWindow()
    MainInterface.show()
    sys.exit(app.exec_())
