from wredis.bitmap import RedisBitmapManager


bitmap_manager = RedisBitmapManager(host="localhost")

bitmap_manager.set_bit(key="my_bitmap", offset=5, value=1)
