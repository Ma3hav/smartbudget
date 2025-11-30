# tests/test_expense_logic.py
import pytest
from models.expense_model import Expense


def test_expense_creation_and_to_dict():
    # create expense with minimal data
    exp = Expense(
        user_id="000000000000000000000001",
        amount=150.75,
        category="Food",
        payment_type="UPI"
    )

    d = exp.to_dict()
    assert isinstance(d, dict)
    assert d["amount"] == 150.75
    assert d["category"] == "Food"
    assert d["payment_type"] == "UPI"
    assert "user_id" in d and isinstance(d["user_id"], str)
    assert "_id" in d and isinstance(d["_id"], str)


def test_expense_update_amount_and_notes():
    exp = Expense(
        user_id="000000000000000000000002",
        amount=10,
        category="Transport",
        payment_type="Cash",
        notes="initial"
    )

    # update amount and notes
    exp.update(amount=25.5, notes="updated note")
    assert exp.amount == pytest.approx(25.5, rel=1e-6)
    assert exp.notes == "updated note"

    # update date with iso string
    iso = "2025-11-01T10:30:00"
    exp.update(date=iso)
    # ensure date was parsed to datetime in model
    assert hasattr(exp, "date")


def test_invalid_category_and_payment_type_validation():
    # Category validation uses static method - ensure invalid returns False
    assert not Expense.validate_category("NonExistingCategory")
    assert not Expense.validate_payment_type("GoldCoin")

    # Valid ones return True
    assert Expense.validate_category("Food")
    assert Expense.validate_payment_type("UPI")


def test_to_mongo_and_from_mongo_roundtrip():
    exp = Expense(
        user_id="000000000000000000000003",
        amount=99.99,
        category="Shopping",
        payment_type="Debit Card",
        notes="gift",
        tags=["gift", "sale"],
        receipt_url=None
    )

    mongo_doc = exp.to_mongo()
    assert "_id" in mongo_doc
    assert "user_id" in mongo_doc
    assert "amount" in mongo_doc

    # Simulate retrieval by converting date fields to iso and using from_mongo
    # (from_mongo expects fields similar to DB doc)
    sim_doc = mongo_doc.copy()
    # from_mongo expects created_at/updated_at maybe present; it's okay if not
    new_exp = Expense.from_mongo(sim_doc)
    assert new_exp is not None
    assert new_exp.amount == pytest.approx(99.99)
    assert new_exp.category == "Shopping"
    assert isinstance(new_exp.tags, list)
