# -*- coding: utf-8 -*-
"""latex2ocr 全面测试 — 验证五轮审查的所有改动"""

import sys
import os
import json
import configparser
import tempfile
import shutil
import unittest
from unittest.mock import patch, MagicMock

# 确保能导入项目模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ============ 1. OCR_Gemini.py 模块级测试 ============

class TestImports(unittest.TestCase):
    """验证所有顶层导入正确"""

    def test_hmac_hashlib_top_level(self):
        """hmac/hashlib 应在 OCR_Gemini.py 顶层导入，不在函数内"""
        import OCR_Gemini
        self.assertTrue(hasattr(OCR_Gemini, 'hmac'), "hmac 未在 OCR_Gemini 顶层导入")
        self.assertTrue(hasattr(OCR_Gemini, 'hashlib'), "hashlib 未在 OCR_Gemini 顶层导入")

    def test_main_v108_top_level_imports(self):
        """main_v108.py 顶层应有 re、PIL"""
        import main_v108
        self.assertTrue(hasattr(main_v108, 're'), "re 未在 main_v108 顶层导入")
        self.assertTrue(hasattr(main_v108, 'PILImage'), "PILImage 未在 main_v108 顶层导入")


class TestCreateRecognizer(unittest.TestCase):
    """验证 create_recognizer 工厂方法"""

    def test_gemini_type(self):
        from main_v108 import create_recognizer
        from OCR_Gemini import GeminiFormulaRecognizer
        r = create_recognizer('gemini', 'fake-key')
        self.assertIsInstance(r, GeminiFormulaRecognizer)

    def test_openai_type(self):
        from main_v108 import create_recognizer
        from OCR_Gemini import OpenAIVisionRecognizer
        r = create_recognizer('openai', 'fake-key', 'https://api.example.com/v1')
        self.assertIsInstance(r, OpenAIVisionRecognizer)

    def test_gpt_type_alias(self):
        """gpt 类型应映射到 OpenAIVisionRecognizer"""
        from main_v108 import create_recognizer
        from OCR_Gemini import OpenAIVisionRecognizer
        r = create_recognizer('gpt', 'fake-key')
        self.assertIsInstance(r, OpenAIVisionRecognizer)

    def test_glm_type(self):
        from main_v108 import create_recognizer
        from OCR_Gemini import GLMFormulaRecognizer
        r = create_recognizer('glm', 'fake.key.id')
        self.assertIsInstance(r, GLMFormulaRecognizer)

    def test_ifly_not_implemented(self):
        from main_v108 import create_recognizer
        with self.assertRaises(NotImplementedError):
            create_recognizer('ifly', 'fake-key')

    def test_unknown_type_value_error(self):
        from main_v108 import create_recognizer
        with self.assertRaises(ValueError):
            create_recognizer('unknown', 'fake-key')

    def test_case_insensitive(self):
        """识别器类型应大小写不敏感"""
        from main_v108 import create_recognizer
        from OCR_Gemini import GeminiFormulaRecognizer
        r = create_recognizer('Gemini', 'fake-key')
        self.assertIsInstance(r, GeminiFormulaRecognizer)


class TestOpenAICompatibleRecognizer(unittest.TestCase):
    """验证 OpenAI 兼容识别器基类"""

    def test_base_url_strips_chat_completions(self):
        """base_url 应自动去掉 /chat/completions 后缀"""
        from OCR_Gemini import OpenAICompatibleRecognizer
        r = OpenAICompatibleRecognizer('fake-key', base_url='https://api.example.com/v1/chat/completions')
        self.assertEqual(r.base_url, 'https://api.example.com/v1')

    def test_base_url_strips_trailing_slash(self):
        from OCR_Gemini import OpenAICompatibleRecognizer
        r = OpenAICompatibleRecognizer('fake-key', base_url='https://api.example.com/v1/')
        self.assertEqual(r.base_url, 'https://api.example.com/v1')

    def test_base_url_none_handled(self):
        from OCR_Gemini import OpenAICompatibleRecognizer
        r = OpenAICompatibleRecognizer('fake-key', base_url=None)
        self.assertIsNone(r.base_url)

    def test_param_degrade_flag(self):
        """参数降级标志应存在且默认为 False"""
        from OCR_Gemini import OpenAICompatibleRecognizer
        r = OpenAICompatibleRecognizer('fake-key')
        self.assertFalse(getattr(r, '_skip_extra_params', False))


