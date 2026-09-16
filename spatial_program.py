import os

from dotenv import load_dotenv
from openai import OpenAI

from core.models import SpatialProgram


# ============================================================
# 1. 读取 .env 文件
# ============================================================
# .env 中保存我们的 DeepSeek API Key。
#
# 例如：
#
# DEEPSEEK_API_KEY=你的API_KEY
#
# 注意：
# API Key 不应该直接写在 Python 代码里面。
# ============================================================

load_dotenv()


# ============================================================
# 2. 创建 DeepSeek API 客户端
# ============================================================
# DeepSeek 提供了与 OpenAI SDK 兼容的 API。
#
# 因此我们可以使用 OpenAI() 这个客户端，
# 但是把 base_url 指向 DeepSeek。
# ============================================================

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)


# ============================================================
# 3. 建立建筑项目需求
# ============================================================
# 这是用户输入给 AI 的项目 Brief。
#
# 以后我们会把这里改造成：
#
# 用户在网页输入 Brief
#        ↓
# Python
#        ↓
# DeepSeek
#
# 现在为了学习，我们先直接写在代码里面。
# ============================================================

project_brief = """
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

请分析这个项目，并建立一个合理的空间需求表。

请为每个空间提供：
1. 空间名称
2. 建议面积
3. 空间用途

总面积目标为 5,000 平方米。

请使用中文。
"""


# ============================================================
# 4. 请求 DeepSeek 分析项目
# ============================================================
# 注意：
#
# 我们这里要求 AI 输出 JSON。
#
# JSON 的结构会对应 SpatialProgram。
#
# 也就是说：
#
# AI
# ↓
# JSON
# ↓
# Pydantic
# ↓
# Python 对象
#
# ============================================================

response = client.chat.completions.create(
    model="deepseek-v4-flash",

    messages=[
        {
            "role": "system",
            "content": """
你是一名建筑空间策划助手。

你的任务是把建筑项目需求转换成结构化的空间需求数据。

必须输出 JSON。

JSON 必须包含：

project_name
target_area
spaces

其中 spaces 是一个列表。

每个空间必须包含：

name
area
purpose

area 必须是数字，单位为平方米。

不要输出 Markdown。
不要输出解释。
只输出 JSON。
""",
        },
        {
            "role": "user",
            "content": project_brief,
        },
    ],

    # 要求模型返回 JSON
    response_format={
        "type": "json_object"
    },
)


# ============================================================
# 5. 获取 AI 返回的 JSON
# ============================================================

raw_json = response.choices[0].message.content


print("\n========== AI 原始输出 ==========\n")

print(raw_json)


# ============================================================
# 6. 将 JSON 转换成 Python 数据
# ============================================================
# Pydantic 会检查：
#
# project_name 是不是字符串？
# target_area 是不是数字？
# spaces 是不是列表？
# 每个 space 有没有：
#   name
#   area
#   purpose
#
# 如果 AI 返回的数据结构不符合要求，
# Pydantic 会报错。
# ============================================================

program = SpatialProgram.model_validate_json(raw_json)


# ============================================================
# 7. 输出结构化数据
# ============================================================

print("\n========== 空间需求 ==========\n")

print(f"项目名称：{program.project_name}")

print(f"目标面积：{program.target_area}㎡")


for space in program.spaces:

    print("\n--------------------")

    print(f"空间：{space.name}")

    print(f"面积：{space.area}㎡")

    print(f"用途：{space.purpose}")


# ============================================================
# 8. 计算空间总面积
# ============================================================
# 这里非常重要。
#
# 我们没有让 AI 计算总面积。
#
# 而是让 Python 来计算。
#
# 这是 AI 系统设计中的一个重要原则：
#
# AI 负责：
# 理解需求
# 推理
# 生成方案
#
# Python 负责：
# 精确计算
# 数据处理
# 规则判断
# ============================================================

total_area = sum(
    space.area
    for space in program.spaces
)


print("\n========== 面积检查 ==========\n")

print(f"空间总面积：{total_area}㎡")

print(f"目标面积：{program.target_area}㎡")


# ============================================================
# 9. 检查是否超过目标面积
# ============================================================

if total_area > program.target_area:

    print("⚠️ 警告：空间总面积超过项目目标面积！")

else:

    remaining_area = program.target_area - total_area

    print("✓ 空间总面积没有超过目标面积。")

    print(f"剩余面积：{remaining_area}㎡")