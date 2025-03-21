## 测试启动入口文件
- main.py



## 测试配置修改

- redis相关配置，可以在`core/redis/RedisConfig.py`修改，或者在`core/http/create_app.py`中实例化`RedisConfig`对象时传参
- 配置连接Perplexica后端服务的地址：在`core/constant/__init__.py`里进行修改


## 接口调用
```json
# 请求地址
http://127.0.0.1:18081/api/aggregator

# 请求方式：POST

# body参数
{
    "query": "Talk about world news",
    "focusModes": ["webSearch", "academicSearch"],
    "options": {
        "summary": true  # 是否开启归纳总结
    }
}
```

