import os
from pathlib import Path

import streamlit as st

from core.export import plan_to_csv, plan_to_json, plan_to_markdown_report

from core.settings import (
    bootstrap_api_key,
    get_deepseek_api_key,
    inspect_secrets_toml_files,
    missing_api_key_error_message,
)

import matplotlib.pyplot as plt


from core.agent import run_modification
from core.llm import analyze_brief
from core.rules import check_relationships
from core.visualize import draw_spatial_graph
from core.layout import draw_spatial_layout

st.set_page_config(
    page_title="Spatial Brief Agent",
    page_icon="🏛️",
    layout="wide",
)


def show_deploy_diagnostics() -> bool:
    """Public demo hides deploy UI; set SPATIAL_BRIEF_DEBUG=1 locally to troubleshoot."""
    return os.getenv("SPATIAL_BRIEF_DEBUG", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


DEFAULT_BRIEF = """
这是一个 5,000 平方米的社区中心。

主要服务：
- 儿童
- 老年人
- 家庭

项目需要包含：
- 图书馆
- 咖啡厅
- 儿童活动区
- 老年人活动区
- 多功能房间
- 户外公共空间

请分析这些空间之间的空间关系。
请使用中文。
"""


def _streamlit_secret_top_keys_label() -> str:
    try:
        keys = list(st.secrets.keys())
    except Exception as exc:
        return f"（读取失败: {exc}）"
    if not keys:
        return "（空，Cloud Secrets 可能未 Save/Reboot 或未绑在此 App）"
    return str(keys)


def _secrets_toml_on_disk() -> bool:
    for path in (
        Path("/mount/.streamlit/secrets.toml"),
        Path("/.streamlit/secrets.toml"),
        Path(".streamlit/secrets.toml"),
    ):
        if path.is_file():
            return True
    return False


def render_key_diagnostics_sidebar() -> None:
    api_key_loaded = bool(get_deepseek_api_key())
    with st.expander("部署 / 密钥诊断", expanded=False):
        st.write(f"**API Key 已加载:** {'是' if api_key_loaded else '否'}")
        st.write(
            f"**环境变量 DEEPSEEK_API_KEY:** "
            f"{'已设置' if os.getenv('DEEPSEEK_API_KEY') else '未设置'}"
        )
        st.write(f"**磁盘 secrets.toml:** {'是' if _secrets_toml_on_disk() else '否'}")
        st.write(f"**Streamlit secrets 顶层键名:** {_streamlit_secret_top_keys_label()}")
        for report in inspect_secrets_toml_files():
            st.write(
                f"**文件:** `{report['path']}` · "
                f"{report['size_bytes']}B · 键 {report['toml_keys']} · "
                f"行匹配 Key: {report['regex_can_read_key']}"
            )
        if not api_key_loaded:
            st.caption(
                "Cloud Secrets 未生效时，请在上方 **DeepSeek API Key** 粘贴密钥（仅本会话）。"
            )


def render_export_section(plan) -> None:
    """导出方案文件（放在主流程里、图表之前，避免被 pyplot 影响）。"""
    safe_name = plan.project_name.replace(" ", "_").replace("/", "_")[:40] or "spatial_plan"
    json_data = plan_to_json(plan)
    csv_data = plan_to_csv(plan)
    md_data = plan_to_markdown_report(plan)

    with st.container(border=True):
        st.subheader("Export")
        st.caption("下载当前 SpatialPlan（JSON / CSV / Markdown）")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name=f"{safe_name}.json",
                mime="application/json",
                key="export_json",
            )
        with col_b:
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=f"{safe_name}.csv",
                mime="text/csv",
                key="export_csv",
            )
        with col_c:
            st.download_button(
                label="Download Markdown",
                data=md_data,
                file_name=f"{safe_name}.md",
                mime="text/markdown",
                key="export_markdown",
            )


