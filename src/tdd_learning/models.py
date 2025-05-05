import datetime as dt
from dataclasses import dataclass
from typing import Optional, Set


@dataclass(frozen=True)
class OrderLine:
    order_id: str
    sku: str
    qty: int


class Batch:
    def __lt__(self, other: "Batch") -> bool:
        """Define less-than for sorting Batches by ETA."""
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta < other.eta

    def __init__(self, ref: str, sku: str, qty: int, eta: Optional[dt.date]):
        self.reference: str = ref
        self.sku: str = sku
        self.eta: Optional[dt.date] = eta
        self._purchased_quantity: int = qty
        self._allocations: Set[OrderLine] = set()

    def allocate(self, line: OrderLine) -> None:
        """Allocate an OrderLine to this Batch if possible."""
        if self.can_allocate(line):
            self._allocations.add(line)

    def can_allocate(self, line: OrderLine) -> bool:
        """Check if the OrderLine can be allocated to this Batch."""
        return line.sku == self.sku and line.qty <= self.available_quantity

    @property
    def available_quantity(self) -> int:
        """Calculate the available quantity for this Batch."""
        return self._purchased_quantity - self.allocate_quantity()

    def allocate_quantity(self):
        return sum(line.qty for line in self._allocations)

    def deallocate(self, line: OrderLine) -> None:
        """Deallocate an OrderLine from this Batch if it is allocated."""
        if line in self._allocations:
            self._allocations.remove(line)


class OutOfStock(Exception):
    """Exception raised when no batch is available to allocate an order line."""

    pass


def allocate(line: OrderLine, batches: list[Batch]) -> str:
    """Allocate an OrderLine to the first Batch that can allocate it.

    Args:
        line (OrderLine): The order line to allocate.
        batches (list[Batch]): A list of batches to allocate from.

    Returns:
        str: The reference of the batch to which the line was allocated.

    Raises:
        OutOfStock: If no batch is available to allocate the order line.
    """
    for batch in sorted(batches):
        if batch.can_allocate(line):
            batch.allocate(line)
            return batch.reference
    raise OutOfStock(
        f"No batch available to allocate the order line with SKU {line.sku}."
    )
