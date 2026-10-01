from history.history_downloader import HistoryDownloader

downloader = HistoryDownloader()
if downloader.connect():
    downloader.select_symbol("خگستر")
    if downloader.download(9999):  # همه داده‌ها
        downloader.save_to_database()
        downloader.save_json()
        print("✅ تاریخچه خگستر به‌روز شد.")
    downloader.disconnect()
