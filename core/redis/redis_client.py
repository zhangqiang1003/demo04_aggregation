# from typing import Optional
#
# from aioredis import Redis, from_url
# from core import logger
#
#
# class RedisClient:
#     def __init__(self, config):
#         self.config = config
#         self.client: Optional[Redis] = None
#
#     async def connect(self):
#         """初始化连接池"""
#         self.client = await from_url(
#             self.config.url,
#             minsize=self.config.min_conn,
#             maxsize=self.config.max_conn,
#             socket_timeout=self.config.timeout,
#             password=self.config.password
#         )
#         logger.info("Redis连接池初始化完成")
#
#     async def close(self):
#         """关闭连接"""
#         if self.client:
#             await self.client.close()
#             logger.info("Redis连接已关闭")
#
#     async def get(self, key: str) -> Optional[bytes]:
#         """安全获取数据"""
#         try:
#             return await self.client.get(key)
#         except Exception as e:
#             logger.error(f"Redis GET操作失败: {str(e)}")
#             return None
#
#     async def set(self, key: str, value, ttl: int = None):
#         """安全设置数据"""
#         try:
#             actual_ttl = ttl or self.config.default_ttl
#             return await self.client.set(key, value, ex=actual_ttl)
#         except Exception as e:
#             logger.error(f"Redis SET操作失败: {str(e)}")
from typing import Union, Optional

from redis import RedisError, ConnectionPool, Redis

from core import logger
from core.redis.redis_config import RedisConfig


class RedisClient:
    """基于redis-py的异步Redis客户端封装"""

    def __init__(self, config: RedisConfig):
        self.config = config
        self.pool: Optional[ConnectionPool] = None
        self.client: Optional[Redis] = None

    def connect(self) -> None:
        """初始化连接池"""
        try:
            self.pool = ConnectionPool.from_url(
                self.config.url,
                max_connections=self.config.max_conn,
                socket_timeout=self.config.socket_timeout,
                password=self.config.password,
                decode_responses=False  # 保持字节数据
            )
            self.client = Redis(connection_pool=self.pool)

            # 验证连接
            # await self.client.ping()
            logger.info(f"Redis连接池已建立，活跃连接数：{self.pool._in_use_connections}")
        except RedisError as e:
            logger.error(f"Redis连接失败: {str(e)}")
            raise

    def close(self) -> None:
        """关闭连接池"""
        if self.pool:
            self.pool.disconnect()
            logger.info("Redis连接池已关闭")
        if self.client:
            self.client.close()

    def get(self, key: str) -> Optional[bytes]:
        """安全获取数据（返回原始字节）"""
        try:
            return self.client.get(key)
        except RedisError as e:
            logger.error(f"GET操作失败 [{key}]: {str(e)}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return None

    def set(
            self,
            key: str,
            value: Union[str, bytes, int, float],
            ttl: Optional[int] = None
    ) -> bool:
        """
        安全设置数据
        :param ttl: 过期时间（秒），None表示使用默认TTL
        :return: 是否设置成功
        """
        try:
            actual_ttl = ttl if ttl is not None else self.config.default_ttl
            result = self.client.set(
                name=key,
                value=value,
                ex=actual_ttl
            )
            return result is True
        except RedisError as e:
            logger.error(f"SET操作失败 [{key}]: {str(e)}", exc_info=True)
            return False

    async def execute_command(self, command: str, *args, **kwargs) -> any:
        """执行原始Redis命令"""
        try:
            return await self.client.execute_command(command, *args, **kwargs)
        except RedisError as e:
            logger.error(f"命令执行失败 [{command}]: {str(e)}")
            raise


# 使用示例
if __name__ == "__main__":
    import asyncio


    def main():
        config = RedisConfig()

        client = RedisClient(config)
        try:
            client.connect()
            client.set("test_key", "Hello Redis!", ttl=60)
            value = client.get("test_key")
            print(f"获取到的值: {value}")
        finally:
            client.close()


    # asyncio.run(main())
    main()


