# Spatial Brief Agent

把建筑需求书（Brief）转换成结构化空间方案，并支持 Agent 式迭代修改。

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

## Streamlit Cloud 部署与 Secrets

本仓库部署分支为 **`master`**（若本地用 `main` 开发，推送时需同步）：

```bash
git push origin main:master
```

### 配置 Secrets（推荐，访客无需粘贴 Key）

1. 打开 [share.streamlit.io](https://share.streamlit.io)，进入 **Workspace**。
2. 选中 **正在访问的 App**（同一 repo 可有多个 App，Secrets **互不共享**）。
3. 右下角 **Manage app** → **Settings** → **Secrets**（不是 GitHub 仓库里的 Settings → Secrets）。
4. 编辑框内 **只保留一行** TOML（英文双引号）：

   ```toml
   DEEPSEEK_API_KEY = "sk-your-key-here"
   ```

5. 点击 **Save**（若有 TOML 语法错误，必须先修到能 Save）。
6. **Reboot app**。
7. 打开 App 左侧诊断（可选）：应看到 **`/mount/.streamlit/secrets.toml`** 体积 **大于 0**，且 **Streamlit secrets 顶层键名** 含 `DEEPSEEK_API_KEY`；主界面显示 **API Key 已就绪（.env / Streamlit Secrets）**。

格式参考：[`.streamlit/secrets.toml.example`](.streamlit/secrets.toml.example)

### 常见误区

| 现象 | 原因 |
|------|------|
| `.streamlit/secrets.toml` 0B，`st.secrets` 为空 | Cloud 控制台 Secrets 未 Save 成功，或 Save 在了别的 App |
| 填在 GitHub → Repository → Secrets | 仅用于 GitHub Actions，**不会**注入 Streamlit App |
| 改了代码但 Cloud 仍是旧行为 | 确认部署分支为 `master`，并 Reboot |

### 备用方案

若暂时无法让 Cloud Secrets 生效，可在 App 左侧 **「备用：手动粘贴 API Key」** 中粘贴 Key（仅当前浏览器会话，不落库）。

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
docs/CASE_STUDY.md  # 案例说明
```

## License

MIT