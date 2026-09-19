
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))


def banner(text):
    print()
    print("=" * 75)
    print("  " + text)
    print("=" * 75)


def main():
    print()
    print("=" * 75)
    print("     Smart_Bourse - Full Run")
    print("=" * 75)

    # 1. بافت بازار
    banner("1/9 - Market Context")
    try:
        from scanner.market_context import MarketContext
        mc = MarketContext()
        mc.fetch_all()
        mc.report()
        mc.save()
    except Exception as e:
        print("   error: " + str(e)[:80])

    # 2. پرتفوی زنده
    banner("2/9 - Live Portfolio")
    try:
        import subprocess
        subprocess.run([sys.executable, str(PROJECT_ROOT / "scanner" / "live_portfolio.py")])
    except Exception as e:
        print("   error: " + str(e)[:80])

    # 3. ذخیره‌ی پرتفوی در تاریخچه
    banner("3/9 - Save Portfolio Snapshot")
    try:
        import subprocess
        subprocess.run([sys.executable, str(PROJECT_ROOT / "scanner" / "portfolio_tracker.py")])
    except Exception as e:
        print("   error: " + str(e)[:80])

    # 4. فیلتر جریان پول
    banner("4/9 - Real Flow Filter")
    try:
        from scanner.real_flow_filter import RealFlowFilter
        f = RealFlowFilter()
        f.run()
    except Exception as e:
        print("   error: " + str(e)[:80])

    # 5. تحلیل تکنیکال
    banner("5/9 - Technical Analysis")
    try:
        from scanner.technical_analyzer import TechnicalAnalyzer
        t = TechnicalAnalyzer()
        analysis = t.analyze_all()
        if analysis:
            t.print_top(analysis, top_n=15)
            t.save(analysis)
    except Exception as e:
        print("   error: " + str(e)[:80])

    # 6. مشاور AI
    banner("6/9 - AI Advisor")
    try:
        from scanner.ai_advisor import AIAdvisor
        advisor = AIAdvisor()
        advisor.run()
    except Exception as e:
        print("   error: " + str(e)[:80])

    # 7. داشبورد HTML
    banner("7/9 - HTML Dashboard")
    try:
        from scanner.dashboard_builder import DashboardBuilder
        d = DashboardBuilder()
        html_file = d.build()
        if html_file:
            print()
            print("   Dashboard: " + str(html_file))
    except Exception as e:
        print("   error: " + str(e)[:80])

    # 8. ژورنال پرتفوی
    banner("8/9 - Portfolio Journal")
    try:
        from portfolio.journal import TradeJournal
        journal = TradeJournal()
        journal.report()
        journal.show_open()
    except Exception as e:
        print("   error: " + str(e)[:80])

    # 9. گزارش پرتفوی HTML
    banner("9/9 - Portfolio HTML Report")
    try:
        from scanner.portfolio_report import PortfolioReport
        r = PortfolioReport()
        portfolio_file = r.build()
    except Exception as e:
        print("   error: " + str(e)[:80])

    # پایان
    banner("DONE - Smart_Bourse Complete")
    print()
    print("  Files created:")
    print("     - Market context:  data\\market_context\\")
    print("     - Live records:    data\\live_records\\")
    print("     - Portfolio:       data\\portfolio_history\\")
    print("     - Real flow:       data\\real_flow\\")
    print("     - HTML dashboard:  reports\\")
    print()
    print("  Open reports folder:")
    print('     start "" "reports"')
    print()


if __name__ == "__main__":
    main()
