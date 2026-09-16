from core.rules import check_relationships
import csv
import io

from core.models import SpatialPlan
def plan_to_json(plan: SpatialPlan) -> str:
    return plan.model_dump_json(indent=2, ensure_ascii=False)

def plan_to_csv(plan: SpatialPlan) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)

    writer.writerow(["# project", plan.project_name])
    writer.writerow(["# target_area_sqm", plan.target_area])
    writer.writerow([])

    writer.writerow(["space_name", "area_sqm", "purpose"])
    for space in plan.spaces:
        writer.writerow([space.name, space.area, space.purpose])

    writer.writerow([])
    writer.writerow(["space_a", "space_b", "relationship", "reason"])
    for rel in plan.relationships:
        writer.writerow([rel.space_a, rel.space_b, rel.relationship, rel.reason])

    return buffer.getvalue()

def plan_to_markdown_report(plan: SpatialPlan) -> str:
    total_area = sum(s.area for s in plan.spaces)
    lines: list[str] = []

    lines.append(f"# {plan.project_name}")
    lines.append("")
    lines.append(f"- 目标面积：**{plan.target_area:.0f} ㎡**")
    lines.append(f"- 空间总面积：**{total_area:.0f} ㎡**")
    lines.append("")

    lines.append("## 空间清单")
    lines.append("")
    lines.append("| 空间 | 面积(㎡) | 用途 |")
    lines.append("| --- | ---: | --- |")
    for s in plan.spaces:
        lines.append(f"| {s.name} | {s.area:.0f} | {s.purpose} |")
    lines.append("")

    lines.append("## 空间关系")
    lines.append("")
    for rel in plan.relationships:
        lines.append(
            f"- **{rel.space_a}** — {rel.relationship} — **{rel.space_b}**：{rel.reason}"
        )
    lines.append("")

    lines.append("## 规则检查")
    lines.append("")
    warnings = check_relationships(plan)
    if not warnings:
        lines.append("_未发现明显冲突。_")
    else:
        for w in warnings:
            lines.append(f"- {w}")

    return "\n".join(lines)