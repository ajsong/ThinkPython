class Config(object):

    # 数据库连接配置信息
    connections = {
        'mysql': {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'password': '19871011',
            'database': '818ab',
            'prefix': 'pf_',
            'charset': 'utf8'
        }
    }

    # 自动写入时间戳字段
    # True为自动识别类型 False关闭
    # 字符串则明确指定时间字段类型 支持 int timestamp datetime date time year
    auto_timestamp = False

    # 时间字段配置 配置格式：添加时间,更新时间，默认：create_time,update_time
    datetime_field = ''

    # 时间字段取出后的默认时间格式
    datetime_format = '%Y-%m-%d %H:%M:%S'

    # requests自动配置主机头
    api_url = 'http://localhost'

    # 缓存驱动 支持 redis file
    cache_type = 'redis'
