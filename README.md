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
git clone <你的仓库地址>
cd spatial-brief-agent