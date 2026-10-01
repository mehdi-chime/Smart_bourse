from database.database import Database
from models.stock import Stock

db = Database()

db.connect()

db.create_tables()

stock = Stock()

stock.symbol = "FOOLAD"
stock.trade_date = "2026-07-21"
stock.open_price = 3200
stock.high_price = 3300
stock.low_price = 3180
stock.close_price = 3280
stock.volume = 1450000

db.insert_stock(stock)

print()

print("===== STOCKS =====")

stocks = db.get_all_stocks()

for row in stocks:

    print(row)

db.close()
