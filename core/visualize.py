import matplotlib.pyplot as plt
import networkx as nx

from core.models import SpatialPlan


RELATIONSHIP_COLORS = {
    "close": "#2E7D32",
    "medium": "#546E7A",
    "far": "#EF6C00",
    "avoid": "#C62828",
}


def draw_spatial_graph(
    plan: SpatialPlan,
    output_path: str = "spatial_layout.png",
    show_plot: bool = True,
):
    """
    把 SpatialPlan 画成空间关系图。

    节点：空间
    边：空间关系
    节点大小：面积
    边的颜色：close / medium / far / avoid
    """

    # Mac 上显示中文
    plt.rcParams["font.sans-serif"] = [
        "PingFang SC",
        "Heiti SC",
        "Arial Unicode MS",
        "SimHei",
    ]
    plt.rcParams["axes.unicode_minus"] = False

    graph = nx.Graph()

    for space in plan.spaces:
        graph.add_node(space.name, area=space.area)

    for relationship in plan.relationships:
        graph.add_edge(
            relationship.space_a,
            relationship.space_b,
            relationship=relationship.relationship,
            reason=relationship.reason,
        )

    pos = nx.spring_layout(graph, seed=42, k=1.4)

    fig, ax = plt.subplots(figsize=(12, 8))

    node_sizes = [
        max(graph.nodes[name]["area"], 200) * 1.5
        for name in graph.nodes
    ]

    nx.draw_networkx_nodes(
        graph,
        pos,
        node_size=node_sizes,
        node_color="#E8EEF2",
        edgecolors="#1F2933",
        linewidths=1.2,
        ax=ax,
    )

    nx.draw_networkx_labels(
        graph,
        pos,
        font_size=10,
        font_color="#1F2933",
        ax=ax,
    )

    for rel_type, color in RELATIONSHIP_COLORS.items():
        edges = [
            (space_a, space_b)
            for space_a, space_b, data in graph.edges(data=True)
            if data.get("relationship") == rel_type
        ]

        if not edges:
            continue

        nx.draw_networkx_edges(
            graph,
            pos,
            edgelist=edges,
            edge_color=color,
            width=2.2,
            style="dashed" if rel_type == "avoid" else "solid",
            ax=ax,
        )

    edge_labels = {
        (space_a, space_b): data["relationship"]
        for space_a, space_b, data in graph.edges(data=True)
    }

    nx.draw_networkx_edge_labels(
        graph,
        pos,
        edge_labels=edge_labels,
        font_size=8,
        ax=ax,
    )

    ax.set_title(f"{plan.project_name} 空间关系图")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    print(f"\n已保存图片：{output_path}")

    if show_plot:
        plt.show()

    return fig