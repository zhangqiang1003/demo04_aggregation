

import os
import traceback
from typing import List

import dashscope
from dashscope.api_entities.dashscope_response import Message

from core import logger

"""
使用通义进行总结
"""


class TongyiSummary(object):

    @staticmethod
    def summarize(user_query: str, query_result: List[str]) -> str:
        """
        总结多聚合返回的结果
        :param user_query: 用户查询内容
        :param query_result: 多聚合查询返回的结果
        :return:
        """
        system_prompt = """
        ## 核心能力
        精准识别用户核心诉求，对已获取的答案进行结构化重组与语义浓缩，实现信息价值的二次提纯。
        ## 关键功能
        1. 问题 - 答案映射分析
        2. 逻辑关系可视化重组
        3. 信息熵减处理
        ## 关键限制
        1. 严格遵循问答对应原则（Q-A Pair Mapping）
        2. 禁止任何外部知识引入
        3. 保持原始答案完整性（信息保真度≥95%）
        4. 语法结构优化需保持语义等价
        ## 输出要求
        1. 采用「分点概述 + 层级递进」结构
        2. 关键数据 / 结论前置
        3. 技术术语智能标注
        4. 逻辑链条可视化（如：因果→∴ 转折→↔）
        注：执行过程需通过 BERT-based 语义相似度校验，确保总结内容与原始答案的余弦相似度≥0.85
        """

        user_prompt = f"""
        用户问题：{user_query}
        
        问题答案：{query_result}
        """

        messages = [
            Message(role='system', content=system_prompt),
            Message(role='user', content=user_prompt)
        ]
        try:
            response = dashscope.Generation.call(
                # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
                api_key=os.getenv('DASHSCOPE_API_KEY'),
                model="qwen-plus",
                # 此处以qwen-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
                messages=messages,
                result_format='message'
            )

            return response.output.choices[0].message.content
        except Exception as e:
            logger.error(f"问题归纳总结失败，原因是：\n {e}")
            logger.error(traceback.format_exc())
            return ""


if __name__ == '__main__':
    os.environ.setdefault("DASHSCOPE_API_KEY", "sk-c94f53464cbc4a8194315971ac19da6e")
    TongyiSummary.summarize("你是谁?", ["我是Qwen，由阿里云开发的AI助手。我被设计用来回答各种问题、提供信息以及与用户进行对话。无论是技术问题、知识查询还是闲聊，我都尽力提供帮助。如果你有任何问题或需要协助，随时可以告诉我！", "从另一个角度来看，我是一个基于人工智能技术构建的对话系统，专注于理解和生成自然语言。我的目的是通过文本交流为用户提供支持，解答疑问，提供知识，以及帮助解决问题。我是阿里云的一部分，利用了最新的机器学习和深度学习算法来不断提升我的能力，以便更好地服务用户。简单来说，我就是你通过文字交流的一个智能伙伴，旨在为你提供信息查询、任务协助等多种服务。"])