"""Integration tests para todos los módulos con Redis real."""

import time

from wredis.bitmap import RedisBitmapManager
from wredis.geo import RedisGeoManager
from wredis.hash import RedisHashManager
from wredis.hyperloglog import RedisHyperLogLogManager
from wredis.pipeline import RedisPipelineManager
from wredis.sets import RedisSetManager
from wredis.sortedset import RedisSortedSetManager


class TestBitmapIntegration:
    """Integration tests para bitmap."""

    def test_set_and_get_bit(self, real_redis):
        """Test set/get bit con Redis real."""
        manager = RedisBitmapManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        manager.set_bit("bitmap", 0, 1)
        manager.set_bit("bitmap", 5, 1)

        assert manager.get_bit("bitmap", 0) == 1
        assert manager.get_bit("bitmap", 1) == 0

    def test_count_bits(self, real_redis):
        """Test count bits con Redis real."""
        manager = RedisBitmapManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        manager.set_bit("bitmap", 0, 1)
        manager.set_bit("bitmap", 1, 1)
        manager.set_bit("bitmap", 2, 1)

        assert manager.count_bits("bitmap") == 3

    def test_ttl_bitmap(self, real_redis):
        """Test TTL con bitmap."""
        manager = RedisBitmapManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        manager.set_bit("bitmap_ttl", 0, 1, ttl=60)
        assert manager.get_ttl("bitmap_ttl") > 0

        manager.extend_ttl("bitmap_ttl", 120)
        assert manager.get_ttl("bitmap_ttl") == 120


class TestGeoIntegration:
    """Integration tests para geo."""

    def test_add_and_get_location(self, real_redis):
        """Test add/get location con Redis real."""
        manager = RedisGeoManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        manager.add_location("cities", "nyc", -74.006, 40.7128)
        manager.add_location("cities", "la", -118.2437, 34.0522)

        positions = manager.get_positions("cities", "nyc", "la")
        assert len(positions) == 2

    def test_distance_between_locations(self, real_redis):
        """Test distancia entre ubicaciones."""
        manager = RedisGeoManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        manager.add_location("cities", "nyc", -74.006, 40.7128)
        manager.add_location("cities", "la", -118.2437, 34.0522)

        distance = manager.get_distance("cities", "nyc", "la", unit="km")
        assert distance is not None
        assert distance > 3000

    def test_search_nearby(self, real_redis):
        """Test búsqueda cercana."""
        manager = RedisGeoManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        manager.add_location("places", "store1", -122.4194, 37.7749)
        manager.add_location("places", "store2", -122.4084, 37.7849)

        nearby = manager.search_nearby("places", -122.4194, 37.7749, 5, unit="km")
        assert len(nearby) >= 1

        nearby_dist = manager.search_nearby_with_distance(
            "places", -122.4194, 37.7749, 5, unit="km"
        )
        assert len(nearby_dist) >= 1


class TestHyperLogLogIntegration:
    """Integration tests para HyperLogLog."""

    def test_add_and_count(self, real_redis):
        """Test add/count con Redis real."""
        manager = RedisHyperLogLogManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        manager.add("visitors", "user1", "user2", "user3")
        assert manager.count("visitors") == 3

    def test_merge_hll(self, real_redis):
        """Test merge de HyperLogLogs."""
        manager = RedisHyperLogLogManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        manager.add("day1", "user1", "user2")
        manager.add("day2", "user2", "user3")
        manager.merge("total", "day1", "day2")

        assert manager.count("total") == 3

    def test_get_all(self, real_redis):
        """Test get_all."""
        manager = RedisHyperLogLogManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        result = manager.get_all("nonexistent")
        assert result == set()


class TestPipelineIntegration:
    """Integration tests para pipeline."""

    def test_execute_commands(self, real_redis):
        """Test pipeline commands con Redis real."""
        manager = RedisPipelineManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        results = manager.execute_commands(
            [
                ("set", ["pipe_key1", "value1"]),
                ("set", ["pipe_key2", "value2"]),
                ("get", ["pipe_key1"]),
            ]
        )

        assert results[0] is True
        assert results[2] == b"value1"

    def test_set_get(self, real_redis):
        """Test set/get en pipeline."""
        manager = RedisPipelineManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        result = manager.set_get("sg_key", "sg_value")
        assert result == b"sg_value"

    def test_mset_mget(self, real_redis):
        """Test mset/mget en pipeline."""
        manager = RedisPipelineManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        manager.mset_pipeline({"m1": "v1", "m2": "v2"})
        results = manager.mget_pipeline("m1", "m2")

        assert results[0] == b"v1"
        assert results[1] == b"v2"

    def test_delete_keys(self, real_redis):
        """Test delete keys en pipeline."""
        manager = RedisPipelineManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        real_redis.set("del1", "v1")
        real_redis.set("del2", "v2")

        deleted = manager.delete_keys("del1", "del2", "nonexistent")
        assert deleted == 2