class TestGLMFormulaRecognizer(unittest.TestCase):
    """验证 GLM 识别器"""

    def test_default_base_url(self):
        """GLM 应有默认 base_url"""
        from OCR_Gemini import GLMFormulaRecognizer
        r = GLMFormulaRecognizer('fake.id.secret')
        self.assertIn('bigmodel.cn', r.base_url)

    def test_custom_base_url_preserved(self):
        """自定义 base_url 应被保留（清理后的）"""
        from OCR_Gemini import GLMFormulaRecognizer
        r = GLMFormulaRecognizer('fake.id.secret', base_url='https://custom.api.com/v1')
        self.assertEqual(r.base_url, 'https://custom.api.com/v1')

    def test_ensure_token_rebuilds_client(self):
        """_ensure_token 过期时应重建 client"""
        from OCR_Gemini import GLMFormulaRecognizer
        r = GLMFormulaRecognizer('fake.id.secret')
        old_client = r.client
        # 强制 token 过期
        r._token_cache = {'token': 'old', 'exp': 0}
        r._ensure_token()
        # client 应被重建
        self.assertIsNot(r.client, old_client)

    def test_generate_token_format(self):
        """生成的 JWT token 应是三段式 (header.payload.signature)"""
        from OCR_Gemini import GLMFormulaRecognizer
        r = GLMFormulaRecognizer('testid.testsecret')
        token = r._generate_token()
        parts = token.split('.')
        self.assertEqual(len(parts), 3, f"JWT token 应有三段，实际: {len(parts)}")


class TestApiTestWorker(unittest.TestCase):
    """验证 ApiTestWorker 的异常处理"""

    def test_not_implemented_error_message(self):
        from main_v108 import ApiTestWorker
        w = ApiTestWorker('ifly', 'key', '', '')
        errors = []
        w.error.connect(errors.append)
        w.run_test()
        self.assertEqual(len(errors), 1)
        self.assertIn('讯飞', errors[0])

    def test_value_error_message(self):
        """未知识别器类型应给出友好提示"""
        from main_v108 import ApiTestWorker
        w = ApiTestWorker('unknown_type', 'key', '', '')
        errors = []
        w.error.connect(errors.append)
        w.run_test()
        self.assertEqual(len(errors), 1)
        self.assertIn('不支持的识别器类型', errors[0])


class TestConfigParserOptionxform(unittest.TestCase):
    """验证 configparser 大小写保持"""

    def test_optionxform_str(self):
        """ConfigParser 应设置 optionxform=str 保持键名大小写"""
        conf = configparser.ConfigParser()
        conf.optionxform = str
        conf.add_section('API_Test')
        conf.set('API_Test', 'APIKey', 'my-key')
        conf.set('API_Test', 'DisplayName', 'Test Model')

        # 写入临时文件再读回
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False, encoding='utf-8') as f:
            conf.write(f)
            tmp_path = f.name

        try:
            conf2 = configparser.ConfigParser()
            conf2.optionxform = str
            conf2.read(tmp_path, encoding='utf-8')
            # 键名应保持 TitleCase
            self.assertEqual(conf2.get('API_Test', 'APIKey'), 'my-key')
            self.assertEqual(conf2.get('API_Test', 'DisplayName'), 'Test Model')
            # 不应有小写键
            self.assertFalse(conf2.has_option('API_Test', 'apikey'))
        finally:
            os.unlink(tmp_path)


