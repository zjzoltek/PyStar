from dataclasses import dataclass
from typing import Optional
from models.cell import Cell

type _Node = Node
@dataclass(frozen=True)
class Node:
    cell: Cell
    parent: Optional[_Node]
    gCost: float
    hCost: float
    
    @property
    def fCost(self) -> float:
        return self.gCost + self.hCost
    
    def __repr__(self) -> str:
        return repr(self.cell)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return NotImplemented
        return self.fCost < other.fCost

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return NotImplemented
        return self.fCost > other.fCost

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return NotImplemented
        return self.fCost <= other.fCost

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return NotImplemented
        return self.fCost >= other.fCost

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return NotImplemented
        return self.fCost == other.fCost

    def __ne__(self, other: object) -> bool:
        return not self == other

    def __hash__(self) -> int:
        return hash(self.__repr__())