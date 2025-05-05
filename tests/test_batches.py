import datetime as dt

from tdd_learning.models import Batch, OrderLine

# filepath: src/tdd_learning/test_models.py


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=dt.date.today())
    line = OrderLine("order-ref", "SMALL-TABLE", 2)

    batch.allocate(line)

    assert batch.available_quantity == 18


def test_allocating_orderline_with_different_sku_does_not_change_available_quantity():
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=dt.date.today())
    line = OrderLine("order-ref", "LARGE-TABLE", 2)

    batch.allocate(line)

    assert batch.available_quantity == 20


def test_allocating_orderline_with_quantity_greater_than_available_does_not_change_available_quantity():
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=dt.date.today())
    line = OrderLine("order-ref", "SMALL-TABLE", 25)

    batch.allocate(line)

    assert batch.available_quantity == 20


def test_allocating_orderline_with_zero_quantity_does_not_change_available_quantity():
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=dt.date.today())
    line = OrderLine("order-ref", "SMALL-TABLE", 0)

    batch.allocate(line)

    assert batch.available_quantity == 20


def test_allocation_is_idempotent():
    batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=dt.date.today())
    line = OrderLine("order-ref", "SMALL-TABLE", 2)

    batch.allocate(line)
    batch.allocate(line)  # Allocating the same line again

    assert batch.available_quantity == 18
