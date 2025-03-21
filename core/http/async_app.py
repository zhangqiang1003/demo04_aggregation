import os

from quart import Quart, jsonify

from core import logger
from core.aggregator.aggregator_core import Aggregator
from core.http.base_exception import *
from core.redis.redis_client import RedisClient
from core.redis.redis_config import RedisConfig


"""
任务初始化
"""
app = Quart(__name__)

"""初始化redis相关配置"""
cfg = RedisConfig()

# 通义的api-key
os.environ.setdefault("DASHSCOPE_API_KEY", "sk-c94f53464cbc4a8194315971ac19da6e")


@app.before_serving
async def init_services():
    """服务启动初始化"""
    app.redis = RedisClient(cfg)
    app.redis.connect()

    app.aggregator_core = Aggregator(app)


@app.after_serving
async def shutdown_services():
    """服务关闭清理"""
    if bool(getattr(app, "redis")):
        app.redis.close()


"""注册蓝图"""
from views.http_aggregator import aggregator_bp
app.register_blueprint(aggregator_bp)

"""异常类注册"""


@app.errorhandler(Exception)
def framework_error(e):
    print()
    logger.exception(e)
    if isinstance(e, ParamError):
        return jsonify({'code': e.code, 'msg': e.msg}), 200
    if isinstance(e, AuthError):
        return jsonify({'code': e.code, 'msg': e.msg}), 200
    if isinstance(e, NotFound):
        return jsonify({'code': e.code, 'msg': e.msg}), 200
    if isinstance(e, InternalError):
        return jsonify({'code': 500, 'msg': e.msg}), 200
    else:
        return jsonify({'code': 500, 'msg': 'Server error'}), 200
