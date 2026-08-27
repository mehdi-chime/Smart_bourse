from database.symbol_repository import SymbolRepository

repo = SymbolRepository()
from database.symbol_repository import SymbolRepository

repo = SymbolRepository()

print("================================")
print("SEARCH فولاد")
print("================================")

results = repo.find_like("فول")

print("RESULT COUNT:", len(results))

for row in results:
    print(row)

print("=" * 60)
print("FOOLAD DATABASE TEST")
print("=" * 60)

print("get_inscode:", repo.get_inscode("فولاد"))

print()
print("find_symbol:")
print(repo.find_symbol("فولاد"))

print()
print("find_like:")
print(repo.find_like("فولاد"))

print("=" * 60)
