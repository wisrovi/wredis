from wredis.sets import RedisSetManager


set_manager = RedisSetManager(host="localhost")


print(set_manager.get_set_members("my_set"))
