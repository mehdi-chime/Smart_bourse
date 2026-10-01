"""
Tests for AI modules
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_import_memory():
    from ai.memory import AIMemory
    assert AIMemory is not None


def test_import_learner():
    from ai.learner import AILearner
    assert AILearner is not None


def test_import_ai_engine():
    from ai.ai_engine import AIEngine
    assert AIEngine is not None


def test_learner_weights():
    from ai.learner import AILearner
    learner = AILearner()
    assert "money_flow" in learner.weights
    assert "technical" in learner.weights
    assert "context" in learner.weights


def test_learner_adjust():
    from ai.learner import AILearner
    learner = AILearner()
    
    outcomes = [
        {"category": "SAFE_BUY", "success": True} for _ in range(8)
    ] + [
        {"category": "SAFE_BUY", "success": False} for _ in range(2)
    ]
    
    new_weights = learner.adjust_weights(outcomes)
    assert sum(new_weights.values()) > 0.99
    assert sum(new_weights.values()) < 1.01


def test_ai_engine_advise():
    from ai.ai_engine import AIEngine
    engine = AIEngine()
    
    result = engine.advise(
        symbol="خگستر",
        category="SAFE_BUY",
        ratio=5.0,
        rsi=25,
        technical_score=70,
        market_change_pct=1.5,
        last_price=10000,
    )
    
    assert "final_score" in result
    assert "advice" in result
    assert "confidence" in result
    assert result["final_score"] >= 0


def test_memory_save_load():
    from ai.memory import AIMemory
    memory = AIMemory()
    
    stats = memory.stats()
    assert "total_signals" in stats
    assert "total_outcomes" in stats
    assert "pending" in stats


def test_ml_model_exists():
    from ai.ml_model import MLModel
    model = MLModel()
    assert model.has_sklearn
