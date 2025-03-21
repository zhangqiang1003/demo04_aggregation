from dataclasses import dataclass
from typing import Optional


# @dataclass
# class RedisConfig:
#     url: str = "redis://192.168.10.11:6379"
#     min_conn: int = 5
#     max_conn: int = 20
#     timeout: int = 5
#     default_ttl: int = 300  # 默认缓存时间
#     password: str = "damao123&&"


class RedisConfig:
    """Redis连接配置类"""
    def __init__(
        self,
        url: str = "redis://192.168.10.11:6379/0",
        min_conn: int = 5,
        max_conn: int = 20,
        socket_timeout: int = 60,
        password: Optional[str] = "damao123&&",
        default_ttl: int = 300
    ):
        self.url = url
        self.min_conn = min_conn
        self.max_conn = max_conn
        self.socket_timeout = socket_timeout
        self.password = password
        self.default_ttl = default_ttl
