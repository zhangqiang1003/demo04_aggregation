
from quart import Blueprint, request
from core import logger
from core.http.async_app import app

from core.http.base_response import ok
from core.redis.decorators import cache_request

aggregator_bp = Blueprint("aggregator", __name__)


@aggregator_bp.route("/api/aggregator", methods=["POST"])
@cache_request(ttl=300)  # 使用装饰器
async def aggregator():
    """
    query: 对话请求参数
    focusModes: focus模式列表
    options: 其它参数
    """
    data = await request.get_json()
    result = await app.aggregator_core.process_request(
        query=data['query'],
        focus_modes=data['focusModes'],
        options=data.get('options', {})
    )

    if result.get("error"):
        logger.info(f"async_search_aggregator error : {result}")
        return ok("")

    # 返回数据结构
    """{
        "query": "...",
        "focusModes": [...],
        "aggregatedResults": [...],
        "summary": "..."
    }"""

    return ok(result)
