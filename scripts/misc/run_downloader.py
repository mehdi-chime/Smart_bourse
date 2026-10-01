from market_downloader import MarketDownloader

if __name__ == "__main__":
    print("🚀 شروع دانلود داده‌های بازار...")
    downloader = MarketDownloader()
    if downloader.download():
        downloader.save_json()
        downloader.show()
        print("✅ دانلود و ذخیره با موفقیت انجام شد.")
    else:
        print("❌ خطا در دانلود داده‌ها.")
