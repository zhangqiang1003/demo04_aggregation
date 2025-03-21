from functools import wraps
import json
from quart import request

from core import logger
from core.http.base_response import ok

from core.utils.hash_util import HashUtil


def cache_request(ttl: int = None):
    """缓存装饰器，自动处理请求参数序列化"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            from core.http.async_app import app
            redis = app.redis

            # 生成唯一缓存键
            params = await request.get_json()
            key = HashUtil.generate_cache_key(params)

            # 尝试获取缓存
            if cached := redis.get(key):
                logger.info("cache hit")
                return ok(json.loads(cached))
            logger.info("cache miss")

            # 执行原函数
            result = await func(*args, **kwargs)

            _result = json.loads(result)

            # 写入缓存
            redis.set(key, json.dumps(_result.get("data") or ""), ttl=ttl)
            return result

        return wrapper

    return decorator
