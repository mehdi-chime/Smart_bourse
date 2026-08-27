"""
Project : Smart_Bourse

File : run.py

Version : 7.0.0

Description :
Main Entry Point
"""

from datetime import datetime

from utils.logger import Logger

from database.database import Database

from models.stock import Stock

from market.market_manager import MarketManager
from market.symbol_downloader import SymbolDownloader
from market_downloader import MarketDownloader

from history.history_manager import HistoryManager
from history.history_downloader import HistoryDownloader
from history.history_database import HistoryDatabase

from analysis import Analyzer

from indicators.indicator_manager import IndicatorManager

from strategy.strategy_manager import StrategyManager

from ai.ai_engine import AIEngine

from portfolio.portfolio import Portfolio

from paper.paper_trading import PaperTrading

from backtest.backtest_engine import BackTestEngine


# =====================================================
# MAIN
# =====================================================

def main():

    # =================================================
    # CREATE OBJECTS
    # =================================================

    log = Logger()

    history_downloader = HistoryDownloader()

    symbol_downloader = SymbolDownloader(
        history_downloader.api
    )

    print()
    print("=" * 70)
    print("FOOLAD DATABASE TEST")
    print("=" * 70)

    print("TOTAL SYMBOLS:", symbol_downloader.repo.count())

    print("FOOLAD:", symbol_downloader.repo.find_symbol("فولاد"))

    print("FOOLAD INSCODE:",
          symbol_downloader.repo.get_inscode("فولاد"))

    print("FOOLAD LIKE:",
          symbol_downloader.repo.find_like("فول"))

    print("=" * 70)    

    downloader = MarketDownloader()

    history = HistoryManager()

    db = Database()

    history_db = HistoryDatabase()

    analyzer = Analyzer()

    indicators = IndicatorManager()

    strategy = StrategyManager()

    ai = AIEngine()

    market = MarketManager()

    portfolio = Portfolio()

    paper = PaperTrading()

    backtest = BackTestEngine()


    # =================================================
    # START
    # =================================================

    log.write("=" * 60)

    log.write(
        "Smart_Bourse Started"
    )

    log.write(
        f"Start Time : {datetime.now()}"
    )

    log.write("=" * 60)


    # =================================================
    # STEP 1
    # DOWNLOAD SYMBOLS
    # =================================================

    log.write(
        "Loading Symbol Downloader"
    )

    print()
    print("=" * 70)
    print("STEP 1 : SYMBOL DOWNLOADER")
    print("=" * 70)

    symbol_downloader.download()

    print()
    print("=" * 70)
    print("SYMBOL DATABASE CHECK")
    print("=" * 70)

    total_symbols = (
        symbol_downloader.repo.count()
    )

    print(
        "TOTAL SYMBOLS IN DATABASE:",
        total_symbols
    )

    print()

    print(
        "FOOLAD:",
        symbol_downloader.repo.find_symbol(
            "فولاد"
        )
    )

    print(
        "FEMELI:",
        symbol_downloader.repo.find_symbol(
            "فملی"
        )
    )

    print(
        "KHODRO:",
        symbol_downloader.repo.find_symbol(
            "خودرو"
        )
    )

    print()

    print(
        "FOOLAD INSCODE:",
        symbol_downloader.repo.get_inscode(
            "فولاد"
        )
    )

    print(
        "FEMELI INSCODE:",
        symbol_downloader.repo.get_inscode(
            "فملی"
        )
    )

    print(
        "KHODRO INSCODE:",
        symbol_downloader.repo.get_inscode(
            "خودرو"
        )
    )

    print("=" * 70)


    # =================================================
    # STEP 2
    # DOWNLOAD TODAY MARKET
    # =================================================

    log.write(
        "Loading Downloader"
    )

    print()
    print("=" * 70)
    print("STEP 2 : MARKET DOWNLOADER")
    print("=" * 70)

    downloader.download()

    print()

    print(
        "Downloaded Records:",
        len(downloader.market_data)
    )

    if not downloader.market_data:

        print(
            "No Market Data Downloaded"
        )

        print(
            "Smart_Bourse stopped."
        )

        return


    # =================================================
    # SAVE MARKET JSON
    # =================================================

    downloader.save_json()

    downloader.load_json()

    downloader.show()


    # =================================================
    # STEP 3
    # SAVE TODAY HISTORY
    # =================================================

    log.write(
        "Loading History Manager"
    )

    print()
    print("=" * 70)
    print("STEP 3 : HISTORY MANAGER")
    print("=" * 70)

    history.save_daily_history(
        downloader.json_file
    )

    history.show_history_files()


    # =================================================
    # STEP 4
    # SAVE TODAY MARKET DATABASE
    # =================================================

    log.write(
        "Loading Database"
    )

    print()
    print("=" * 70)
    print("STEP 4 : MARKET DATABASE")
    print("=" * 70)

    db.connect()

    db.create_tables()

    today = (
        downloader.market_data[0]["trade_date"]
    )

    db.delete_by_date(
        today
    )

    for item in downloader.market_data:

        stock = Stock()

        stock.symbol = item["symbol"]

        stock.trade_date = item["trade_date"]

        stock.open_price = item["open_price"]

        stock.high_price = item["high_price"]

        stock.low_price = item["low_price"]

        stock.close_price = item["close_price"]

        stock.volume = item["volume"]

        db.insert_stock(
            stock
        )

    db.close()


    # =================================================
    # STEP 5
    # DOWNLOAD HISTORY
    # =================================================

    log.write(
        "Loading History Downloader"
    )

    print()
    print("=" * 70)
    print("STEP 5 : HISTORY DOWNLOADER")
    print("=" * 70)

    if history_downloader.connect():

        for item in downloader.market_data:

            symbol = item["symbol"]

            print()
            print(
                "Selected Symbol :",
                symbol
            )

            history_downloader.select_symbol(
                symbol
            )

            if history_downloader.download(
                365
            ):

                history_downloader.save_to_database()

                history_downloader.save_json()

            else:

                print(
                    "History Download Failed :",
                    symbol
                )

        history_downloader.disconnect()

    else:

        log.write(
            "History Downloader Connection Failed"
        )


    # =================================================
    # STEP 6
    # MARKET MANAGER
    # =================================================

    log.write(
        "Loading Market Manager"
    )

    print()
    print("=" * 70)
    print("STEP 6 : MARKET MANAGER")
    print("=" * 70)

    market.show()

    market.run(
        downloader.json_file
    )


    # =================================================
    # STEP 7
    # SECTOR MANAGER TEST
    # =================================================

    print()
    print("=" * 70)
    print("STEP 7 : SECTOR MANAGER TEST")
    print("=" * 70)

    from market.sector_manager import SectorManager

    sector_manager = SectorManager()

    sector_manager.show()

    print()

    print(
        "Foolad Sector:",
        sector_manager.find_sector(
            "فولاد"
        )
    )

    print(
        "Femeli Sector:",
        sector_manager.find_sector(
            "فملی"
        )
    )

    print(
        "Khodro Sector:",
        sector_manager.find_sector(
            "خودرو"
        )
    )

    print("=" * 70)


    # =================================================
    # STEP 8
    # SYMBOL DATABASE REPORT
    # =================================================

    print()
    print("=" * 70)
    print("STEP 8 : SYMBOL DATABASE REPORT")
    print("=" * 70)

    print(
        "TOTAL SYMBOLS:",
        symbol_downloader.repo.count()
    )

    print()

    print(
        "FOOLAD:",
        symbol_downloader.repo.find_symbol(
            "فولاد"
        )
    )

    print(
        "FEMELI:",
        symbol_downloader.repo.find_symbol(
            "فملی"
        )
    )

    print(
        "KHODRO:",
        symbol_downloader.repo.find_symbol(
            "خودرو"
        )
    )

    print()

    print(
        "FEMELI BY LIKE:",
        symbol_downloader.repo.find_like(
            "فمل"
        )
    )

    print(
        "KHODRO BY LIKE:",
        symbol_downloader.repo.find_like(
            "خودرو"
        )
    )

    print()

    print(
        "FOOLAD INSCODE:",
        symbol_downloader.repo.get_inscode(
            "فولاد"
        )
    )

    print(
        "FEMELI INSCODE:",
        symbol_downloader.repo.get_inscode(
            "فملی"
        )
    )

    print(
        "KHODRO INSCODE:",
        symbol_downloader.repo.get_inscode(
            "خودرو"
        )
    )

    print("=" * 70)


    # =================================================
    # STEP 9
    # LOAD SYMBOLS
    # =================================================

    print()
    print("=" * 70)
    print("STEP 9 : LOAD SYMBOLS")
    print("=" * 70)

    symbols = [
        item["symbol"]
        for item in downloader.market_data
    ]

    print(
        "DEBUG SYMBOLS =",
        symbols
    )

    print(
        "COUNT =",
        len(symbols)
    )


    # =================================================
    # STEP 10
    # ANALYZE EVERY SYMBOL
    # =================================================

    print()
    print("=" * 70)
    print("STEP 10 : ANALYSIS")
    print("=" * 70)

    for symbol in symbols:

        print()
        print("=" * 80)
        print(
            "ANALYZING :",
            symbol
        )
        print("=" * 80)

        history_db.connect()

        stocks = history_db.get_history(
            symbol,
            365
        )

        history_db.close()

        print(
            "History Records:",
            len(stocks)
        )

        if len(stocks) < 60:

            print(
                "Not Enough History"
            )

            continue


        # ---------------------------------------------
        # ANALYZER
        # ---------------------------------------------

        log.write(
            f"Analyzer : {symbol}"
        )

        analyzer.analyze(
            stocks
        )

        analyzer.show()


        # ---------------------------------------------
        # INDICATORS
        # ---------------------------------------------

        indicator_result = indicators.run(
            stocks
        )

        print()
        print("=" * 80)
        print(
            "Technical Indicators"
        )
        print("=" * 80)

        for name, value in indicator_result.items():

            print(
                f"{name:<20} : {value}"
            )

        print("=" * 80)


        # ---------------------------------------------
        # STRATEGY
        # ---------------------------------------------

        signal = strategy.generate(
            indicator_result
        )

        print()
        print("=" * 60)
        print(
            "STRATEGY SIGNAL"
        )
        print("=" * 60)

        print(
            signal
        )

        print("=" * 60)


        # ---------------------------------------------
        # AI
        # ---------------------------------------------

        ai.show(

            signal["signal"],

            signal["risk"],

            signal["score"]

        )


        # ---------------------------------------------
        # BACKTEST
        # ---------------------------------------------

        backtest.run(
            stocks
        )


        # ---------------------------------------------
        # PAPER TRADING
        # ---------------------------------------------

        if signal["signal"] == "BUY":

            paper.buy(

                stocks[0].symbol,

                stocks[0].close_price,

                100

            )

            portfolio.buy(

                stocks[0].symbol,

                stocks[0].close_price,

                100

            )

        elif signal["signal"] == "SELL":

            paper.sell(

                stocks[-1].symbol,

                stocks[-1].close_price

            )

            portfolio.sell(

                stocks[-1].symbol,

                100

            )


    # =================================================
    # FINAL REPORT
    # =================================================

    print()
    print("=" * 80)
    print("FINAL REPORT")
    print("=" * 80)

    portfolio.show()

    print()

    paper.show()

    print()

    paper.show_history()

    log.write(
        "=" * 60
    )

    log.write(
        "System Ready"
    )

    log.write(
        "=" * 60
    )


# =====================================================
# ENTRY POINT
# =====================================================

if __name__ == "__main__":

    main()
