import sys
import os
import re
import json
import configparser
import shutil
from datetime import datetime

import pyperclip
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox, QSizePolicy,
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QComboBox, QLabel, QHBoxLayout, QInputDialog
)

from PIL import Image as PILImage
from Init_Window_v105 import MainWindowUI
from OCR_Gemini import GeminiFormulaRecognizer, OpenAIVisionRecognizer, GLMFormulaRecognizer

# PyInstaller --onefile 兼容：优先使用 exe 所在目录，否则用脚本目录
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class ScreenshotOverlay(QtWidgets.QWidget):
    """全屏半透明覆盖层，用户拖拽选区截取屏幕区域"""

    captured = pyqtSignal(QtGui.QPixmap)  # 选区截图完成信号
    cancelled = pyqtSignal()              # ESC 取消截图信号

    def __init__(self, screen_pixmap, parent=None):
        super().__init__(parent)
        self.screen_pixmap = screen_pixmap
        self.origin = None
        self.selection = None

        # 全屏、无边框、置顶
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setWindowState(Qt.WindowFullScreen)
        self.setCursor(Qt.CrossCursor)
        self.show()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        # 画屏幕截图
        painter.drawPixmap(0, 0, self.screen_pixmap)

        if self.origin and self.selection:
            # 暗化非选区
            painter.fillRect(self.rect(), QtGui.QColor(0, 0, 0, 120))
            # 选区内显示原始截图
            painter.drawPixmap(self.selection, self.screen_pixmap, self.selection)
            # 选区边框
            pen = QtGui.QPen(QtGui.QColor("#4f6ef7"), 2, Qt.DashLine)
            painter.setPen(pen)
            painter.drawRect(self.selection)
        else:
            # 未选区时轻微暗化
            painter.fillRect(self.rect(), QtGui.QColor(0, 0, 0, 80))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.origin = event.pos()
            self.selection = None
            self.update()
        elif event.button() == Qt.RightButton:
            # 右键取消截图
            self.cancelled.emit()
            self.close()

    def mouseMoveEvent(self, event):
        if self.origin:
            self.selection = QtCore.QRect(self.origin, event.pos()).normalized()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.selection and self.selection.width() > 10 and self.selection.height() > 10:
                # 选区足够大，裁剪并发出截图信号
                cropped = self.screen_pixmap.copy(self.selection)
                self.captured.emit(cropped)
            else:
                # 选区过小，视为取消
                self.cancelled.emit()
            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.cancelled.emit()
            self.close()


def create_recognizer(recognizer_type, api_key, api_base=None, model_name=None):
    """工厂方法：根据识别器类型创建对应的识别器实例"""
    recognizer_type = recognizer_type.lower()
    if recognizer_type == 'gemini':
        return GeminiFormulaRecognizer(api_key, model_name=model_name)
    elif recognizer_type in ('openai', 'gpt'):
        return OpenAIVisionRecognizer(api_key, api_base, model_name=model_name)
    elif recognizer_type == 'ifly':
        raise NotImplementedError("讯飞API识别尚未实现")
    elif recognizer_type == 'glm':
        return GLMFormulaRecognizer(api_key, api_base, model_name=model_name)
    else:
        raise ValueError(f"未知的识别器类型: {recognizer_type}")


class OcrWorker(QObject):
    """OCR 工作线程，负责在后台执行耗时的网络请求"""
    success = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, img_path, section_name, conf):
        super().__init__()
        self.img_path = img_path
        self.section_name = section_name
        self.conf = conf

    def run_ocr(self):
        """在工作线程中执行的函数 — 根据 config.ini section 动态选择识别器"""
        try:
            section = self.section_name
            recognizer_type = self.conf.get(section, 'Recognizer', fallback='openai')
            api_key = self.conf.get(section, 'APIKey', fallback='')
            api_base = self.conf.get(section, 'APIBase', fallback='')
            model_name = self.conf.get(section, 'ModelName', fallback='')
            display_name = self.conf.get(section, 'DisplayName', fallback=section)

            if not api_key:
                raise ValueError(f"请先配置 {display_name} 的 API Key")

            recognizer = create_recognizer(recognizer_type, api_key, api_base, model_name)
            result = recognizer.recognize_formula(self.img_path)
            self.success.emit(result)

        except Exception as e:
            self.error.emit(f"识别错误: {str(e)}")