def render_plan(plan):
    """把 SpatialPlan 渲染到页面上。"""

    st.subheader("Project Summary")
    col1, col2, col3 = st.columns(3)

    total_area = sum(space.area for space in plan.spaces)

    col1.metric("项目名称", plan.project_name)
    col2.metric("目标面积", f"{plan.target_area:.0f} ㎡")
    col3.metric("空间总面积", f"{total_area:.0f} ㎡")

    if total_area > plan.target_area:
        st.warning(
            f"空间总面积超过目标面积 {(total_area - plan.target_area):.0f} ㎡"
        )
    else:
        st.success(
            f"剩余可用面积 {(plan.target_area - total_area):.0f} ㎡"
        )

    st.subheader("Spatial Program")
    st.dataframe(
        [
            {
                "空间": space.name,
                "面积(㎡)": space.area,
                "用途": space.purpose,
            }
            for space in plan.spaces
        ],
        use_container_width=True,
    )

    st.subheader("Spatial Relationships")
    for relationship in plan.relationships:
        st.write(
            f"**{relationship.space_a}** "
            f"-- {relationship.relationship} -- "
            f"**{relationship.space_b}**"
        )
        st.caption(relationship.reason)

    st.subheader("Constraints")
    warnings = check_relationships(plan)

    if not warnings:
        st.success("没有发现明显的空间关系冲突。")
    else:
        for warning in warnings:
            st.warning(warning)

    st.subheader("Adjacency Graph")
    graph_fig = draw_spatial_graph(plan, show_plot=False)
    st.pyplot(graph_fig)
    plt.close(graph_fig)

    st.subheader("Abstract Layout")
    layout_fig = draw_spatial_layout(plan, show_plot=False)
    st.pyplot(layout_fig)
    plt.close(layout_fig)


st.title("SPATIAL BRIEF AGENT")
st.caption("把建筑需求书转换成结构化空间方案，并支持迭代修改")

if "deepseek_api_key_override" not in st.session_state:
    st.session_state.deepseek_api_key_override = ""

_debug = show_deploy_diagnostics()
_session_key = st.session_state.deepseek_api_key_override if _debug else ""
bootstrap_api_key(_session_key)

if _debug:
    with st.sidebar:
        if get_deepseek_api_key():
            if st.session_state.deepseek_api_key_override.strip():
                st.success("API Key 已就绪（本会话粘贴）")
            else:
                st.success("API Key 已就绪（.env / Streamlit Secrets）")
        with st.expander("备用：手动粘贴 API Key", expanded=False):
            st.caption(
                "正式环境请在 Streamlit Cloud → Settings → Secrets 配置 "
                "DEEPSEEK_API_KEY，Save 后 Reboot。"
            )
            st.session_state.deepseek_api_key_override = st.text_input(
                "DeepSeek API Key",
                type="password",
                value=st.session_state.deepseek_api_key_override,
                placeholder="sk-...",
                label_visibility="collapsed",
            )
            bootstrap_api_key(st.session_state.deepseek_api_key_override)
        render_key_diagnostics_sidebar()

if "plan" not in st.session_state:
    st.session_state.plan = None

if "messages" not in st.session_state:
    st.session_state.messages = []

brief = st.text_area(
    "Tell me about your project:",
    value=DEFAULT_BRIEF.strip(),
    height=220,
)

if st.button("Analyze Brief", type="primary"):
    if not get_deepseek_api_key():
        st.error(missing_api_key_error_message())
    else:
        with st.spinner("正在分析建筑需求..."):
            st.session_state.plan = analyze_brief(brief)
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "已完成初始分析。你可以继续提出修改，例如：把儿童活动区增加到 700㎡。",
            }
        ]
        st.rerun()

if st.session_state.plan is not None:
    render_export_section(st.session_state.plan)
    st.divider()
    render_plan(st.session_state.plan)

    st.divider()
    st.subheader("Agent Chat")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    modification = st.chat_input(
        "提出修改，例如：把咖啡厅增加到 400㎡"
    )

    if modification:
        st.session_state.messages.append(
            {"role": "user", "content": modification}
        )

        with st.spinner("Agent 正在更新方案..."):
            updated_plan, reply = run_modification(
                st.session_state.plan,
                modification,
            )
            st.session_state.plan = updated_plan
            st.session_state.messages.append(
                {"role": "assistant", "content": reply}
            )

        st.rerun()