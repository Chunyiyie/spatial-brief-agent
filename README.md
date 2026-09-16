# Spatial Brief Agent

把建筑需求书（Brief）转换成结构化空间方案，并支持 Agent 式迭代修改。

[![Live Demo](https://img.shields.io/badge/Live_Demo-Streamlit-FF4B4B?style=for-the-badge)](https://spatial-brief-agent.streamlit.app)
[![GitHub Repo](https://img.shields.io/badge/GitHub-Repo-181717?style=for-the-badge)](https://github.com/Chunyiyie/spatial-brief-agent)
[![Case Study](https://img.shields.io/badge/Case_Study-Portfolio-2ea44f?style=for-the-badge)](docs/CASE_STUDY.md)

## 在线体验

- **[Live Demo](https://spatial-brief-agent.streamlit.app)**
- **[Case Study](docs/CASE_STUDY.md)**

## 截图

| Analyze 结果 | 邻接图 | Agent 修改 |
|:---:|:---:|:---:|
| ![Analyze](docs/screenshots/01-analyze-result.png) | ![Graph](docs/screenshots/02-graph-layout.png) | ![Chat](docs/screenshots/03-agent-chat.png) |

## 功能

- 输入自然语言建筑 Brief
- AI 提取空间清单（名称、面积、用途）
- 分析空间邻接关系（close / medium / far / avoid）
- Python 规则引擎验证空间冲突（数据驱动规则表 + 面积检查）
- 生成空间关系图和抽象布局图
- 支持对话式修改方案（Agent Loop）
- 导出 JSON / CSV / Markdown 报告

## 技术栈

Python · DeepSeek API · Pydantic · NetworkX · Matplotlib · Streamlit

## 设计原则

> Let AI reason. Let the system calculate. Let the designer decide.

## 本地运行

```bash
git clone https://github.com/Chunyiyie/spatial-brief-agent.git
cd spatial-brief-agent
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

创建 `.env`（勿提交）：

```env
DEEPSEEK_API_KEY=sk-your-key-here
```

```bash
streamlit run app.py
```

## License

MIT
