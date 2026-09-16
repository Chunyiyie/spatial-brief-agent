# Spatial Brief Agent

把建筑需求书（Brief）转换成结构化空间方案，并支持 Agent 式迭代修改。

[![Live Demo](https://img.shields.io/badge/Live_Demo-Streamlit-FF4B4B?style=for-the-badge)](https://spatial-brief-agent.streamlit.app)
[![GitHub Repo](https://img.shields.io/badge/GitHub-Repo-181717?style=for-the-badge)](https://github.com/Chunyiyie/spatial-brief-agent)
[![Case Study](https://img.shields.io/badge/Case_Study-Portfolio-2ea44f?style=for-the-badge)](docs/CASE_STUDY.md)

> **Live Demo URL：** 若徽章链接无法打开，请在 [share.streamlit.io](https://share.streamlit.io) 复制你的 App 地址，并更新 [`docs/DEMO_URL`](docs/DEMO_URL) 与本段链接。

## 在线体验

- **[打开 Live Demo](https://spatial-brief-agent.streamlit.app)** — Streamlit Cloud 部署；服务端已配置 `DEEPSEEK_API_KEY`（Secrets），访客可直接 Analyze。
- **Case Study（作品集叙事）：** [docs/CASE_STUDY.md](docs/CASE_STUDY.md)

## 截图

| Analyze 结果 | 邻接图 | Agent 修改 |
|:---:|:---:|:---:|
| ![Analyze](docs/screenshots/01-analyze-result.png) | ![Graph](docs/screenshots/02-graph-layout.png) | ![Chat](docs/screenshots/03-agent-chat.png) |

抽象布局见 [`docs/screenshots/03b-abstract-layout.png`](docs/screenshots/03b-abstract-layout.png)。

## 功能

- 输入自然语言建筑 Brief
- AI 提取空间清单（名称、面积、用途）
- 分析空间邻接关系（close / medium / far / avoid）
- Python 规则引擎验证空间冲突
- 生成空间关系图和抽象布局图
- 支持对话式修改方案（Agent Loop）

## 技术栈

- Python 3.12+
- DeepSeek API（OpenAI SDK 兼容）
- Pydantic（结构化数据验证）
- NetworkX + Matplotlib（关系图与布局）
- Streamlit（Web UI）

## 设计原则

> Let AI reason. Let the system calculate. Let the designer decide.

- LLM 负责：理解需求、推理、生成方案
- Python 负责：面积计算、规则验证、图表生成

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/Chunyiyie/spatial-brief-agent.git
cd spatial-brief-agent
```

### 2. 本地环境

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

在项目根目录创建 `.env`（已在 `.gitignore` 中，勿提交）：

```env
DEEPSEEK_API_KEY=sk-your-key-here
```

### 3. 本地运行

```bash
streamlit run app.py
```

本地排障（显示部署诊断侧栏）：`SPATIAL_BRIEF_DEBUG=1 streamlit run app.py`

## Streamlit Cloud 部署

本仓库 Cloud 跟踪分支为 **`master`**（本地 `main` 开发时同步）：

```bash
git push origin main:master
```

在 **share.streamlit.io → 本 App → Settings → Secrets** 配置：

```toml
DEEPSEEK_API_KEY = "sk-your-key-here"
```

Save → Reboot。格式参考 [`.streamlit/secrets.toml.example`](.streamlit/secrets.toml.example)。

### 部署排障（Troubleshooting）

| 现象 | 原因 |
|------|------|
| `.streamlit/secrets.toml` 0B，`st.secrets` 为空 | Cloud 控制台 Secrets 未 Save 成功，或 Save 在了别的 App |
| 填在 GitHub → Repository → Secrets | 仅用于 GitHub Actions，**不会**注入 Streamlit App |
| 改了代码但 Cloud 仍是旧行为 | 确认 branch=`master`，并 Reboot |
| 诊断中 `/mount/.streamlit/secrets.toml` 不存在 | 尚未在 **Streamlit App** Settings 中 Save Secrets |

开发模式下可设 `SPATIAL_BRIEF_DEBUG=1` 查看侧栏诊断信息。

## 项目结构

```
app.py              # Streamlit 入口
core/
  llm.py            # DeepSeek 调用
  agent.py          # Agent 修改循环
  models.py         # Pydantic 模型
  rules.py          # 空间关系规则
  settings.py       # API Key / Secrets 加载
  visualize.py      # 关系图
  layout.py         # 抽象布局
docs/
  CASE_STUDY.md     # Portfolio 案例
  screenshots/      # README 用截图
  DAY_12_EXPORT.md  # Day 12 自学指南（导出功能）
```

- **Live Demo：** https://spatial-brief-agent.streamlit.app（见 [`docs/DEMO_URL`](docs/DEMO_URL)）

## License

MIT
