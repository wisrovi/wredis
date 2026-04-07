from wredis.sync import RedisHyperLogLogManager

hll = RedisHyperLogLogManager(host="localhost")

hll.add("visitors", "user1", "user2", "user3", "user4", "user5")
hll.add("visitors", "user6", "user7")

count = hll.count("visitors")
print(f"Unique visitors: {count}")
