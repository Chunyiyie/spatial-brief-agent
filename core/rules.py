from core.models import SpatialPlan


def check_relationships(plan: SpatialPlan):
    """
    检查空间关系是否符合我们定义的基本设计规则。

    注意：

    这里不是建筑规范。

    这是我们自己的 MVP 规则系统。
    """


    warnings = []


    # ========================================================
    # 规则 1
    # ========================================================
    # 图书馆与儿童活动区不应该 close。
    #
    # 原因：
    # 儿童活动通常具有更高的声音和活动强度。
    #
    # 这是一个非常简化的示例。
    # ========================================================

    for relationship in plan.relationships:

        spaces = {
            relationship.space_a,
            relationship.space_b
        }


        if (
            "图书馆" in spaces
            and "儿童活动区" in spaces
        ):

            if relationship.relationship == "close":

                warnings.append(
                    "⚠️ 图书馆与儿童活动区被设置为 close，"
                    "可能存在噪音冲突。"
                )


    # ========================================================
    # 规则 2
    # ========================================================
    # 儿童活动区最好与户外公共空间保持 close。
    # ========================================================

    for relationship in plan.relationships:

        spaces = {
            relationship.space_a,
            relationship.space_b
        }


        if (
            "儿童活动区" in spaces
            and "户外公共空间" in spaces
        ):

            if relationship.relationship == "far":

                warnings.append(
                    "⚠️ 儿童活动区与户外公共空间距离过远，"
                    "可能降低户外活动的便利性。"
                )


    return warnings