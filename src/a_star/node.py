from dataclasses import dataclass

from maze import Cell


@dataclass(frozen=True, kw_only=True)
class Node:
    cell: Cell
    parent: Cell
    gCost: float
    hCost: float
    
    @property
    def fCost(self) -> float:
        return self.gCost + self.hCost
    
    def __repr__(self):
        return repr(self.cell)
    
    def __lt__(self, other):
        return self.fCost < other.fCost
    
    def __gt__(self, other):
        return self.fCost > other.fCost
    
    def __le__(self, other):
        return self.fCost <= other.fCost
    
    def __ge__(self, other):
        return self.fCost >= other.fCost
    
    def __eq__(self, other):
        return self.fCost == other.fCost
    
    def __ne__(self, other):
        return not self == other
    
    def __hash__(self):
        return hash(self.__repr__())