class TestSetsIntegration:
    """Integration tests para sets."""

    def test_add_and_check_membership(self, real_redis):
        """Test add/check membership con Redis real."""
        manager = RedisSetManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        manager.add_to_set("myset", "a", "b", "c")
        assert manager.is_member("myset", "a") == 1
        assert manager.is_member("myset", "d") == 0

    def test_get_members(self, real_redis):
        """Test get members."""
        manager = RedisSetManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        manager.add_to_set("myset2", "x", "y", "z")
        members = manager.get_set_members("myset2")
        assert len(members) == 3

    def test_remove_from_set(self, real_redis):
        """Test remove from set."""
        manager = RedisSetManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        manager.add_to_set("myset3", "a", "b", "c")
        manager.remove_from_set("myset3", "b")
        assert manager.is_member("myset3", "b") == 0

    def test_ttl_sets(self, real_redis):
        """Test TTL en sets."""
        manager = RedisSetManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        manager.add_to_set("set_ttl", "a", ttl=60)
        assert manager.get_ttl("set_ttl") > 0

        manager.extend_ttl("set_ttl", 120)
        assert manager.get_ttl("set_ttl") == 120


class TestSortedSetIntegration:
    """Integration tests para sorted sets."""

    def test_add_and_get_sorted(self, real_redis):
        """Test add/get sorted con Redis real."""
        manager = RedisSortedSetManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        manager.add_to_sorted_set("zset", 1.0, "a")
        manager.add_to_sorted_set("zset", 2.0, "b")
        manager.add_to_sorted_set("zset", 3.0, "c")

        result = manager.get_sorted_set("zset")
        assert len(result) == 3

    def test_get_sorted_with_scores(self, real_redis):
        """Test get sorted con scores."""
        manager = RedisSortedSetManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        manager.add_to_sorted_set("zset2", 1.0, "a")
        manager.add_to_sorted_set("zset2", 2.0, "b")

        result = manager.get_sorted_set("zset2", with_scores=True)
        assert len(result) == 2

    def test_get_rank_and_score(self, real_redis):
        """Test rank y score."""
        manager = RedisSortedSetManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        manager.add_to_sorted_set("zset3", 1.0, "a")
        manager.add_to_sorted_set("zset3", 2.0, "b")
        manager.add_to_sorted_set("zset3", 3.0, "c")

        assert manager.get_rank("zset3", "b") == 1
        assert manager.get_score("zset3", "b") == 2.0

    def test_remove_and_delete(self, real_redis):
        """Test remove y delete."""
        manager = RedisSortedSetManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        manager.add_to_sorted_set("zset4", 1.0, "a")
        manager.add_to_sorted_set("zset4", 2.0, "b")

        manager.remove_from_sorted_set("zset4", "a")
        assert manager.get_score("zset4", "a") is None

        manager.delete_sorted_set("zset4")
        assert real_redis.exists("zset4") == 0

    def test_increment_score(self, real_redis):
        """Test increment score."""
        manager = RedisSortedSetManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        manager.add_to_sorted_set("zset5", 5.0, "a")
        manager.increment_score("zset5", 3.0, "a")
        assert manager.get_score("zset5", "a") == 8.0

    def test_get_by_score_range(self, real_redis):
        """Test get by score range."""
        manager = RedisSortedSetManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        manager.add_to_sorted_set("zset6", 1.0, "a")
        manager.add_to_sorted_set("zset6", 5.0, "b")
        manager.add_to_sorted_set("zset6", 10.0, "c")

        result = manager.get_sorted_set_by_score("zset6", 2, 8)
        assert len(result) == 1
        assert result[0] == "b"

    def test_ttl_sortedset(self, real_redis):
        """Test TTL en sorted sets."""
        manager = RedisSortedSetManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        manager.add_to_sorted_set("zset_ttl", 1.0, "a", ttl=60)
        assert manager.get_ttl("zset_ttl") > 0

        manager.set_ttl("zset_ttl", 120)
        assert manager.get_ttl("zset_ttl") == 120

    def test_reverse_order(self, real_redis):
        """Test reverse order."""
        manager = RedisSortedSetManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        manager.add_to_sorted_set("zset_rev", 1.0, "a")
        manager.add_to_sorted_set("zset_rev", 2.0, "b")
        manager.add_to_sorted_set("zset_rev", 3.0, "c")

        result = manager.get_sorted_set_reverse("zset_rev")
        assert result[0] == "c"


class TestHashIntegration:
    """Integration tests para hash."""

    def test_create_and_read_hash(self, real_redis):
        """Test create/read hash con Redis real."""
        manager = RedisHashManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        manager.create_hash("myhash", "key1", {"name": "Alice", "age": 30})
        result = manager.read_hash("myhash", "key1")
        assert result["name"] == "Alice"

    def test_update_hash(self, real_redis):
        """Test update hash."""
        manager = RedisHashManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        manager.create_hash("myhash2", "key1", {"name": "Alice"})
        manager.update_hash("myhash2", "key1", {"age": 25})

        result = manager.read_hash("myhash2", "key1")
        assert result["age"] == 25

    def test_delete_hash_field(self, real_redis):
        """Test delete hash field."""
        manager = RedisHashManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        manager.create_hash("myhash3", "key1", "value")
        manager.delete_hash_field("myhash3", "key1")
        assert manager.read_hash("myhash3", "key1") is None

    def test_read_all_hash(self, real_redis):
        """Test read all hash."""
        manager = RedisHashManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        manager.create_hash("myhash4", "k1", "v1")
        manager.create_hash("myhash4", "k2", "v2")

        result = manager.read_all_hash("myhash4")
        assert len(result) == 2

    def test_ttl_hash(self, real_redis):
        """Test TTL en hash."""
        manager = RedisHashManager(host="localhost", verbose=False)
        manager.redis_client = real_redis

        manager.create_hash("myhash5", "key1", "value", ttl=60)
        assert manager.get_ttl("myhash5") > 0

        manager.extend_ttl("myhash5", 120)
        assert manager.get_ttl("myhash5") == 120
