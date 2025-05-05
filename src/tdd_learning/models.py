import datetime as dt
from dataclasses import dataclass


@dataclass(frozen=True)
class OrderLine:
    order_id: str
    sku: str
    qty: int


class Batch:
    def __init__(self, ref: str, sku: str, qty: int, eta: dt.date | None):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = qty
        self._allocations = set[OrderLine]()

    def allocate(self, line: OrderLine):
        if line.sku == self.sku and line.qty <= self.available_quantity:
            self._allocations.add(line)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - sum(line.qty for line in self._allocations)
