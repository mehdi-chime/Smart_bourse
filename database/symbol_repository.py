
"""
Project : Smart_Bourse

File : symbol_repository.py

Version : 2.0.0

Description :
Manage Symbols Table
"""

from database.database import Database


class SymbolRepository:

    def __init__(self):

        self.db = Database()

    # -------------------------------------
    # Normalize Symbol
    # -------------------------------------

    @staticmethod
    def normalize_symbol(symbol):

        if not symbol:
            return ""

        symbol = str(symbol).strip()

        replacements = {

            "ي": "ی",
            "ى": "ی",
            "ئ": "ی",

            "ك": "ک",

            "ة": "ه",
            "ۀ": "ه",

            "ؤ": "و",

            "\u200c": "",
            "\u200f": "",
            "\u200e": "",

        }

        for old, new in replacements.items():

            symbol = symbol.replace(old, new)

        return symbol

    # -------------------------------------
    # Save
    # -------------------------------------

    def save(
        self,
        symbol,
        company,
        isin,
        company_isin,
        inscode,
        market,
        board,
        instrument_type,
        sector_code,
        sector_name,
        sub_sector
    ):

        if not symbol:

            return False

        symbol = self.normalize_symbol(symbol)

        self.db.connect()

        sql = """

        INSERT OR REPLACE INTO symbols(

            symbol,
            company,
            isin,
            company_isin,
            inscode,
            market,
            board,
            instrument_type,
            sector_code,
            sector_name,
            sub_sector

        )

        VALUES(?,?,?,?,?,?,?,?,?,?,?)

        """

        self.db.cursor.execute(

            sql,

            (

                symbol,
                company,
                isin,
                company_isin,
                inscode,
                market,
                board,
                instrument_type,
                sector_code,
                sector_name,
                sub_sector

            )

        )

        self.db.connection.commit()

        self.db.close()

        return True

    # -------------------------------------
    # Get InsCode
    # -------------------------------------

    def get_inscode(self, symbol):

        normalized = self.normalize_symbol(symbol)

        self.db.connect()

        self.db.cursor.execute(
            """
            SELECT symbol, inscode
            FROM symbols
            """
        )

        rows = self.db.cursor.fetchall()

        self.db.close()

        matches = []

        for db_symbol, inscode in rows:

            if not db_symbol or not inscode:
                continue

            if self.normalize_symbol(db_symbol) == normalized:
                matches.append(
                    (db_symbol, inscode)
                )

        if len(matches) == 1:
            return matches[0][1]

        if len(matches) > 1:

            print("Multiple InsCodes Found:", symbol)
            print(matches)

        return None    
        # ---------------------------------
        # Exact / normalized search
        # ---------------------------------

        self.db.cursor.execute(

            """
            SELECT symbol, inscode
            FROM symbols
            """

        )

        rows = self.db.cursor.fetchall()

        matches = []

        for db_symbol, inscode in rows:

            if not db_symbol or not inscode:

                continue

            db_normalized = self.normalize_symbol(db_symbol)

            if db_normalized == normalized:

                matches.append(
                    (db_symbol, inscode)
                )

        self.db.close()

        # فقط یک نتیجه مطمئن
        if len(matches) == 1:

            return matches[0][1]

        return None

    # -------------------------------------
    # Get All
    # -------------------------------------

    def get_all(self):

        self.db.connect()

        self.db.cursor.execute(
            "SELECT * FROM symbols"
        )

        rows = self.db.cursor.fetchall()

        self.db.close()

        return rows

    # -------------------------------------
    # Find Exact Symbol
    # -------------------------------------

    def find_symbol(self, symbol):

        normalized = self.normalize_symbol(symbol)

        self.db.connect()

        self.db.cursor.execute(

            """
            SELECT *
            FROM symbols
            """

        )

        rows = self.db.cursor.fetchall()

        self.db.close()

        for row in rows:

            db_symbol = row[1]

            if self.normalize_symbol(db_symbol) == normalized:

                return row

        return None

    # -------------------------------------
    # Find Similar Symbols
    # -------------------------------------

    def find_like(self, text):

        normalized = self.normalize_symbol(text)

        self.db.connect()

        self.db.cursor.execute(

            """
            SELECT *
            FROM symbols
            WHERE symbol LIKE ?
            LIMIT 20
            """,

            (f"%{normalized}%",)

        )

        rows = self.db.cursor.fetchall()

        self.db.close()

        return rows

    # -------------------------------------
    # Exists
    # -------------------------------------

    def exists(self, symbol):

        return self.find_symbol(symbol) is not None

    # -------------------------------------
    # Count
    # -------------------------------------

    def count(self):

        self.db.connect()

        self.db.cursor.execute(
            "SELECT COUNT(*) FROM symbols"
        )

        count = self.db.cursor.fetchone()[0]

        self.db.close()

        return count

    # -------------------------------------
    # Clear
    # -------------------------------------

    def clear(self):

        self.db.connect()

        self.db.cursor.execute(
            "DELETE FROM symbols"
        )

        self.db.connection.commit()

        self.db.close()

