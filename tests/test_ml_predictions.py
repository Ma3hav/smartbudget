# tests/test_ml_predictions.py
import pytest
from statistics import mean


def heuristic_predict_last5_avg(history):
    """
    Replicates the ml_routes logic: take last up to 5 entries and return average amount.
    The route uses float(...) on amounts, and returns round(avg,2).
    """
    if not isinstance(history, list) or len(history) == 0:
        raise ValueError("history must be a non-empty list")

    last = history[-5:]
    amounts = [float(item.get("amount", 0)) for item in last]
    avg = mean(amounts)
    return round(avg, 2)


def test_predict_with_less_than_five_transactions():
    history = [
        {"amount": 10},
        {"amount": 20},
        {"amount": 30}
    ]
    pred = heuristic_predict_last5_avg(history)
    assert pred == round((10 + 20 + 30) / 3, 2)


def test_predict_with_more_than_five_transactions():
    history = [
        {"amount": 5},
        {"amount": 7},
        {"amount": 9},
        {"amount": 11},
        {"amount": 13},
        {"amount": 100}  # only last 5 should be considered (7..100)
    ]
    # last 5: 7,9,11,13,100 -> avg = (7+9+11+13+100)/5
    expected = round((7 + 9 + 11 + 13 + 100) / 5, 2)
    pred = heuristic_predict_last5_avg(history)
    assert pred == expected


def test_predict_raises_on_invalid_history():
    with pytest.raises(ValueError):
        heuristic_predict_last5_avg([])
    with pytest.raises(ValueError):
        heuristic_predict_last5_avg("not-a-list")
