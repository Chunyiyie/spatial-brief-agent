from core.llm import modify_plan
from core.models import SpatialPlan
from core.rules import check_relationships


def run_modification(
    current_plan: SpatialPlan,
    modification: str,
) -> tuple[SpatialPlan, str]:
    """
    Agent 主循环：

    1. LLM 修改方案
    2. Python 重算面积
    3. Python 检查规则
    4. 生成文字回复
    """

    updated_plan = modify_plan(current_plan, modification)

    old_total = sum(space.area for space in current_plan.spaces)
    new_total = sum(space.area for space in updated_plan.spaces)

    warnings = check_relationships(updated_plan)

    reply_lines = [
        f"已根据你的要求更新方案：{modification}",
        "",
        f"空间总面积：{old_total:.0f}㎡ → {new_total:.0f}㎡",
        f"目标面积：{updated_plan.target_area:.0f}㎡",
    ]

    if new_total > updated_plan.target_area:
        reply_lines.append(
            f"⚠ 当前空间总面积超过目标 {(new_total - updated_plan.target_area):.0f}㎡"
        )
    else:
        reply_lines.append(
            f"✓ 剩余可用面积 {(updated_plan.target_area - new_total):.0f}㎡"
        )

    if warnings:
        reply_lines.append("")
        reply_lines.append("规则检查：")
        reply_lines.extend(warnings)
    else:
        reply_lines.append("")
        reply_lines.append("✓ 没有发现明显的空间关系冲突。")

    return updated_plan, "\n".join(reply_lines)