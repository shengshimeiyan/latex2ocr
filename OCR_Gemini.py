# OCR_Gemini.py
import google.generativeai as genai
import os
from openai import OpenAI
import base64
import configparser
from PIL import Image, ImageFilter
from io import BytesIO
from ratelimit import limits, sleep_and_retry

class GeminiFormulaRecognizer:
    def __init__(self, api_key=None):
        self.conf = configparser.ConfigParser()
        self.conf.read(os.path.join(os.path.dirname(__file__), 'config.ini'), encoding="utf-8-sig")
        self.api_key = api_key or self.conf.get('API_Gemini', 'APIKey', fallback='')
        self.model = None
        genai.configure(api_key=self.api_key)

    def initialize_model(self):
        """Initialize Gemini model with safety settings"""
        try:
            self.model = genai.GenerativeModel(
                'gemini-2.0-flash',
                safety_settings={
                    'HARM_CATEGORY_HARASSMENT': 'block_none',
                    'HARM_CATEGORY_HATE_SPEECH': 'block_none',
                    'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'block_none',
                    'HARM_CATEGORY_DANGEROUS_CONTENT': 'block_none'
                }
            )
            return True
        except Exception as e:
            raise RuntimeError(f"Model initialization failed: {str(e)}")

    @sleep_and_retry
    @limits(calls=10, period=60)
    def recognize_formula(self, image_path):
        """Perform formula recognition with image preprocessing"""
        if not self.model:
            self.initialize_model()

        try:
            # Preprocess image
            print("preparing picture...")
            with Image.open(image_path) as img:
                img = img.convert('L')  # Convert to grayscale
                img = img.filter(ImageFilter.SHARPEN)

                buffered = BytesIO()
                img.save(buffered, format="PNG", optimize=True)
                image_data = base64.b64encode(buffered.getvalue()).decode("utf-8")

            # Generate prompt
            prompt = """请严格按以下要求执行：
1. 识别图片中的数学公式
2. 返回标准LaTeX代码（不含任何额外符号）
3. 如果存在多个公式，用换行分隔
4. 如果非数学内容，返回'ERROR: Non-math content detected'

示例正确响应：
\\begin{align}
E &= mc^2 \\\\
F &= ma
\\end{align}"""

            response = self.model.generate_content([prompt, {"mime_type": "image/png", "data": image_data}])
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

class DeepSeekFormulaRecognizer:
    def __init__(self, api_key, base_url=None):
        self.api_key = api_key
        self.base_url = base_url
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url if self.base_url else None  # 设置自定义 API 地址
        )

    def encode_image_to_base64(self, image_path):
        """
        将图片编码为 Base64 字符串
        :param image_path: 图片路径
        :return: Base64 编码的图片字符串
        """
        with Image.open(image_path) as img:
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def recognize_formula(self, image_path):
        """
        使用 DeepSeek-VL 模型识别图片中的公式并转换为 LaTeX
        :param image_path: 图片路径
        :return: 识别后的 LaTeX 公式
        """
        prompt ="""请严格按以下要求执行：
1. 识别图片中的数学公式
2. 返回标准LaTeX代码（不含任何额外符号）
3. 如果存在多个公式，用换行分隔
4. 如果非数学内容，返回'ERROR: Non-math content detected'

示例正确响应：
\mathbb{P}\left(y_i\mid f(c_i)_{y_i}=\beta_i\right)=\beta_i,\quad\forall\beta_i\in\Delta^{|\mathcal{Y}_i|}."""
        try:
            # 将图片编码为 Base64
            base64_image = self.encode_image_to_base64(image_path)

            # API调用（非流式）
            response = self.client.chat.completions.create(
                model="deepseek-ai/deepseek-vl2",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
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
                stream=False  # 非流式（或者直接移除）
            )

            # 获取响应结果（对象属性方式）
            result = response.choices[0].message.content
            return result

        except Exception as e:
            raise RuntimeError(f"DeepSeek-VL 识别错误: {str(e)}")


class GPTFormulaRecognizer:
    def __init__(self, api_key, base_url=None):
        """
        初始化 GPT-4.1-mini 模型识别器
        :param api_key: API Key
        :param base_url: 自定义 API 地址（可选）
        """
        self.api_key = api_key
        self.base_url = base_url
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url if self.base_url else None  # 设置 API 地址
        )

    def encode_image_to_base64(self, image_path):
        """
        将图片编码为 Base64 字符串
        :param image_path: 图片路径
        :return: Base64 编码的图片字符串
        """
        with Image.open(image_path) as img:
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def recognize_formula(self, image_path):
        """
        使用 GPT-4.1-mini 模型识别图片中的公式并转换为 LaTeX
        :param image_path: 图片路径
        :return: 识别后的 LaTeX 公式
        """
        try:
            # 将图片编码为 Base64
            base64_image = self.encode_image_to_base64(image_path)

            # 新版API调用方式
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "请识别图片中的数学公式，并返回标准的 LaTeX 代码。"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ]
            )

            # 提取识别结果
            result = response.choices[0].message.content
            return result

        except Exception as e:
            raise RuntimeError(f"GPT-4.1-mini 识别错误: {str(e)}")