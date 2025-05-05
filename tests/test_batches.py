import datetime as dt

import pytest

from tdd_learning.models import Batch, OrderLine, OutOfStock, allocate

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


def test_allocate_returns_batch_reference_when_allocation_is_successful():
    batch1 = Batch("batch-001", "SMALL-TABLE", qty=10, eta=dt.date.today())
    batch2 = Batch(
        "batch-002", "SMALL-TABLE", qty=20, eta=dt.date.today() + dt.timedelta(days=1)
    )
    batches = [batch1, batch2]
    line = OrderLine("order-ref", "SMALL-TABLE", 5)

    result = allocate(line, batches)

    assert result == "batch-001"
    assert batch1.available_quantity == 5
    assert batch2.available_quantity == 20


def test_allocate_prefers_earlier_batches():
    batch1 = Batch("batch-001", "SMALL-TABLE", qty=10, eta=dt.date.today())
    batch2 = Batch(
        "batch-002", "SMALL-TABLE", qty=20, eta=dt.date.today() + dt.timedelta(days=1)
    )
    batches = [batch1, batch2]
    line = OrderLine("order-ref", "SMALL-TABLE", 10)

    result = allocate(line, batches)
    assert result == "batch-001"
    assert batch1.available_quantity == 0
    assert batch2.available_quantity == 20


def test_allocate_reduces_available_quantity_in_allocated_batch():
    batch1 = Batch("batch-001", "SMALL-TABLE", qty=10, eta=dt.date.today())
    batch2 = Batch(
        "batch-002", "SMALL-TABLE", qty=20, eta=dt.date.today() + dt.timedelta(days=1)
    )
    batches = [batch1, batch2]
    line = OrderLine("order-ref", "SMALL-TABLE", 5)

    allocate(line, batches)

    assert batch1.available_quantity == 5
    assert batch2.available_quantity == 20


def test_allocate_raises_value_error_when_no_batches_can_allocate():
    batch1 = Batch("batch-001", "SMALL-TABLE", qty=10, eta=dt.date.today())
    batch2 = Batch(
        "batch-002", "SMALL-TABLE", qty=20, eta=dt.date.today() + dt.timedelta(days=1)
    )
    batches = [batch1, batch2]
    line = OrderLine("order-ref", "LARGE-TABLE", 5)  # SKU does not match

    with pytest.raises(
        OutOfStock,
        match="No batch available to allocate the order line with SKU LARGE-TABLE.",
    ):
        allocate(line, batches)
