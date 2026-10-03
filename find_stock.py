def find_stock(stock_info, df_live):
    for _, row in df_live.iterrows():
        live_ins = str(row.get("InsCode") or row.get("insCode") or "")
        live_symbol = str(row.get("Symbol", ""))
        
        # چک INS Code (دقیق‌ترین)
        if stock_info.get("ins_code") and live_ins == stock_info["ins_code"]:
            return row
        
        # چک alias
        for alias in stock_info["aliases"]:
            if normalize(alias) == normalize(live_symbol):
                return row
    
    return None
