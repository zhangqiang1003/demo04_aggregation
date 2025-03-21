import asyncio
from typing import Dict, Any, List

import aiohttp
import httpx
import yaml
from pathlib import Path

from core.constant import SEARXNG_INSTANCE


class FocusModeHandler:
    def __init__(self):
        # 缓存系统focus modes
        self.sys_focus_modes: List[str] = ["webSearch", "academicSearch", "writingAssistant", "wolframAlphaSearch",
                                           "youtubeSearch", "redditSearch"]
        # 缓存自定义的focus modes
        self.custom_modes = self._load_custom_modes()

    # 加载自定义的focus modes
    @staticmethod
    def _load_custom_modes() -> Dict[str, Any]:
        config_path = Path(__file__).parent / "focus_config.yaml"
        with open(config_path) as f:
            return yaml.safe_load(f)

    # 调用focus modes
    async def fetch(self, mode: str, query: str):
        if mode in self.sys_focus_modes:
            return await self._fetch_sys_mode(mode, query)
        else:
            return await self._fetch_custom_mode(mode, query)

    # 调用自定义的focus modes
    async def _fetch_custom_mode(self, mode: str, query: str):
        config = self.custom_modes.get(mode)
        if not config:
            raise ValueError(f"Invalid focus mode: {mode}")

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.request(
                    method=config['method'],
                    url=config['endpoint'],
                    params={**config.get('params', {}), 'query': query},
                    headers=config.get('headers', {})
                )
                resp.raise_for_status()
                return self._parse_response(config['parser'], resp.json())
            except Exception as e:
                return []

    # 调用系统focus modes
    async def _fetch_sys_mode(self, mode: str, query: str):
        if mode not in self.sys_focus_modes:
            raise ValueError(f"Invalid focus mode: {mode}")

        """修复后的安全搜索方法"""
        connector = aiohttp.TCPConnector(limit=10)  # 添加连接限制
        params = dict()
        params['query'] = query
        params["optimizationMode"] = "speed"
        params["focusMode"] = mode

        try:
            async with aiohttp.ClientSession(
                    connector=connector,
                    timeout=aiohttp.ClientTimeout(total=60),
                    headers={"User-Agent": "Mozilla/5.0"}
            ) as session:

                async with session.post(
                        f"{SEARXNG_INSTANCE}/api/search",
                        json=params,
                        ssl=False  # 如果本地测试可禁用SSL验证
                ) as response:
                    response.raise_for_status()
                    return await response.json()

        except aiohttp.ClientError as e:
            print(f"网络请求异常: {str(e)}")
        except asyncio.TimeoutError:
            print("请求超时")
        except Exception as e:
            print(f"未处理异常: {str(e)}")
        finally:
            await connector.close()  # 显式关闭连接器

        return {"error": "搜索失败"}

    def _parse_response(self, parser_type: str, data: Dict):
        # Implement different parsers for different sources
        if parser_type == "academic":
            return data.get('papers', [])
        elif parser_type == "youtube":
            return [item['snippet'] for item in data.get('items', [])]
        return []
