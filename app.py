import matplotlib.pyplot as plt
import streamlit as st

from core.agent import run_modification
from core.llm import analyze_brief
from core.rules import check_relationships
from core.visualize import draw_spatial_graph
from core.layout import draw_spatial_layout


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


st.set_page_config(
    page_title="Spatial Brief Agent",
    page_icon="🏛️",
    layout="wide",
)

st.title("SPATIAL BRIEF AGENT")
st.caption("把建筑需求书转换成结构化空间方案，并支持迭代修改")

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
    with st.spinner("正在分析建筑需求..."):
        st.session_state.plan = analyze_brief(brief)
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "已完成初始分析。你可以继续提出修改，例如：把儿童活动区增加到 700㎡。",
            }
        ]

if st.session_state.plan is not None:
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