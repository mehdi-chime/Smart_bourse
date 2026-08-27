print("TEST SCENARIO ENGINE")

import sys

sys.path.insert(
    0,
    r"F:\python\har roz ba python\smart_bours"
)

from strategy.scenario_engine import ScenarioEngine


engine = ScenarioEngine()

print("ScenarioEngine imported successfully")
print("ScenarioEngine created successfully")


# ==================================================
# TEST ANALYSIS
# ==================================================

analysis = {

    "signal": "STRONG SELL",

    "trend": "Bearish",

    "trend_strength": "Strong",

    "reversal_risk": "Elevated",

    "RSI": 18,

    "MACD": {
        "Trend": "Bearish"
    },

    "Ichimoku": {
        "Trend": "Bearish"
    },

    "SuperTrend": {
        "Trend": "Sell"
    },

    "ADX": 32,

}


# ==================================================
# GENERATE SCENARIOS
# ==================================================

print()
print("=" * 70)
print("GENERATING SCENARIOS")
print("=" * 70)

scenarios = engine.generate(analysis)


for scenario in scenarios:

    print(
        f"{scenario['name']:<25}"
        f": {scenario['probability']:>6.2f}%"
    )


# ==================================================
# BEST SCENARIO
# ==================================================

print()
print("=" * 70)
print("BEST SCENARIO")
print("=" * 70)

best = engine.best_scenario(analysis)

print("Name        :", best["name"])
print("Probability :", best["probability"], "%")


print()
print("=" * 70)
print("TEST FINISHED")
print("=" * 70)