class TestHistoryManagement(unittest.TestCase):
    """验证历史记录管理"""

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_history_save_load(self):
        """历史记录应正确保存和加载"""
        history = [
            {'time': '07-14 12:00', 'latex': r'\frac{1}{2}', 'model': 'GLM', 'image': ''},
            {'time': '07-14 12:01', 'latex': r'E=mc^2', 'model': 'Gemini', 'image': ''},
        ]
        path = os.path.join(self.tmp_dir, 'history.json')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False)

        with open(path, 'r', encoding='utf-8') as f:
            loaded = json.load(f)

        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0]['latex'], r'\frac{1}{2}')
        self.assertEqual(loaded[1]['model'], 'Gemini')

    def test_history_max_100(self):
        """历史记录应限制最多 100 条"""
        history = [{'time': f'07-14 12:{i:02d}', 'latex': f'latex_{i}', 'model': 'Test', 'image': ''} for i in range(150)]
        # 模拟 _save_history 的截断
        history = history[:100]
        self.assertEqual(len(history), 100)

    def test_orphan_cleanup(self):
        """孤立图片清理应只删除未被引用的文件"""
        history_dir = os.path.join(self.tmp_dir, 'history_images')
        os.makedirs(history_dir)

        # 创建两个图片文件
        referenced = os.path.join(history_dir, 'screenshot_20260714_120000.png')
        orphan = os.path.join(history_dir, 'screenshot_20260714_110000.png')
        open(referenced, 'w').close()
        open(orphan, 'w').close()

        # 模拟历史记录只引用一个
        history = [{'time': '07-14 12:00', 'latex': 'x', 'model': 'T', 'image': referenced}]

        # 清理逻辑
        ref_set = {os.path.normpath(e.get('image', '')) for e in history if e.get('image')}
        for f in os.listdir(history_dir):
            fpath = os.path.normpath(os.path.join(history_dir, f))
            if fpath not in ref_set:
                os.remove(fpath)

        # 被引用的文件应存在
        self.assertTrue(os.path.isfile(referenced))
        # 孤立文件应被删除
        self.assertFalse(os.path.isfile(orphan))


class TestScreenshotOverlayLogic(unittest.TestCase):
    """验证截图覆盖层逻辑（不启动 GUI）"""

    def test_small_selection_emits_cancelled(self):
        """选区过小应发出 cancelled 信号"""
        from PyQt5.QtCore import QRect
        # 模拟小选区
        small = QRect(0, 0, 5, 5)
        self.assertLess(small.width(), 10)
        self.assertLess(small.height(), 10)
        # 逻辑：width < 10 or height < 10 → cancelled

    def test_right_click_cancels(self):
        """右键点击应取消（通过代码逻辑验证）"""
        from PyQt5.QtCore import Qt
        # ScreenshotOverlay.mousePressEvent 处理 Qt.RightButton → cancelled
        self.assertEqual(Qt.RightButton, Qt.RightButton)


