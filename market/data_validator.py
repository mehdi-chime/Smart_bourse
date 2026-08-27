"""
Project : Smart_Bourse

File : data_validator.py

Version : 2.0.0

Author :
Mehdi Jalali
ChatGPT

Description :
Professional Market Data Validator
"""


from datetime import datetime


class DataValidator:

    def __init__(self):

        self.required_fields = [

            "symbol",
            "trade_date",
            "open_price",
            "high_price",
            "low_price",
            "close_price",
            "volume"

        ]

        self.errors = []

    # --------------------------------------------------

    def add_error(self, symbol, message):

        self.errors.append({
            "symbol": symbol,
            "error": message
        })

    # --------------------------------------------------

    def has_required_fields(self, data):

        for field in self.required_fields:

            if field not in data:

                self.add_error(
                    data.get("symbol", "Unknown"),
                    f"Missing Field : {field}"
                )

                return False

        return True

    # --------------------------------------------------

    def validate_symbol(self, data):

        symbol = str(data["symbol"]).strip()

        if symbol == "":

            self.add_error(symbol, "Empty Symbol")

            return False

        return True

    # --------------------------------------------------

    def validate_date(self, data):

        try:

            datetime.strptime(str(data["trade_date"]), "%Y-%m-%d")

            return True

        except:

            self.add_error(data["symbol"], "Invalid Date")

            return False

    # --------------------------------------------------

    def validate_prices(self, data):

        try:

            open_price = float(data["open_price"])
            high_price = float(data["high_price"])
            low_price = float(data["low_price"])
            close_price = float(data["close_price"])
            volume = int(data["volume"])

        except:

            self.add_error(data["symbol"], "Invalid Data Type")

            return False

        if open_price <= 0:

            self.add_error(data["symbol"], "Open Price <= 0")

            return False

        if close_price <= 0:

            self.add_error(data["symbol"], "Close Price <= 0")

            return False

        if high_price <= 0:

            self.add_error(data["symbol"], "High Price <= 0")

            return False

        if low_price <= 0:

            self.add_error(data["symbol"], "Low Price <= 0")

            return False

        if volume <= 0:

            self.add_error(data["symbol"], "Volume <= 0")

            return False

        if high_price < low_price:

            self.add_error(data["symbol"], "High < Low")

            return False

        if open_price > high_price:

            self.add_error(data["symbol"], "Open > High")

            return False

        if open_price < low_price:

            self.add_error(data["symbol"], "Open < Low")

            return False

        if close_price > high_price:

            self.add_error(data["symbol"], "Close > High")

            return False

        if close_price < low_price:

            self.add_error(data["symbol"], "Close < Low")

            return False

        return True

    # --------------------------------------------------

    def validate(self, data):

        if not self.has_required_fields(data):
            return False

        if not self.validate_symbol(data):
            return False

        if not self.validate_date(data):
            return False

        if not self.validate_prices(data):
            return False

        return True

    # --------------------------------------------------

    def validate_list(self, market_data):

        self.errors = []

        valid_data = []

        invalid_data = []

        for item in market_data:

            if self.validate(item):

                valid_data.append(item)

            else:

                invalid_data.append(item)

        return valid_data, invalid_data

    # --------------------------------------------------

    def show_report(self, valid_data, invalid_data):

        print()

        print("=" * 70)
        print("DATA VALIDATION REPORT")
        print("=" * 70)

        print("Valid Records   :", len(valid_data))
        print("Invalid Records :", len(invalid_data))

        if self.errors:

            print()

            print("Errors:")

            for error in self.errors:

                print(f"{error['symbol']} --> {error['error']}")

        print("=" * 70)
