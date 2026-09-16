import re
from typing import Any

from pydantic import BaseModel, Field, field_validator


def parse_area_number(value: Any) -> Any:
    """
    把 AI 可能返回的面积值转成数字。

    LLM 经常会输出：
        "850平方米"
        "5000㎡"
        "700"

    Python 计算需要的是：
        850.0
        5000.0
        700.0

    所以这里先从字符串里抽出数字，再交给 Pydantic。
    """

    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, str):
        match = re.search(r"-?\d+(?:\.\d+)?", value.replace(",", ""))

        if match:
            return float(match.group())

    return value


class Space(BaseModel):
    """
    建筑中的一个空间。

    例如：
    - 图书馆
    - 咖啡厅
    - 儿童活动区
    """

    name: str = Field(
        description="空间名称"
    )

    area: float = Field(
        description="空间面积，单位为平方米"
    )

    purpose: str = Field(
        description="空间的主要用途"
    )

    @field_validator("area", mode="before")
    @classmethod
    def coerce_area(cls, value: Any) -> Any:
        return parse_area_number(value)


class Relationship(BaseModel):
    """
    两个空间之间的关系。

    relationship 可以是：

    close
    medium
    far
    avoid
    """

    space_a: str = Field(
        description="第一个空间名称"
    )

    space_b: str = Field(
        description="第二个空间名称"
    )

    relationship: str = Field(
        description="两个空间之间的关系：close / medium / far / avoid"
    )

    reason: str = Field(
        description="为什么两个空间需要这样的关系"
    )


class SpatialProgram(BaseModel):
    """
    整个建筑项目的空间需求。

    包含：
    - 项目名称
    - 总面积
    - 空间列表
    """

    project_name: str

    target_area: float

    spaces: list[Space]

    @field_validator("target_area", mode="before")
    @classmethod
    def coerce_target_area(cls, value: Any) -> Any:
        return parse_area_number(value)


class SpatialPlan(BaseModel):
    """
    一个完整的空间规划。

    SpatialPlan 比 SpatialProgram 多了：

    relationships

    也就是说，我们现在不仅知道：

    建筑里有什么空间

    还知道：

    空间之间是什么关系。
    """

    project_name: str

    target_area: float

    spaces: list[Space]

    relationships: list[Relationship]

    @field_validator("target_area", mode="before")
    @classmethod
    def coerce_target_area(cls, value: Any) -> Any:
        return parse_area_number(value)
