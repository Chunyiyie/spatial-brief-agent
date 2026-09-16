import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

response = client.responses.create(
    model="deepseek-v4-flash",
    input="""
你是一名建筑空间策划助手。

请分析下面的项目需求：

一个 5,000 平方米的社区中心，主要服务儿童、老年人和家庭。

项目需要包括：
- 图书馆
- 咖啡厅
- 儿童活动区
- 老年人活动区
- 多功能房间
- 户外公共空间

请完成以下任务：
1. 识别项目中应该包含的主要空间。
2. 对每个空间说明它的主要功能和用途。
3. 简要说明不同空间之间可能存在的关系。

请使用中文回答。
"""
)

print(response.output_text)