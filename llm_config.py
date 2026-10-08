# config/llm_config.py
# تنظیمات LLM — نسخه ۲
# اجرا: python config/llm_config.py

import os
from pathlib import Path

# ═══════════════════════════════════════════════════════════
# LLM Keys
# ═══════════════════════════════════════════════════════════

# Groq (رایگان - اولویت اول)
GROQ_API_KEY = "gsk_XXX"  # ← کلید Groq

# DeepSeek (پول - اولویت دوم)
DEEPSEEK_API_KEY = "sk-XXX"  # ← کلید DeepSeek

# ═══════════════════════════════════════════════════════════
# LLM Mode
# ═══════════════════════════════════════════════════════════

# auto: اول Groq، بعد DeepSeek، بعد Fallback
# groq: فقط Groq
# deepseek: فقط DeepSeek
# fallback: فقط Fallback
LLM_MODE = "auto"

# ═══════════════════════════════════════════════════════════
# Groq Settings
# ═══════════════════════════════════════════════════════════

GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

# ═══════════════════════════════════════════════════════════
# DeepSeek Settings
# ═══════════════════════════════════════════════════════════

DEEPSEEK_MODEL = "deepseek-chat"
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

# ═══════════════════════════════════════════════════════════
# Timeouts
# ═══════════════════════════════════════════════════════════

TIMEOUT = 30
MAX_TOKENS = 500


if __name__ == "__main__":
    print("Groq:", GROQ_API_KEY[:20] + "..." if GROQ_API_KEY else "❌")
    print("DeepSeek:", DEEPSEEK_API_KEY[:20] + "..." if DEEPSEEK_API_KEY else "❌")
    print("Mode:", LLM_MODE)
