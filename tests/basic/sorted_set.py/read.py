from wredis.sortedset import RedisSortedSetManager


sorted_set_manager = RedisSortedSetManager(host="localhost")


items = sorted_set_manager.get_sorted_set("my_sorted_set", with_scores=True)
items_reverse = sorted_set_manager.get_sorted_set_reverse("my_sorted_set")
# Obtener rank y score
rank = sorted_set_manager.get_rank("my_sorted_set", "item1")
score = sorted_set_manager.get_score("my_sorted_set", "item2")

# Eliminar un miembro
sorted_set_manager.remove_from_sorted_set("my_sorted_set", "item1")

# Eliminar todo el conjunto ordenado
# sorted_set_manager.delete_sorted_set("my_sorted_set")


print(items)
print(items_reverse)
print(rank)
print(score)
