from dataclasses import dataclass

from core.models import Relationship, SpatialPlan


def find_relationship(
    plan: SpatialPlan, space_a: str, space_b: str
) -> Relationship | None:
    """返回 space_a 与 space_b 之间的 Relationship；没有则 None。"""
    pair = {space_a, space_b}
    for rel in plan.relationships:
        if {rel.space_a, rel.space_b} == pair:
            return rel
    return None


@dataclass(frozen=True)
class RelationshipRule:
    space_a: str
    space_b: str
    forbidden: frozenset[str]
    message: str


RELATIONSHIP_RULES: list[RelationshipRule] = [
    RelationshipRule(
        space_a="图书馆",
        space_b="儿童活动区",
        forbidden=frozenset({"close"}),
        message="⚠️ 图书馆与儿童活动区被设置为 close，可能存在噪音冲突。",
    ),
    RelationshipRule(
        space_a="儿童活动区",
        space_b="户外公共空间",
        forbidden=frozenset({"far"}),
        message="⚠️ 儿童活动区与户外公共空间距离过远，可能降低户外活动的便利性。",
    ),
]


@dataclass(frozen=True)
class ExpectedRelationshipRule:
    space_a: str
    space_b: str
    expected: frozenset[str]
    message_if_missing: str
    message_if_wrong: str


EXPECTED_RELATIONSHIP_RULES: list[ExpectedRelationshipRule] = [
    ExpectedRelationshipRule(
        space_a="咖啡厅",
        space_b="户外公共空间",
        expected=frozenset({"close", "medium"}),
        message_if_missing="⚠️ 未定义咖啡厅与户外公共空间的关系，建议保持 close 或 medium。",
        message_if_wrong="⚠️ 咖啡厅与户外公共空间关系偏弱，建议调整为 close 或 medium。",
    ),
]


def _check_relationship_rules(plan: SpatialPlan) -> list[str]:
    warnings: list[str] = []
    for rule in RELATIONSHIP_RULES:
        rel = find_relationship(plan, rule.space_a, rule.space_b)
        if rel is not None and rel.relationship in rule.forbidden:
            warnings.append(rule.message)
    return warnings


def _check_expected_relationship_rules(plan: SpatialPlan) -> list[str]:
    warnings: list[str] = []
    for rule in EXPECTED_RELATIONSHIP_RULES:
        rel = find_relationship(plan, rule.space_a, rule.space_b)
        if rel is None:
            warnings.append(rule.message_if_missing)
        elif rel.relationship not in rule.expected:
            warnings.append(rule.message_if_wrong)
    return warnings


def _check_area_rules(plan: SpatialPlan) -> list[str]:
    total = sum(space.area for space in plan.spaces)
    if total > plan.target_area:
        over = total - plan.target_area
        return [
            f"⚠️ 空间总面积 {total:.0f} ㎡ 超过目标 {plan.target_area:.0f} ㎡"
            f"（超出 {over:.0f} ㎡）。"
        ]
    return []


def check_relationships(plan: SpatialPlan) -> list[str]:
    """
    检查空间关系与面积是否符合我们定义的基本设计规则。

    注意：这里不是建筑规范，是我们自己的 MVP 规则系统。
    """
    warnings: list[str] = []
    warnings.extend(_check_relationship_rules(plan))
    warnings.extend(_check_expected_relationship_rules(plan))
    warnings.extend(_check_area_rules(plan))
    return warnings
