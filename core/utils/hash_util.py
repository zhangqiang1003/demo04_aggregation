# 生成缓存键（带参数哈希）
import hashlib


class HashUtil(object):

    @staticmethod
    def generate_cache_key(params: str) -> str:
        """
        生成redis缓存key
        :param params: 请求参数字符串
        :return: str
        """
        return f"query_{hashlib.md5(str(params).encode()).hexdigest()}"