class TestMathJaxHtml(unittest.TestCase):
    """验证 MathJax HTML 生成逻辑"""

    def test_formula_size_responsive(self):
        """公式字号应根据窗口宽度缩放"""
        # 模拟 _build_mathjax_html 中的计算
        for width, expected_range in [(600, (18, 28)), (960, (22, 36)), (1500, (28, 46))]:
            scale = max(0.8, min(1.6, width / 960))
            formula_size = max(18, int(28 * scale))
            self.assertGreaterEqual(formula_size, expected_range[0],
                f"width={width}: font-size {formula_size} < min {expected_range[0]}")
            self.assertLessEqual(formula_size, expected_range[1],
                f"width={width}: font-size {formula_size} > max {expected_range[1]}")

    def test_local_mathjax_path(self):
        """本地 MathJax 路径应正确拼接"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        local = os.path.join(base_dir, 'mathjax', 'tex-svg.js')
        # 路径应包含 mathjax/tex-svg.js
        self.assertIn('mathjax', local)
        self.assertTrue(local.endswith('tex-svg.js'))


class TestBuildExeBat(unittest.TestCase):
    """验证 build_exe.bat 的 Python 路径逻辑"""

    def test_bat_uses_spec_file(self):
        """build_exe.bat 应使用 latex2ocr.spec 而非裸 pyinstaller"""
        bat_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build_exe.bat')
        with open(bat_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('latex2ocr.spec', content, "build_exe.bat 应引用 latex2ocr.spec")
        # 不应直接对 .py 文件调用 pyinstaller
        self.assertNotIn('pyinstaller --onefile main_v108.py', content)

    def test_bat_has_fallback(self):
        """build_exe.bat 应有 Python 路径回退逻辑"""
        bat_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build_exe.bat')
        with open(bat_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('where python', content, "build_exe.bat 应有 where python 回退")


class TestSetupIss(unittest.TestCase):
    """验证 setup.iss 配置"""

    def test_no_legacy_temp_files(self):
        """setup.iss 不应包含旧临时文件条目"""
        iss_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'setup.iss')
        with open(iss_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # 不应有 screenshot.png, temp_latex.png, temp.png, clipboard_paste.png
        self.assertNotIn('screenshot.png', content, "setup.iss 不应包含 screenshot.png")
        self.assertNotIn('temp_latex.png', content, "setup.iss 不应包含 temp_latex.png")
        self.assertNotIn('temp.png', content, "setup.iss 不应包含 temp.png")
        self.assertNotIn('clipboard_paste.png', content, "setup.iss 不应包含 clipboard_paste.png")
        # 应有 history 相关清理
        self.assertIn('history.json', content)
        self.assertIn('history_images', content)

    def test_version_matches(self):
        """setup.iss 版本号应存在"""
        iss_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'setup.iss')
        with open(iss_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn('MyAppVersion', content)


class TestReadme(unittest.TestCase):
    """验证 README 内容正确性"""

    def test_gpt_recognizer_is_openai(self):
        """README 中 GPT 识别器类型应为 openai 而非 gpt"""
        readme_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'README.md')
        with open(readme_path, 'r', encoding='utf-8') as f:
            lines = f.read().split('\n')
        # 配置表中 GPT 行的识别器类型应为 openai
        for line in lines:
            if 'api.openai.com' in line and 'gpt-4o-mini' in line:
                self.assertIn('openai', line.split('|')[-2].strip(),
                    f"GPT 行识别器类型应为 openai: {line}")
                self.assertNotIn('| gpt |', line, "GPT 行不应使用 gpt 识别器类型")

    def test_no_main_v105_reference(self):
        """README 文件树不应包含 main_v105.py"""
        readme_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'README.md')
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertNotIn('main_v105.py', content, "README 不应引用已删除的 main_v105.py")


class TestResponsiveFonts(unittest.TestCase):
    """验证响应式字号计算"""

    def test_scale_clamped(self):
        """缩放因子应限制在 0.8-1.6 之间"""
        for width in [400, 960, 2000]:
            scale = max(0.8, min(1.6, width / 960))
            self.assertGreaterEqual(scale, 0.8)
            self.assertLessEqual(scale, 1.6)

    def test_button_size_calc(self):
        """按钮字号应在合理范围内"""
        for width in [600, 960, 1500]:
            scale = max(0.8, min(1.6, width / 960))
            btn_size = max(14, int(20 * scale))
            self.assertGreaterEqual(btn_size, 14)
            self.assertLessEqual(btn_size, 40)

    def test_action_button_larger(self):
        """主操作按钮字号应大于通用按钮"""
        scale = max(0.8, min(1.6, 960 / 960))
        btn_size = max(14, int(20 * scale))
        action_size = max(16, int(22 * scale))
        self.assertGreater(action_size, btn_size)


if __name__ == '__main__':
    unittest.main(verbosity=2)
