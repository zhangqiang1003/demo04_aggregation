
import asyncio
import json
import os

from typing import Dict, List
from .focus_modes import FocusModeHandler
from .. import logger
from ..tongyi.tongyi_summary import TongyiSummary

from ..utils.hash_util import HashUtil


class Aggregator:

    def __init__(self, app: any):

        self.redis = app.redis
        self.focus_handler = FocusModeHandler()

        self.llm_api_key = os.environ.get('DASHSCOPE_API_KEY')
        self.llm_enabled = bool(self.llm_api_key)
        self.logger = logger

    async def process_request(self, query: str, focus_modes: List[str], options: Dict):

        # 检查缓存
        cache_key = HashUtil.generate_cache_key(f"{query + ''.join(sorted(focus_modes))}")
        if cached := self.redis.get(cache_key):
            return json.loads(cached)

        # 多聚合获取数据
        tasks = [self.focus_handler.fetch(mode, query) for mode in focus_modes]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理结果
        aggregated = {
            "query": query,
            "focusModes": focus_modes,
            "aggregatedResults": [
                {"source": mode, "items": result}
                for mode, result in zip(focus_modes, results)
                if not isinstance(result, Exception)
            ]
        }

        # 生成总结
        if self.llm_enabled and options.get('summary', False):
            aggregated['summary'] = await self._generate_summary(aggregated)

        # 缓存
        self.redis.set(cache_key, json.dumps(aggregated), 300)
        return aggregated

    async def _generate_summary(self, data: Dict):
        try:
            # 使用通义千问进行归纳总结
            query = data.get("query")
            aggregated_results = data.get("aggregatedResults")
            results = [result for result in aggregated_results]
            summary_content = TongyiSummary.summarize(query, results)

            return summary_content
        except Exception as e:
            self.logger.error(f"LLM Summary failed: {str(e)}")
            return ""


