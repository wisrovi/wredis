from a_wredis import RedisBitmapManager


bitmap_manager = RedisBitmapManager(host="localhost")

print(bitmap_manager.get_bit("my_bitmap", 0))
print(bitmap_manager.count_bits("my_bitmap"))
