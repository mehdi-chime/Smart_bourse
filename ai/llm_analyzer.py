# ai/llm_analyzer.py
# تحلیل‌گر LLM — نسخه ۳
# اجرا: python ai/llm_analyzer.py

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime

if os.name == 'nt':
    os.system('chcp 65001 >nul 2>&1')

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
except:
    pass

PROJECT_ROOT = Path(r"F:\python\har roz ba python\smart_bours")
sys.path.insert(0, str(PROJECT_ROOT))


def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode('ascii', errors='ignore').decode('ascii'))


def call_groq(prompt, api_key):
    """ارسال به Groq"""
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500,
        }
        r = requests.post(url, headers=headers, json=data, timeout=30)

        if r.status_code == 200:
            result = r.json()
            return result["choices"][0]["message"]["content"]
        else:
            return None
    except Exception as e:
        safe_print(f"Groq error: {e}")
        return None


def call_deepseek(prompt, api_key):
    """ارسال به DeepSeek"""
    try:
        url = "https://api.deepseek.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500,
        }
        r = requests.post(url, headers=headers, json=data, timeout=30)

        if r.status_code == 200:
            result = r.json()
            return result["choices"][0]["message"]["content"]
        else:
            return None
    except Exception as e:
        safe_print(f"DeepSeek error: {e}")
        return None


def analyze_news(news_text):
    """تحلیل خبر"""
    from config.llm_config import (
        GROQ_API_KEY,
        DEEPSEEK_API_KEY,
        LLM_MODE,
    )

    prompt = f"""تحلیل خبر بورس:
{news_text}

پاسخ JSON:
{{
  "sentiment": "positive/negative/neutral",
  "impact": -10 to +10,
  "symbols": ["..."],
  "advice": "..."
}}
"""

    # Groq
    if LLM_MODE in ["auto", "groq"] and GROQ_API_KEY and not GROQ_API_KEY.startswith("gsk_XXX"):
        result = call_groq(prompt, GROQ_API_KEY)
        if result:
            return {
                "mode": "groq",
                "result": result,
            }

    # DeepSeek
    if LLM_MODE in ["auto", "deepseek"] and DEEPSEEK_API_KEY and not DEEPSEEK_API_KEY.startswith("sk-XXX"):
        result = call_deepseek(prompt, DEEPSEEK_API_KEY)
        if result:
            return {
                "mode": "deepseek",
                "result": result,
            }

    # Fallback
    return {
        "mode": "fallback",
        "result": {
            "sentiment": "neutral",
            "impact": 0,
            "symbols": [],
            "advice": "تحلیل با Fallback",
        }
    }


if __name__ == "__main__":
    result = analyze_news("تست خبر")
    safe_print(json.dumps(result, ensure_ascii=False, indent=2))
