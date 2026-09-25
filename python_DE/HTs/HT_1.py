import json
PATH = 'data/purchase_log.txt'

purchases = {}

with open(PATH, 'r', encoding='utf-8') as f:
    next(f)
    for i in f:
        data = json.loads(i.strip())
        purchases[data['user_id']] = data['category']   # кортеж

for user_id, category in list(purchases.items())[:2]:   # итератор достаёт два значения из кортежа
    print(f"{user_id} '{category}'\n")


"""
items_iter = iter(purchases.items())

print(next(items_iter))
print(next(items_iter))

"""