class ApiTestWorker(QObject):
    """API 连接测试工作线程"""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, recognizer_type, api_key, api_base, model_name, display_name=""):
        super().__init__()
        self.recognizer_type = recognizer_type
        self.api_key = api_key
        self.api_base = api_base
        self.model_name = model_name
        self.display_name = display_name

    def run_test(self):
        try:
            recognizer = create_recognizer(self.recognizer_type, self.api_key, self.api_base, self.model_name)
            recognizer.test_connection()
            self.finished.emit("API连接测试成功!")

        except NotImplementedError:
            self.error.emit("讯飞API测试尚未实现")
        except ValueError as e:
            self.error.emit(f"不支持的识别器类型: {self.recognizer_type}")
        except Exception as e:
            self.error.emit(f"API连接测试失败:\n{str(e)}")


class SettingsDialog(QDialog):
    """模型参数设置对话框 - 白色主题，动态模型列表"""

    DIALOG_STYLE = """
        QDialog {
            background-color: #f5f6fa;
        }
        QLabel {
            color: #333344;
            font-size: 25px;
        }
        QLineEdit {
            background-color: #ffffff;
            color: #1a1a2e;
            border: 1px solid #d8d8e3;
            border-radius: 8px;
            padding: 10px 14px;
            font-size: 25px;
            selection-background-color: #dce0ff;
        }
        QLineEdit:focus {
            border-color: #4f6ef7;
        }
        QLineEdit::placeholder {
            color: #a0a0b8;
        }
        QComboBox {
            background-color: #ffffff;
            color: #333344;
            border: 1px solid #d8d8e3;
            border-radius: 8px;
            padding: 10px 14px;
            min-width: 220px;
            font-size: 25px;
        }
        QComboBox:hover { border-color: #4f6ef7; }
        QComboBox::drop-down { border: none; width: 28px; }
        QComboBox::down-arrow {
            image: none; border-left: 5px solid transparent;
            border-right: 5px solid transparent; border-top: 6px solid #8888aa;
            margin-right: 8px;
        }
        QComboBox QAbstractItemView {
            background-color: #ffffff; color: #333344;
            border: 1px solid #d8d8e3; border-radius: 8px;
            selection-background-color: #eef0ff; selection-color: #1a1a2e;
            outline: none; padding: 4px;
            font-size: 25px;
        }
        QPushButton {
            background-color: #ffffff; color: #333344;
            border: 1px solid #d8d8e3; border-radius: 8px;
            padding: 10px 24px; font-size: 25px; font-weight: 500;
        }
        QPushButton:hover { background-color: #f0f0f8; color: #1a1a2e; border-color: #b0b0cc; }
        QPushButton:pressed { background-color: #e8e8f0; }
        QPushButton#save_btn {
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #4f6ef7, stop:1 #6c5ce7);
            color: #ffffff; border: none;
        }
        QPushButton#save_btn:hover {
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #5f7eff, stop:1 #7c6cf7);
        }
        QPushButton#test_btn {
            background-color: transparent; color: #4f6ef7;
            border: 1px solid #4f6ef7;
        }
        QPushButton#test_btn:hover {
            background-color: #f0f0f8; color: #3b5ce7;
        }
        QPushButton#test_btn:disabled {
            color: #b0b0c0; border-color: #d8d8e3;
        }
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("⚙ 模型参数设置")
        self.setMinimumWidth(560)
        self.setStyleSheet(self.DIALOG_STYLE)

        self.thread = None
        self.worker = None

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # 模型选择 + 添加/删除按钮
        model_row = QHBoxLayout()
        self.model_combo = QComboBox()
        self._section_names = []
        self._populate_model_combo()
        model_row.addWidget(self.model_combo, stretch=1)

        add_btn = QPushButton("➕")
        add_btn.setToolTip("添加自定义模型")
        add_btn.setFixedWidth(44)
        add_btn.clicked.connect(self._add_custom_model)
        model_row.addWidget(add_btn)

        del_btn = QPushButton("🗑")
        del_btn.setToolTip("删除当前模型")
        del_btn.setFixedWidth(44)
        del_btn.setObjectName("del_btn")
        del_btn.clicked.connect(self._delete_current_model)
        model_row.addWidget(del_btn)

        form_layout.addRow("配置对象:", model_row)

        self.api_base_edit = QLineEdit()
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.Password)

        self.model_name_edit = QLineEdit()
        self.model_name_edit.setPlaceholderText("例如: gpt-4o-mini, Qwen/Qwen3-VL-8B-Instruct")

        self.recognizer_combo = QComboBox()
        self.recognizer_combo.addItems(["openai", "gemini", "glm", "ifly"])
        self.recognizer_combo.setToolTip("openai = OpenAI兼容API (GPT/DeepSeek/Qwen/SiliconFlow等)\ngemini = Google Gemini API\nglm = 智谱GLM视觉模型\nifly = 讯飞API")

        form_layout.addRow("API地址:", self.api_base_edit)
        form_layout.addRow("API密钥:", self.api_key_edit)
        form_layout.addRow("模型名称:", self.model_name_edit)
        form_layout.addRow("识别器类型:", self.recognizer_combo)

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

    def _populate_model_combo(self):
        """从 config.ini 动态读取所有 API_ section，填充下拉框"""
        self.model_combo.clear()
        self._section_names = []
        conf = self.parent.conf
        current_main_model = self.parent.ui.model_selector.currentText()

        for section in conf.sections():
            if section.startswith('API_'):
                display_name = conf.get(section, 'DisplayName', fallback=section.replace('API_', ''))
                self.model_combo.addItem(display_name)
                self._section_names.append(section)

        # 尝试选中主窗口当前选择的模型
        for i, section in enumerate(self._section_names):
            display_name = conf.get(section, 'DisplayName', fallback='')
            if display_name == current_main_model:
                self.model_combo.setCurrentIndex(i)
                break

    def _get_section_name(self):
        """获取当前选中模型对应的 config.ini section 名"""
        idx = self.model_combo.currentIndex()
        if 0 <= idx < len(self._section_names):
            return self._section_names[idx]
        return "API_DEFAULT"

    def update_api_fields(self):
        section = self._get_section_name()

        api_base = self.parent.conf.get(section, 'APIBase', fallback='')
        api_key = self.parent.conf.get(section, 'APIKey', fallback='')
        model_name = self.parent.conf.get(section, 'ModelName', fallback='')
        recognizer = self.parent.conf.get(section, 'Recognizer', fallback='openai').lower()

        self.api_base_edit.setText(api_base)
        self.api_key_edit.setText(api_key)
        self.model_name_edit.setText(model_name)

        # 设置识别器类型
        idx = self.recognizer_combo.findText(recognizer)
        if idx >= 0:
            self.recognizer_combo.setCurrentIndex(idx)
        else:
            self.recognizer_combo.setCurrentIndex(0)

    def save_settings(self):
        try:
            section = self._get_section_name()

            if not self.parent.conf.has_section(section):
                self.parent.conf.add_section(section)

            self.parent.conf.set(section, 'APIBase', self.api_base_edit.text())
            self.parent.conf.set(section, 'APIKey', self.api_key_edit.text())
            self.parent.conf.set(section, 'ModelName', self.model_name_edit.text())
            self.parent.conf.set(section, 'DisplayName', self.model_combo.currentText())
            self.parent.conf.set(section, 'Recognizer', self.recognizer_combo.currentText().lower())

            with open(os.path.join(BASE_DIR, 'config.ini'), 'w', encoding='utf-8') as f:
                self.parent.conf.write(f)

            self.status_label.setText("状态: 设置已保存")
        except Exception as e:
            self.status_label.setText("状态: 保存失败")
            QMessageBox.critical(self, "错误", f"保存设置失败: {e}")

    def _add_custom_model(self):
        """添加自定义模型 — 弹出输入框让用户命名，然后在 config.ini 创建新 section"""
        name, ok = QInputDialog.getText(self, "添加自定义模型", "请输入模型显示名称（例如: Claude Vision）:")
        if not ok or not name.strip():
            return

        name = name.strip()
        # 检查是否重名
        for section in self.parent.conf.sections():
            if section.startswith('API_'):
                existing = self.parent.conf.get(section, 'DisplayName', fallback='')
                if existing == name:
                    QMessageBox.warning(self, "提示", f"模型「{name}」已存在")
                    return

        # 创建新的 section（用名称生成安全的 section 名）
        safe_name = re.sub(r'[^a-zA-Z0-9]', '_', name)
        section_name = f"API_Custom_{safe_name}"

        if not self.parent.conf.has_section(section_name):
            self.parent.conf.add_section(section_name)

        self.parent.conf.set(section_name, 'DisplayName', name)
        self.parent.conf.set(section_name, 'Recognizer', 'openai')
        self.parent.conf.set(section_name, 'APIBase', '')
        self.parent.conf.set(section_name, 'APIKey', '')
        self.parent.conf.set(section_name, 'ModelName', '')

        with open(os.path.join(BASE_DIR, 'config.ini'), 'w', encoding='utf-8') as f:
            self.parent.conf.write(f)

        # 刷新下拉框并选中新模型
        self._populate_model_combo()
        for i, sec in enumerate(self._section_names):
            if sec == section_name:
                self.model_combo.setCurrentIndex(i)
                break

        self.status_label.setText(f"状态: 已添加模型「{name}」，请配置参数")

    def _delete_current_model(self):
        """删除当前选中的模型配置"""
        section = self._get_section_name()
        display_name = self.model_combo.currentText()

        # 不允许删除内置模型
        builtin_sections = {'API_Gemini', 'API_GPT', 'API_DeepSeek', 'API_QWen', 'API_GLM', 'API_iFLY'}
        if section in builtin_sections:
            QMessageBox.warning(self, "提示", f"内置模型「{display_name}」不可删除\n可以清空 API Key 使其在主界面隐藏。")
            return

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除模型「{display_name}」吗？\n此操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        self.parent.conf.remove_section(section)
        with open(os.path.join(BASE_DIR, 'config.ini'), 'w', encoding='utf-8') as f:
            self.parent.conf.write(f)

        self._populate_model_combo()
        self.update_api_fields()
        self.status_label.setText(f"状态: 已删除模型「{display_name}」")

    def test_connection(self):
        api_key = self.api_key_edit.text()
        if not api_key:
            self.status_label.setText("状态: 错误 - 请先输入API密钥")
            return

        # 使用表单当前值（而非配置文件中的旧值）
        recognizer_type = self.recognizer_combo.currentText().lower()
        display_name = self.model_combo.currentText()

        self.test_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.status_label.setText(f"状态: 正在测试 {display_name} 连接...")

        self.thread = QThread()
        self.worker = ApiTestWorker(
            recognizer_type=recognizer_type,
            api_key=api_key,
            api_base=self.api_base_edit.text(),
            model_name=self.model_name_edit.text(),
            display_name=display_name
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

        # 双击公式预览区复制 LaTeX
        self.ui.latexWebView.installEventFilter(self)

        # 绑定关于菜单事件
        self.ui.helpAction.triggered.connect(self.show_help)
        self.ui.contactAction.triggered.connect(self.show_contact)

        # 绑定历史记录事件
        self.ui.history_combo.currentIndexChanged.connect(self._on_history_selected)
        self.ui.clear_history_btn.clicked.connect(self._clear_history)

        # 初始化配置（optionxform=str 保持键名大小写，确保 TitleCase 键名正确读写）
        self.conf = configparser.ConfigParser()
        self.conf.optionxform = str
        self.conf.read(os.path.join(BASE_DIR, 'config.ini'), encoding="utf-8-sig")

        # 动态加载模型下拉框 — 只显示有 API Key 的模型
        self._load_models_from_config()

        self.img_path = None

        # 用于存储原始的高清 Pixmap（图片预览用）
        self.source_pixmap = None

        # 初始公式预览占位
        self.render_latex_preview("")

        # 持有对 OCR 线程的引用
        self.ocr_thread = None
        self.ocr_worker = None

        # 启用拖拽
        self.setAcceptDrops(True)

        # 识别历史记录
        self._history = []  # [{'time':..., 'latex':..., 'model':..., 'image':...}, ...]
        self._last_history_index = -1  # 上次选中的历史条目索引（用于单条删除）
        self._load_history()

    def dragEnterEvent(self, event):
        """拖拽进入时，接受包含图片或文件的事件"""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                    event.acceptProposedAction()
                    return
        if event.mimeData().hasImage():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """拖拽释放时，加载图片并自动识别"""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                    self._load_image_file(path, auto_recognize=True)
                    return
        if event.mimeData().hasImage():
            pixmap = QtGui.QPixmap.fromImage(event.mimeData().imageData())
            if not pixmap.isNull():
                self.img_path = os.path.join(BASE_DIR, "clipboard_paste.png")
                pixmap.save(self.img_path, "PNG")
                self.load_image(self.img_path)
                self.recognize_formula()

    def keyPressEvent(self, event):
        """Ctrl+V 粘贴剪贴板中的图片并自动识别"""
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_V:
            clipboard = QApplication.clipboard()
            mime = clipboard.mimeData()
            if mime.hasImage():
                pixmap = QtGui.QPixmap.fromImage(mime.imageData())
                if not pixmap.isNull():
                    self.img_path = os.path.join(BASE_DIR, "clipboard_paste.png")
                    pixmap.save(self.img_path, "PNG")
                    self.load_image(self.img_path)
                    self.recognize_formula()
                    return
        super().keyPressEvent(event)

    def eventFilter(self, obj, event):
        """双击公式预览区复制 LaTeX 到剪贴板"""
        if obj is self.ui.latexWebView and event.type() == QtCore.QEvent.MouseButtonDblClick:
            text = self.ui.plain_text_edit.toPlainText()
            if text and not text.startswith("正在使用"):
                pyperclip.copy(text)
                self.ui.Copy_Status_Label.setText("已从公式预览区复制")
            return True
        return super().eventFilter(obj, event)

    def _load_image_file(self, path, auto_recognize=False):
        """加载图片文件（含大小校验），auto_recognize=True 时加载后自动识别"""
        try:
            file_size = os.path.getsize(path)
            if file_size > 4 * 1024 * 1024:
                QMessageBox.warning(self, "提示", f"图片大小为 {file_size / 1024 / 1024:.1f}MB，超过 4MB 限制。")
                return
        except OSError:
            QMessageBox.warning(self, "提示", "无法读取图片文件，请检查路径。")
            return

        try:
            with PILImage.open(path) as img:
                img.verify()
        except Exception:
            QMessageBox.warning(self, "提示", "无法识别该文件为有效图片，请重新选择。")
            return

        self.img_path = path
        self.load_image(path)
        if auto_recognize:
            self.recognize_formula()

    def load_image(self, image_path):
        """加载图片并保持比例显示"""
        self.source_pixmap = QPixmap(image_path)
        self.ui.imageLabel.setAlignment(Qt.AlignCenter)
        self.update_pixmaps()

    def update_pixmaps(self):
        """根据标签的当前大小重新缩放并设置图片 Pixmap"""
        if self.source_pixmap:
            self.ui.imageLabel.setPixmap(self.source_pixmap.scaled(
                self.ui.imageLabel.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
        else:
            self.ui.imageLabel.clear()

    def resizeEvent(self, event):
        """覆盖 QMainWindow 的 resizeEvent — 自适应字号 + 更新图片"""
        super(MainWindow, self).resizeEvent(event)
        self.update_pixmaps()
        self._update_font_sizes()

    def _load_models_from_config(self):
        """从 config.ini 动态加载模型到下拉框 — 只显示有 API Key 的模型"""
        self.ui.model_selector.clear()
        self._model_sections = {}  # display_name -> section_name

        for section in self.conf.sections():
            if section.startswith('API_'):
                api_key = self.conf.get(section, 'APIKey', fallback='')
                display_name = self.conf.get(section, 'DisplayName', fallback=section.replace('API_', ''))
                if api_key:  # 有 API Key 才显示
                    self.ui.model_selector.addItem(display_name)
                    self._model_sections[display_name] = section

        # 如果没有可用模型，提示用户配置
        if self.ui.model_selector.count() == 0:
            self.ui.model_selector.addItem("⚠ 请先配置 API Key")
            self.ui.model_selector.setEnabled(False)
        else:
            self.ui.model_selector.setEnabled(True)

    def _update_font_sizes(self):
        """根据窗口宽度动态调整字号 — 基准: 960px 宽度 = 16pt"""
        base_width = 960
        scale = max(0.8, min(1.6, self.width() / base_width))

        # 主编辑框字号
        edit_font = self.ui.plain_text_edit.font()
        edit_font.setPointSize(max(16, int(26 * scale)))
        self.ui.plain_text_edit.setFont(edit_font)

        # 卡片标题字号（图片预览、公式预览、LaTeX代码）
        header_size = max(12, int(16 * scale))
        header_font = QtGui.QFont()
        header_font.setPointSize(header_size)
        header_font.setBold(True)
        for header in self.findChildren(QtWidgets.QLabel, "section_header"):
            header.setFont(header_font)

        # 状态标签字号
        status_size = max(14, int(25 * scale))
        self.ui.Copy_Status_Label.setStyleSheet(
            f"color: #4f6ef7; font-size: {status_size}px; padding: 4px 8px;"
        )

        # 通用按钮字号
        btn_size = max(14, int(20 * scale))
        btn_font = QtGui.QFont()
        btn_font.setPointSize(btn_size)
        for btn in self.findChildren(QtWidgets.QPushButton):
            if btn.objectName() not in ('screenshotButton', 'recognize_button'):
                btn.setFont(btn_font)

        # 主操作按钮字号（稍大）
        action_size = max(16, int(22 * scale))
        action_font = QtGui.QFont()
        action_font.setPointSize(action_size)
        action_font.setBold(True)
        self.ui.screenshotButton.setFont(action_font)
        self.ui.recognize_button.setFont(action_font)

        # 下拉框字号
        combo_size = max(14, int(18 * scale))
        combo_font = QtGui.QFont()
        combo_font.setPointSize(combo_size)
        self.ui.model_selector.setFont(combo_font)
        self.ui.history_combo.setFont(combo_font)

        # 预览标签占位文字字号
        label_size = max(12, int(14 * scale))
        label_font = QtGui.QFont()
        label_font.setPointSize(label_size)
        self.ui.imageLabel.setFont(label_font)

    def _build_mathjax_html(self, latex_str):
        """生成包含 MathJax 渲染的 HTML 页面（优先本地，离线可用）"""
        # 转义 HTML 特殊字符
        escaped = latex_str.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

        # 响应式公式字号
        scale = max(0.8, min(1.6, self.width() / 960))
        formula_size = max(18, int(28 * scale))

        # 优先使用本地 MathJax，离线也能渲染
        local_mathjax = os.path.join(BASE_DIR, 'mathjax', 'tex-svg.js')
        if os.path.isfile(local_mathjax):
            mathjax_src = f'file:///{local_mathjax.replace(os.sep, "/")}'
        else:
            mathjax_src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js'

        return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{
    margin: 0; padding: 20px;
    background: #ffffff;
    display: flex; align-items: center; justify-content: center;
    min-height: 100vh;
    font-family: "Times New Roman", serif;
  }}
  .formula {{
    font-size: {formula_size}px;
    color: #1a1a2e;
    text-align: center;
    padding: 10px;
  }}
  .placeholder {{
    color: #a0a0b8;
    font-size: 18px;
    font-family: sans-serif;
  }}
</style>
<script>
window.MathJax = {{
  tex: {{
    inlineMath: [['$', '$']],
    displayMath: [['$$', '$$']],
    processEscapes: true
  }},
  svg: {{ fontCache: 'global' }},
  startup: {{
    ready: () => {{
      MathJax.startup.defaultReady();
    }}
  }}
}};
</script>
<script src="{mathjax_src}" async></script>
</head>
<body>
<div class="formula">${escaped}$</div>
</body>
</html>"""

    def render_latex_preview(self, latex_str):
        """用 MathJax 渲染公式到 WebEngineView"""
        if not latex_str or not latex_str.strip():
            self.ui.latexWebView.setHtml(
                '<html><body style="margin:0;padding:20px;background:#fff;'
                'display:flex;align-items:center;justify-content:center;min-height:100vh;">'
                '<div style="color:#a0a0b8;font-size:18px;font-family:sans-serif;">识别结果将在此渲染</div>'
                '</body></html>'
            )
            return
        html = self._build_mathjax_html(latex_str.strip().strip('$'))
        self.ui.latexWebView.setHtml(html)

    def upload_image(self):
        """处理用户上传图片操作（上传后自动识别）"""
        path = QFileDialog.getOpenFileName(self, "选择文件", ".", "公式图片 (*.png *.bmp *.jpg)")[0]
        if path:
            self._load_image_file(path, auto_recognize=True)

    def capture_screenshot(self):
        """截图：抓取所有屏幕拼接为虚拟桌面 → 弹出选区覆盖层 → 用户框选 → 获取截图"""
        try:
            # 先最小化窗口，避免截到自身
            self.setWindowState(QtCore.Qt.WindowMinimized)
            QtCore.QCoreApplication.processEvents()
            # 等待窗口最小化完成
            QtCore.QThread.msleep(200)

            # 拼接所有屏幕为一张完整虚拟桌面截图
            screens = QApplication.screens()
            if not screens:
                self.show()
                QMessageBox.warning(self, "提示", "截图失败，无法获取屏幕内容")
                return

            # 计算虚拟桌面总范围
            min_x = min(s.geometry().x() for s in screens)
            min_y = min(s.geometry().y() for s in screens)
            max_x = max(s.geometry().x() + s.geometry().width() for s in screens)
            max_y = max(s.geometry().y() + s.geometry().height() for s in screens)
            total_w = max_x - min_x
            total_h = max_y - min_y

            # 创建空白画布，逐屏绘制
            self._full_screenshot = QtGui.QPixmap(total_w, total_h)
            self._full_screenshot.fill(Qt.black)
            painter = QtGui.QPainter(self._full_screenshot)
            for screen in screens:
                geo = screen.geometry()
                grab = screen.grabWindow(0)
                # 坐标转换到虚拟桌面
                painter.drawPixmap(geo.x() - min_x, geo.y() - min_y, grab)
            painter.end()

            if self._full_screenshot.isNull():
                self.show()
                QMessageBox.warning(self, "提示", "截图失败，无法获取屏幕内容")
                return

            # 弹出选区覆盖层
            self._overlay = ScreenshotOverlay(self._full_screenshot)
            self._overlay.captured.connect(self._on_screenshot_captured)
            self._overlay.cancelled.connect(self._on_screenshot_cancelled)

        except Exception as e:
            self.show()
            QMessageBox.critical(self, "错误", f"截图失败: {str(e)}")

    def _on_screenshot_captured(self, pixmap):
        """选区截图完成回调"""
        self.show()
        self.activateWindow()
        self.setWindowState(QtCore.Qt.WindowActive)

        # 保存到历史图片目录（不会被覆盖，历史记录缩略图可持久化）
        history_dir = os.path.join(BASE_DIR, "history_images")
        os.makedirs(history_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.img_path = os.path.join(history_dir, f"screenshot_{ts}.png")
        pixmap.save(self.img_path, "PNG")

        self.load_image(self.img_path)
        print(f"截图已保存到: {self.img_path}")
        self.recognize_formula()

    def _on_screenshot_cancelled(self):
        """ESC 取消截图回调 — 恢复窗口"""
        self.show()
        self.activateWindow()
        self.setWindowState(QtCore.Qt.WindowActive)

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
        result = dialog.exec_()
        # 设置关闭后刷新模型下拉框
        self._load_models_from_config()

    def recognize_formula(self):
        """根据选择的模型识别公式（启动工作线程）"""
        if not self.img_path:
            QMessageBox.warning(self, "提示", "请先上传图片或截图")
            return

        if self.ocr_thread and self.ocr_thread.isRunning():
            QMessageBox.warning(self, "提示", "正在识别中，请稍候...")
            return

        self.set_ui_enabled(False)
        model_display = self.ui.model_selector.currentText()
        section_name = self._model_sections.get(model_display, '')
        if not section_name:
            QMessageBox.warning(self, "提示", "请先配置有效的模型 API Key")
            self.set_ui_enabled(True)
            return

        self.ui.plain_text_edit.setPlainText(f"正在使用 {model_display} 识别...")
        QApplication.processEvents()

        self.ocr_thread = QThread()
        self.ocr_worker = OcrWorker(
            img_path=self.img_path,
            section_name=section_name,
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

        print("正在渲染 LaTeX 公式预览...")
        self.render_latex_preview(result_latex)

        # 保存到历史记录
        model_display = self.ui.model_selector.currentText()
        self._add_history(result_latex, model_display, self.img_path or '')

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

    # ====== 识别历史 ======

    def _history_path(self):
        """历史记录文件路径"""
        return os.path.join(BASE_DIR, 'history.json')

    def _load_history(self):
        """从磁盘加载历史记录"""
        try:
            path = self._history_path()
            if os.path.isfile(path):
                with open(path, 'r', encoding='utf-8') as f:
                    self._history = json.load(f)
        except Exception:
            self._history = []
        self._refresh_history_combo()

    def _save_history(self):
        """持久化历史记录到磁盘（最多保留 100 条）"""
        try:
            self._history = self._history[:100]
            with open(self._history_path(), 'w', encoding='utf-8') as f:
                json.dump(self._history, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _add_history(self, latex, model_name, image_path=''):
        """添加一条历史记录并刷新下拉框"""
        entry = {
            'time': datetime.now().strftime('%m-%d %H:%M'),
            'latex': latex,
            'model': model_name,
            'image': image_path
        }
        self._history.insert(0, entry)
        self._save_history()
        self._refresh_history_combo()

    def _refresh_history_combo(self):
        """刷新历史记录下拉框"""
        combo = self.ui.history_combo
        combo.blockSignals(True)
        combo.clear()
        combo.addItem("📋 历史记录")
        for entry in self._history:
            full = entry['latex'].replace('\n', ' ')
            short = full[:40]
            suffix = "…" if len(full) > 40 else ""
            combo.addItem(f"{entry['time']} {entry['model']}  {short}{suffix}")
        combo.blockSignals(False)

    def _on_history_selected(self, index):
        """从历史记录中恢复选中条目"""
        if index <= 0:
            return
        self._last_history_index = index - 1
        entry = self._history[index - 1]
        latex = entry['latex']
        self.ui.plain_text_edit.setPlainText(latex)
        self.render_latex_preview(latex)
        pyperclip.copy(latex)
        self.ui.Copy_Status_Label.setText("已从历史记录恢复并复制（🗑 删除此条）")
        # 恢复图片（如果文件还在）
        img = entry.get('image', '')
        if img and os.path.isfile(img):
            self.img_path = img
            self.load_image(img)
        # 重置下拉框显示
        self.ui.history_combo.blockSignals(True)
        self.ui.history_combo.setCurrentIndex(0)
        self.ui.history_combo.blockSignals(False)

    def _clear_history(self):
        """删除单条或清空历史记录"""
        # 如果刚选中过某条历史，则删除该条；否则清空全部
        if self._last_history_index >= 0 and self._last_history_index < len(self._history):
            entry = self._history[self._last_history_index]
            short = entry['latex'][:30].replace('\n', ' ')
            reply = QMessageBox.question(
                self, "删除历史",
                f"确定删除此条记录吗？\n\n{short}…",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self._history.pop(self._last_history_index)
                self._save_history()
                self._refresh_history_combo()
                self._cleanup_orphan_history_images()
            self._last_history_index = -1
            return

        self._last_history_index = -1
        if not self._history:
            return
        reply = QMessageBox.question(
            self, "清空历史",
            "确定要清空所有识别历史记录吗？",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self._history = []
            self._save_history()
            self._refresh_history_combo()
            self._cleanup_orphan_history_images()

    def _cleanup_orphan_history_images(self):
        """清理 history_images 目录中不被任何历史记录引用的图片"""
        history_dir = os.path.join(BASE_DIR, "history_images")
        if not os.path.isdir(history_dir):
            return
        # 收集历史记录中仍在引用的图片路径
        referenced = {os.path.normpath(e.get('image', '')) for e in self._history if e.get('image')}
        try:
            for f in os.listdir(history_dir):
                fpath = os.path.normpath(os.path.join(history_dir, f))
                if fpath not in referenced:
                    os.remove(fpath)
        except Exception:
            pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainInterface = MainWindow()
    MainInterface.show()
    sys.exit(app.exec_())
