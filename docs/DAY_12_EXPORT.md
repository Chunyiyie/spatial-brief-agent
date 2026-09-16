# DAY 12 — 导出方案（自学指南）

完成 Day 10–11 作品集收口后，按 Future Work 第一项：**把 `SpatialPlan` 导出为可下载文件**。

**目标（约 90 分钟）：** 在 Streamlit 结果页增加「下载 JSON / CSV / Markdown 报告」，不改动 Analyze / Agent 核心逻辑。

## 要学的 4 件事

1. **数据出域**：Pydantic `model_dump_json()` vs 表格化 CSV
2. **Streamlit 下载**：`st.download_button(data=..., file_name=...)`
3. **报告结构**：Markdown 适合 Portfolio PDF 打印；JSON 适合二次开发
4. **模块边界**：新建 `core/export.py`，`app.py` 只调用函数

## 建议步骤

### Step 1 — `core/export.py`

实现（签名自定，保持纯函数）：

- `plan_to_json(plan: SpatialPlan) -> str`
- `plan_to_csv(plan: SpatialPlan) -> str`（spaces 一张表；relationships 可选第二张或合并）
- `plan_to_markdown_report(plan: SpatialPlan) -> str`（含项目名、面积汇总、空间表、关系列表、规则 warnings）

### Step 2 — `app.py`

在 `render_plan(plan)` 末尾或 `st.divider()` 前增加 **Export** 小节，三个 `st.download_button`。

### Step 3 — 自测

本地 Analyze 默认 Brief → 下载三种格式 → 打开确认中文与面积数字正确。

### Step 4 — 提交

```bash
git add core/export.py app.py
git commit -m "feat: export spatial plan as JSON, CSV, and Markdown"
git push origin main && git push origin main:master
```

## 完成标准

- [ ] 三种格式均可下载且内容与页面一致
- [ ] README 功能列表增加「导出报告」一行
- [ ] Case Study Future Work 中「导出」项可勾选

## 扩展（可选）

- 打包 zip（json + csv + md）
- 导出时嵌入关系图 PNG（`fig.savefig` 到 `BytesIO`）
