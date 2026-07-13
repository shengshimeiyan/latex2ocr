# OCR_Gemini.py
from google import genai
from google.genai import types as genai_types
import os
from openai import OpenAI
import base64
import configparser
from PIL import Image, ImageFilter
from io import BytesIO
from ratelimit import limits, sleep_and_retry

# 统一的公式识别 prompt
FORMULA_RECOGNITION_PROMPT = """请严格按以下要求执行：
1. 识别图片中的数学公式
2. 返回标准LaTeX代码（不含任何额外符号）
3. 如果存在多个公式，用换行分隔
4. 如果非数学内容，返回'ERROR: Non-math content detected'

示例正确响应：
\\begin{align}
E &= mc^2 \\\\
F &= ma
\\end{align}"""


def encode_image_to_base64(image_path):
    """将图片编码为 Base64 字符串"""
    with Image.open(image_path) as img:
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")


class GeminiFormulaRecognizer:
    def __init__(self, api_key=None, model_name=None):
        self.conf = configparser.ConfigParser()
        self.conf.read(os.path.join(os.path.dirname(__file__), 'config.ini'), encoding="utf-8-sig")
        self.api_key = api_key or self.conf.get('API_Gemini', 'APIKey', fallback='')
        self.model_name = model_name or 'gemini-2.0-flash'
        self.client = None
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)

    def test_connection(self):
        """测试 API 连接是否正常"""
        try:
            if not self.client:
                self.client = genai.Client(api_key=self.api_key)
            response = self.client.models.generate_content(
                model=self.model_name,
                contents="Hello",
            )
            if response.text:
                return True
            raise RuntimeError("API 返回空响应")
        except Exception as e:
            raise RuntimeError(f"连接测试失败: {str(e)}")

    @sleep_and_retry
    @limits(calls=10, period=60)
    def recognize_formula(self, image_path):
        """Perform formula recognition with image preprocessing"""
        try:
            if not self.client:
                self.client = genai.Client(api_key=self.api_key)

            # Preprocess image
            print("preparing picture...")
            with Image.open(image_path) as img:
                img = img.convert('L')  # Convert to grayscale
                img = img.filter(ImageFilter.SHARPEN)

                buffered = BytesIO()
                img.save(buffered, format="PNG", optimize=True)
                image_bytes = buffered.getvalue()

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    FORMULA_RECOGNITION_PROMPT,
                    genai_types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
                ],
                config=genai_types.GenerateContentConfig(
                    safety_settings=[
                        genai_types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
                        genai_types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
                        genai_types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"),
                        genai_types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
                    ],
                ),
            )
            return self._process_response(response)

        except Exception as e:
            raise RuntimeError(f"API request failed: {str(e)}")

    def _process_response(self, response):
        """Process and validate API response"""
        try:
            cleaned = response.text.strip()
            if '```latex' in cleaned:
                cleaned = cleaned.replace("```latex", "").replace("```", "").strip()

            # Basic LaTeX validation
            if not any(c in cleaned for c in {'\\', '{', '}'}):
                raise ValueError("Invalid LaTeX format")

            return cleaned
        except AttributeError:
            raise ValueError("Invalid API response format")


class OpenAICompatibleRecognizer:
    """OpenAI 兼容接口的公式识别器基类，供 DeepSeek / GPT / Qwen 等复用"""

    def __init__(self, api_key, base_url=None, model_name=None, default_model='gpt-4o-mini'):
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name or default_model
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url if self.base_url else None
        )

    def test_connection(self):
        """测试 API 连接是否正常"""
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            if response.choices:
                return True
            raise RuntimeError("API 返回空响应")
        except Exception as e:
            raise RuntimeError(f"连接测试失败: {str(e)}")

    def recognize_formula(self, image_path):
        """识别图片中的公式并转换为 LaTeX"""
        try:
            base64_image = encode_image_to_base64(image_path)

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": FORMULA_RECOGNITION_PROMPT},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                            }
                        ]
                    }
                ],
                temperature=0.2,
                top_p=0.7,
                max_tokens=1024,
                stream=False
            )

            result = response.choices[0].message.content
            return result

        except Exception as e:
            raise RuntimeError(f"({self.model_name}) 识别错误: {str(e)}")


class DeepSeekFormulaRecognizer(OpenAICompatibleRecognizer):
    """DeepSeek-VL2 公式识别器"""

    def __init__(self, api_key, base_url=None, model_name=None):
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            model_name=model_name,
            default_model='deepseek-ai/deepseek-vl2'
        )


class GPTFormulaRecognizer(OpenAICompatibleRecognizer):
    """GPT 公式识别器"""

    def __init__(self, api_key, base_url=None, model_name=None):
        super().__init__(
            api_key=api_key,
            base_url=base_url,
            model_name=model_name,
            default_model='gpt-4o-mini'
        )
