import math

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import networkx as nx

from core.models import SpatialPlan


RELATIONSHIP_COLORS = {
    "close": "#2E7D32",
    "medium": "#546E7A",
    "far": "#EF6C00",
    "avoid": "#C62828",
}


def build_graph(plan: SpatialPlan):
    """
    把 SpatialPlan 转成 networkx 图。
    """

    graph = nx.Graph()

    for space in plan.spaces:
        graph.add_node(space.name, area=space.area)

    for relationship in plan.relationships:
        graph.add_edge(
            relationship.space_a,
            relationship.space_b,
            relationship=relationship.relationship,
        )

    return graph


def compute_rectangle_size(area: float, scale: float = 0.08):
    """
    根据面积计算矩形边长。

    使用 sqrt(area) 是因为：
    面积 ∝ 边长 × 边长
    所以边长 ∝ sqrt(面积)
    """

    side = math.sqrt(max(area, 1.0)) * scale
    return side, side


def draw_spatial_layout(
    plan: SpatialPlan,
    output_path: str = "spatial_layout.png",
    show_plot: bool = True,
):
    """
    把 SpatialPlan 画成抽象 2D 矩形布局。
    """

    plt.rcParams["font.sans-serif"] = [
        "PingFang SC",
        "Heiti SC",
        "Arial Unicode MS",
        "SimHei",
    ]
    plt.rcParams["axes.unicode_minus"] = False

    graph = build_graph(plan)
    pos = nx.spring_layout(graph, seed=42, k=1.8)

    fig, ax = plt.subplots(figsize=(14, 10))

    for space in plan.spaces:
        x, y = pos[space.name]
        width, height = compute_rectangle_size(space.area)

        rect = patches.Rectangle(
            (x - width / 2, y - height / 2),
            width,
            height,
            linewidth=1.5,
            edgecolor="#1F2933",
            facecolor="#E8EEF2",
        )
        ax.add_patch(rect)

        ax.text(
            x,
            y,
            f"{space.name}\n{space.area:.0f}㎡",
            ha="center",
            va="center",
            fontsize=9,
            color="#1F2933",
        )

    for space_a, space_b, data in graph.edges(data=True):
        rel_type = data.get("relationship", "medium")
        color = RELATIONSHIP_COLORS.get(rel_type, "#546E7A")

        x1, y1 = pos[space_a]
        x2, y2 = pos[space_b]

        ax.plot(
            [x1, x2],
            [y1, y2],
            color=color,
            linewidth=1.5,
            linestyle="--" if rel_type == "avoid" else "-",
            alpha=0.7,
        )

    ax.set_title(f"{plan.project_name} 抽象空间布局")
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    print(f"\n已保存图片：{output_path}")

    if show_plot:
        plt.show()

    return fig