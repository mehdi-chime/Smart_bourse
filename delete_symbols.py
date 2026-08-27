from database.database import Database

db = Database()
db.connect()

db.cursor.execute("DROP TABLE IF EXISTS symbols")

db.connection.commit()

db.close()

print("Old symbols table deleted.")
