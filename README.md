# latex2ocr

### 介绍

**轻量级开源公式 OCR 小工具：调用大模型一键识别公式图片，并转换为 LaTeX 格式。**

基于 [QC-Formula](https://github.com/QingchenWait/QC-Formula) 修改，支持 DeepSeek-VL2、Google Gemini、GPT、Qwen3-VL 等大模型。

- 支持从 **电脑本地** 导入公式图片，或使用 **截屏识别** 功能直接截图；
- 公式图片支持 **.png** / **.jpg** / **.bmp**，大小为 **4M** 以内均可；
- 支持**印刷体**及**手写体**，前者识别效果更佳；
- 识别结果自动复制到剪贴板，并渲染为 LaTeX 公式预览；
- OCR 识别在后台线程执行，界面不卡顿。

### 1 软件架构

- 软件基于 `Python 3.7+` 开发，界面基于 `PyQt5`，项目 **完全开源**。
- 软件在 Windows 10 测试通过，macOS / Linux 平台截屏功能可能需要适配。

### 2 使用教程

#### 2.1 安装依赖

```bash
pip install -r requirements.txt
```

#### 2.2 获取 API Key（必需）

根据需要选择一个或多个模型，申请对应的 API Key：

| 模型 | API 来源 | 说明 |
|------|----------|------|
| DeepSeek-VL2 | [SiliconFlow 硅基流动](https://cloud.siliconflow.cn/models) | 注册送 14 元，无需翻墙 |
| Qwen3-VL | [SiliconFlow 硅基流动](https://cloud.siliconflow.cn/models) | 注册送 14 元，无需翻墙 |
| Google Gemini | [Google AI Studio](https://aistudio.google.com/) | 免费额度，需翻墙 |
| GPT | [OpenAI](https://openai.com/index/openai-api/) | 需付费，需翻墙 |

#### 2.3 配置 API Key

1. 运行程序：

   ```bash
   python main_v108.py
   ```

2. 点击界面上的 **「设置」** 按钮，打开设置对话框。

3. 在 **配置对象** 下拉框中选择要配置的模型，填写对应的 **API 地址**、**API 密钥** 和 **模型名称**。

4. 可点击 **「测试连接」** 验证配置是否正确。

5. 点击 **「保存设置」**，配置将写入 `config.ini` 文件。

各模型的默认配置参考：

| 模型 | API 地址 | 模型名称 |
|------|----------|----------|
| DeepSeek | `https://api.siliconflow.cn/v1` | `deepseek-ai/deepseek-vl2` |
| Qwen3-VL | `https://api.siliconflow.cn/v1` | `Qwen/Qwen3-VL-8B-Instruct` |
| Google Gemini | （留空） | `gemini-2.0-flash` |
| GPT | （留空或自定义） | `gpt-4o-mini` |

### 3 开发说明

#### 3.1 文件树

```
latex2ocr/
├── main_v108.py           # 主程序（推荐使用）
├── main_v105.py           # 旧版主程序（API Key 硬编码，不推荐）
├── OCR_Gemini.py          # OCR 后端，包含 Gemini / DeepSeek / GPT 识别器
├── Init_Window_v105.py    # PyQt5 GUI 界面定义
├── config.ini             # API 配置文件（首次运行后自动生成）
├── requirements.txt       # Python 依赖列表
├── .gitignore             # Git 忽略规则
└── README.md
```

#### 3.2 核心类说明

- **`MainWindow`**（main_v108.py）：主窗口，管理 UI 交互、截屏、剪贴板监控。
- **`OcrWorker`**（main_v108.py）：OCR 工作线程，在后台执行 API 调用，避免 UI 冻结。
- **`ClipboardMonitor`**（main_v108.py）：剪贴板监控，检测截图后自动触发识别。
- **`GeminiFormulaRecognizer`**（OCR_Gemini.py）：Gemini 模型识别器，支持 `model_name` 参数。
- **`DeepSeekFormulaRecognizer`**（OCR_Gemini.py）：DeepSeek / Qwen3-VL 识别器（OpenAI 兼容接口），支持 `model_name` 参数。
- **`GPTFormulaRecognizer`**（OCR_Gemini.py）：GPT 模型识别器，支持 `model_name` 参数。

#### 3.3 依赖配置

安装依赖：

```bash
pip install -r requirements.txt
```

主要依赖：

| 包名 | 用途 |
|------|------|
| PyQt5 | GUI 界面 |
| Pillow | 图片处理 |
| google-genai | Gemini API |
| openai | DeepSeek / GPT API（OpenAI 兼容） |
| matplotlib | LaTeX 公式渲染为图片 |
| pyperclip | 剪贴板操作 |
| pyautogui / psutil / pygetwindow | 截屏辅助 |
| ratelimit | API 调用速率限制 |

#### 3.4 调试方法

运行主程序：

```bash
python main_v108.py
```

程序的部分运行状态（如图片加载状态、公式识别结果等）会输出到终端中，便于调试。

### 4 已知问题

- **截屏功能仅支持 Windows**：使用 `ms-screenclip:` 协议调用系统截图工具，macOS / Linux 需要适配。
- **讯飞 API 尚未实现**：界面中保留了讯飞 API 选项，但功能尚未完成。
- **复杂公式识别准确率不高**：结构特别复杂的公式，识别效果可能不理想。
- **请勿使用 Windows 记事本编辑 config.ini**：记事本默认 ANSI 编码会导致读取中文路径时 `UnicodeDecodeError`。请使用支持 UTF-8 编码的编辑器（如 VS Code、Notepad++）。

### 5 参与贡献

欢迎对软件进行后续开发和改进！

1. Fork 本仓库
2. 新建 Feat_xxx 分支
3. 提交代码
4. 新建 Pull Request
