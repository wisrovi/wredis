from wredis.ha import SentinelRedisManager

sentinel_nodes = [
    ("localhost", 26379),
    ("localhost", 26380),
    ("localhost", 26381),
]

manager = SentinelRedisManager(
    sentinel_nodes=sentinel_nodes,
    service_name="mymaster",
)

master = manager.get_master()
slave = manager.get_slave()

master.set("key", "value")
value = master.get("key")

print(f"Value from master: {value}")

if slave:
    slave_value = slave.get("key")
    print(f"Value from slave: {slave_value}")
