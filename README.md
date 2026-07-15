# latex2ocr

### 介绍

**轻量级开源公式 OCR 小工具：调用大模型一键识别公式图片，并转换为 LaTeX 格式。**

基于 [QC-Formula](https://github.com/QingchenWait/QC-Formula) 修改，支持 GLM-4.6V-Flash、Google Gemini、GPT、Qwen3-VL、AIHubMix 等大模型。

- 支持从 **电脑本地** 导入公式图片，或使用 **截屏识别** 功能直接截图；
- 公式图片支持 **.png** / **.jpg** / **.bmp**，大小为 **4M** 以内均可；
- 支持**印刷体**及**手写体**，前者识别效果更佳；
- 识别结果自动复制到剪贴板，并渲染为 LaTeX 公式预览（MathJax）；
- OCR 识别在后台线程执行，界面不卡顿；
- 支持自定义添加/删除模型，动态模型选择。

### 1 软件架构

- 软件基于 `Python 3.10+` 开发，界面基于 `PyQt5`，项目 **完全开源**。
- 公式预览基于 `QWebEngineView` + MathJax 3 渲染，支持完整 LaTeX 语法。
- 截屏功能基于 `QScreen.grabWindow` + 全屏覆盖层拖选，无需外部工具。
- 软件在 Windows 10/11 测试通过，macOS / Linux 平台截屏功能可能需要适配。

### 2 使用教程

#### 2.1 快速开始（免安装）

前往 [Releases 页面](https://github.com/shengshimeiyan/latex2ocr/releases) 下载最新版本：

| 文件 | 说明 |
|------|------|
| `latex2ocr-setup-vX.X.X.exe` | 安装包，双击安装后使用（推荐） |
| `latex2ocr-vX.X.X.exe` | 便携版，下载后直接双击运行，无需安装 |

> ⚠️ 首次运行若被 Windows 拦截，请点击「更多信息」→「仍要运行」。使用安装包版本可降低拦截概率。

安装或运行后，进入设置填写 API Key 即可使用，详见下方 2.4 配置说明。

#### 2.2 从源码运行

```bash
pip install -r requirements.txt
python main_v108.py
```

主要依赖：

| 包名 | 用途 |
|------|------|
| PyQt5 | GUI 界面 |
| PyQtWebEngine | QWebEngineView 公式渲染 |
| Pillow | 图片处理 |
| google-genai | Gemini API |
| openai | DeepSeek / GPT / GLM / Qwen API（OpenAI 兼容） |
| httpx | HTTP 客户端（API 调用） |
| pyperclip | 剪贴板操作 |
| ratelimit | API 调用速率限制 |

#### 2.3 获取 API Key（必需）

根据需要选择一个或多个模型，申请对应的 API Key：

| 模型 | API 来源 | 说明 |
|------|----------|------|
| GLM-4.6V-Flash | [智谱 BigModel](https://open.bigmodel.cn/) | 免费额度，国内直连 |
| Qwen3-VL | [SiliconFlow 硅基流动](https://cloud.siliconflow.cn/models) | 注册送额度，国内直连 |
| Google Gemini | [Google AI Studio](https://aistudio.google.com/) | 免费额度，需翻墙 |
| GPT-5.5 等 | [AIHubMix](https://aihubmix.com/) | 需翻墙 |
| GPT | [OpenAI](https://openai.com/index/openai-api/) | 需付费，需翻墙 |

#### 2.4 配置 API Key

1. 运行程序：

   ```bash
   python main_v108.py
   ```

2. 点击界面上的 **「设置」** 按钮，打开设置对话框。

3. 在 **配置对象** 下拉框中选择要配置的模型，填写对应的 **API 地址**、**API 密钥** 和 **模型名称**。

4. 可点击 **「测试连接」** 验证配置是否正确。

5. 点击 **「保存设置」**，配置将写入 `config.ini` 文件。

6. 也可点击 **「➕」** 按钮添加自定义模型。

各模型的默认配置参考：

| 模型 | API 地址 | 模型名称 | 识别器类型 |
|------|----------|----------|-----------|
| GLM-4.6V-Flash | `https://open.bigmodel.cn/api/paas/v4` | `glm-4.6v-flash` | glm |
| Qwen3-VL | `https://api.siliconflow.cn/v1` | `Qwen/Qwen3-VL-8B-Instruct` | openai |
| AIHubMix | `https://aihubmix.com/v1` | `gpt-5.5-free` | openai |
| Google Gemini | `https://generativelanguage.googleapis.com/v1beta/openai/` | `gemini-2.0-flash` | gemini |
| GPT | `https://api.openai.com/v1` | `gpt-4o-mini` | gpt |

### 3 开发说明

#### 3.1 文件树

```
latex2ocr/
├── main_v108.py           # 主程序（推荐使用）
├── main_v105.py           # 旧版主程序（API Key 硬编码，不推荐）
├── OCR_Gemini.py          # OCR 后端，包含 Gemini / DeepSeek / GPT / GLM 识别器
├── Init_Window_v105.py    # PyQt5 GUI 界面定义
├── config.ini             # API 配置文件（首次运行后自动生成）
├── config.ini.example     # API 配置模板
├── requirements.txt       # Python 依赖列表
├── setup.iss              # Inno Setup 安装包脚本
├── .gitignore             # Git 忽略规则
└── README.md
```

#### 3.2 核心类说明

- **`MainWindow`**（main_v108.py）：主窗口，管理 UI 交互、截屏、公式渲染。
- **`ScreenshotOverlay`**（main_v108.py）：全屏截图覆盖层，拖选区域截图。
- **`OcrWorker`**（main_v108.py）：OCR 工作线程，在后台执行 API 调用，避免 UI 冻结。
- **`ApiTestWorker`**（main_v108.py）：API 连接测试工作线程。
- **`SettingsDialog`**（main_v108.py）：模型参数设置对话框，支持动态添加/删除模型。
- **`GeminiFormulaRecognizer`**（OCR_Gemini.py）：Gemini 模型识别器。
- **`OpenAICompatibleRecognizer`**（OCR_Gemini.py）：OpenAI 兼容接口基类，供 GPT / DeepSeek / Qwen / AIHubMix 复用。
- **`OpenAIVisionRecognizer`**（OCR_Gemini.py）：OpenAI 兼容视觉模型识别器，适用于所有 OpenAI 兼容 API（GPT / DeepSeek / Qwen / AIHubMix 等）。
- **`GLMFormulaRecognizer`**（OCR_Gemini.py）：智谱 GLM 视觉模型识别器，支持 JWT 鉴权。

#### 3.3 调试方法

运行主程序：

```bash
python main_v108.py
```

程序的部分运行状态（如图片加载状态、公式识别结果等）会输出到终端中，便于调试。

### 4 已知问题

- **讯飞 API 尚未实现**：界面中保留了讯飞 API 选项，但功能尚未完成。
- **复杂公式识别准确率不高**：结构特别复杂的公式，识别效果可能不理想。
- **请勿使用 Windows 记事本编辑 config.ini**：记事本默认 ANSI 编码会导致读取中文路径时 `UnicodeDecodeError`。请使用支持 UTF-8 编码的编辑器（如 VS Code、Notepad++）。

### 5 参与贡献

欢迎对软件进行后续开发和改进！

1. Fork 本仓库
2. 新建 Feat_xxx 分支
3. 提交代码
4. 新建 Pull Request

### 6 许可证

MIT License
