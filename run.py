"""
Project : Smart_Bourse
File : run.py
Version : 9.0.0
Description : Main Entry Point with Full History Download
"""

from datetime import datetime
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from core.logger import Logger
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

# ========== تنظیمات ==========
MAX_WORKERS = 10  # تعداد نخ‌های همزمان برای دانلود تاریخچه

# =====================================================
# MAIN
# =====================================================

def main():

    # ========== مقداردهی لاگر ==========
    log = Logger()
    log.log("=" * 70, to_console=True)
    log.log("🚀 Smart_Bourse Started", to_console=True)
    log.log(f"⏱  Start Time : {datetime.now()}", to_console=True)
    log.log("=" * 70, to_console=True)

    # ========== ایجاد اشیا ==========
    history_downloader = HistoryDownloader()
    symbol_downloader = SymbolDownloader(history_downloader.api)
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

    # =============================================
    # STEP 1 : DOWNLOAD SYMBOLS
    # =============================================
    log.log("", to_console=True)
    log.log("=" * 70, to_console=True)
    log.log("📥 STEP 1 : SYMBOL DOWNLOADER", to_console=True)
    log.log("=" * 70, to_console=True)

    try:
        symbol_downloader.download()
        total_symbols = symbol_downloader.repo.count()
        log.log(f"✅ TOTAL SYMBOLS: {total_symbols}", to_console=True)
    except Exception as e:
        log.log(f"❌ ERROR downloading symbols: {e}", to_console=True)
        return

    # =============================================
    # STEP 2 : DOWNLOAD TODAY MARKET
    # =============================================
    log.log("", to_console=True)
    log.log("=" * 70, to_console=True)
    log.log("📥 STEP 2 : MARKET DOWNLOADER", to_console=True)
    log.log("=" * 70, to_console=True)

    try:
        downloader.download()
        market_data_len = len(downloader.market_data)
        log.log(f"✅ RECORDS DOWNLOADED: {market_data_len}", to_console=True)

        if market_data_len == 0:
            log.log("❌ No market data available - stopping.", to_console=True)
            return

        symbols = [item["symbol"] for item in downloader.market_data]
        log.log(f"📊 SYMBOLS: {', '.join(symbols)}", to_console=True)

        downloader.save_json()
        downloader.load_json()
        sample = downloader.market_data[0] if downloader.market_data else {}
        log.log(f"📌 Sample record: {sample}", to_console=False)
    except Exception as e:
        log.log(f"❌ ERROR downloading market data: {e}", to_console=True)
        return

    # =============================================
    # STEP 3 : SAVE TODAY HISTORY
    # =============================================
    log.log("", to_console=True)
    log.log("=" * 70, to_console=True)
    log.log("💾 STEP 3 : HISTORY MANAGER", to_console=True)
    log.log("=" * 70, to_console=True)

    try:
        history.save_daily_history(downloader.json_file)
        history.show_history_files()
        log.log("✅ History saved.", to_console=True)
    except Exception as e:
        log.log(f"❌ ERROR saving history: {e}", to_console=True)

    # =============================================
    # STEP 4 : SAVE TODAY MARKET DATABASE
    # =============================================
    log.log("", to_console=True)
    log.log("=" * 70, to_console=True)
    log.log("💾 STEP 4 : MARKET DATABASE", to_console=True)
    log.log("=" * 70, to_console=True)

    try:
        db.connect()
        db.create_tables()
        today = downloader.market_data[0]["trade_date"]
        db.delete_by_date(today)
        for item in downloader.market_data:
            stock = Stock()
            stock.symbol = item["symbol"]
            stock.trade_date = item["trade_date"]
            stock.open_price = item["open_price"]
            stock.high_price = item["high_price"]
            stock.low_price = item["low_price"]
            stock.close_price = item["close_price"]
            stock.volume = item["volume"]
            db.insert_stock(stock)
        db.close()
        log.log("✅ Database updated.", to_console=True)
    except Exception as e:
        log.log(f"❌ ERROR updating database: {e}", to_console=True)

    # =============================================
    # STEP 5 : DOWNLOAD HISTORY FOR ALL SYMBOLS (NEW)
    # =============================================
    log.log("", to_console=True)
    log.log("=" * 70, to_console=True)
    log.log("📥 STEP 5 : HISTORY DOWNLOADER (ALL SYMBOLS)", to_console=True)
    log.log("=" * 70, to_console=True)

    try:
        # دریافت همه نمادها از دیتابیس
        db = Database()
        db.connect()
        all_symbols = db.get_all_symbols()
        db.close()
        log.log(f"📊 TOTAL SYMBOLS TO DOWNLOAD: {len(all_symbols)}", to_console=True)

        if history_downloader.connect():
            total = len(all_symbols)
            completed = 0

            # تابع دانلود برای هر سهم
            def download_symbol(symbol_row):
                symbol_name = symbol_row[1]
                if symbol_name.startswith('ح.'):
                    return None
                try:
                    history_downloader.select_symbol(symbol_name)
                    if history_downloader.download(365):
                        history_downloader.save_to_database()
                        history_downloader.save_json()
                        return symbol_name
                except Exception as e:
                    return None
                return None

            # دانلود همزمان با ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futures = {executor.submit(download_symbol, s): s for s in all_symbols}
                
                for future in as_completed(futures):
                    completed += 1
                    if completed % 50 == 0:
                        log.log(f"   دانلود {completed}/{total} ...", to_console=True)
                    
                    result = future.result()
                    if result:
                        log.log(f"✅ تاریخچه {result} دانلود شد.", to_console=False)

            history_downloader.disconnect()
            log.log(f"✅ دانلود تاریخچه {completed} سهم کامل شد.", to_console=True)
        else:
            log.log("❌ History Downloader Connection Failed", to_console=True)

    except Exception as e:
        log.log(f"❌ ERROR in history download: {e}", to_console=True)

    # =============================================
    # STEP 6 : MARKET MANAGER
    # =============================================
    log.log("", to_console=True)
    log.log("=" * 70, to_console=True)
    log.log("📈 STEP 6 : MARKET MANAGER", to_console=True)
    log.log("=" * 70, to_console=True)

    try:
        market.show()
        market.run(downloader.json_file)
        log.log("✅ Market manager executed.", to_console=True)
    except Exception as e:
        log.log(f"❌ ERROR in market manager: {e}", to_console=True)

    # =============================================
    # STEP 7 : SECTOR MANAGER TEST
    # =============================================
    log.log("", to_console=True)
    log.log("=" * 70, to_console=True)
    log.log("📊 STEP 7 : SECTOR MANAGER", to_console=True)
    log.log("=" * 70, to_console=True)

    try:
        from market.sector_manager import SectorManager
        sector_manager = SectorManager()
        for sym in ["فولاد", "فملی", "خودرو"]:
            sector = sector_manager.find_sector(sym)
            log.log(f"🔹 {sym} → {sector}", to_console=True)
    except Exception as e:
        log.log(f"❌ ERROR in sector manager: {e}", to_console=True)

    # =============================================
    # STEP 8 : SYMBOL DATABASE REPORT
    # =============================================
    log.log("", to_console=True)
    log.log("=" * 70, to_console=True)
    log.log("📋 STEP 8 : SYMBOL DATABASE REPORT", to_console=True)
    log.log("=" * 70, to_console=True)

    try:
        total_symbols = symbol_downloader.repo.count()
        log.log(f"✅ TOTAL SYMBOLS IN DB: {total_symbols}", to_console=True)
    except Exception as e:
        log.log(f"❌ ERROR: {e}", to_console=True)

    # =============================================
    # STEP 9 : LOAD SYMBOLS FOR ANALYSIS
    # =============================================
    symbols = [item["symbol"] for item in downloader.market_data]
    log.log("", to_console=True)
    log.log("=" * 70, to_console=True)
    log.log("🔍 STEP 9 : LOAD SYMBOLS", to_console=True)
    log.log("=" * 70, to_console=True)
    log.log(f"📊 SYMBOLS TO ANALYZE: {', '.join(symbols)}", to_console=True)

    # =============================================
    # STEP 10 : FULL ANALYSIS FOR EACH SYMBOL
    # =============================================
    log.log("", to_console=True)
    log.log("=" * 70, to_console=True)
    log.log("📈 STEP 10 : ANALYSIS", to_console=True)
    log.log("=" * 70, to_console=True)

    for symbol in symbols:
        try:
            log.log("", to_console=True)
            log.log("=" * 80, to_console=True)
            log.log(f"🔍 ANALYZING : {symbol}", to_console=True)
            log.log("=" * 80, to_console=True)

            history_db.connect()
            stocks = history_db.get_history(symbol, 365)
            history_db.close()

            log.log(f"📊 History Records: {len(stocks)}", to_console=True)

            if len(stocks) < 60:
                log.log("⚠️ Not enough history data.", to_console=True)
                continue

            # Analysis
            analyzer.analyze(stocks)
            analyzer.show()

            # Indicators
            indicator_result = indicators.run(stocks)
            log.log("📊 Technical Indicators:", to_console=True)
            for name, value in indicator_result.items():
                log.log(f"   {name:<20} : {value}", to_console=True)

            # Strategy
            signal = strategy.generate(indicator_result)
            log.log(f"📈 Strategy Signal: {signal}", to_console=True)

            # AI
            ai.show(signal["signal"], signal["risk"], signal["score"])

            # Backtest
            backtest.run(stocks)

            # Paper Trading
            if signal["signal"] == "BUY":
                paper.buy(stocks[0].symbol, stocks[0].close_price, 100)
                portfolio.buy(stocks[0].symbol, stocks[0].close_price, 100)
            elif signal["signal"] == "SELL":
                paper.sell(stocks[-1].symbol, stocks[-1].close_price)
                portfolio.sell(stocks[-1].symbol, 100)

        except Exception as e:
            log.log(f"❌ Error analyzing {symbol}: {e}", to_console=True)

    # =============================================
    # FINAL REPORT
    # =============================================
    log.log("", to_console=True)
    log.log("=" * 80, to_console=True)
    log.log("📊 FINAL REPORT", to_console=True)
    log.log("=" * 80, to_console=True)

    try:
        portfolio.show()
        paper.show()
        paper.show_history()
    except Exception as e:
        log.log(f"❌ Error in final report: {e}", to_console=True)

    log.log("", to_console=True)
    log.log("=" * 70, to_console=True)
    log.log("✅ System Ready", to_console=True)
    log.log("=" * 70, to_console=True)
    log.log(f"📁 Full log saved to: {log.log_file}", to_console=True)


# =====================================================
# ENTRY POINT
# =====================================================

if __name__ == "__main__":
    main()
