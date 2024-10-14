from dataclasses import dataclass
from maze import Cell
from typing import Optional

@dataclass
class Point:
    x: int
    y: int
    
@dataclass
class Dimensions:
    width: int
    height: int

@dataclass
class StartEnd:
    start: Optional[Cell]
    end: Optional[Cell]
    
    def has_start(self) -> bool:
        self.start is not None
    
    def has_end(self) -> bool:
        self.end is not None
    
    def reset(self) -> None:
        self.start.mark_as_open()
        self.end.mark_as_open()
        self.start = self.end = None
    
    def progress(self, p: Cell) -> None:
        if self.start is not None and self.end is not None:
            self.reset()
        
        if self.start is None:
            self.start = p
        elif self.end is None:
            self.end = p
    
@dataclass(frozen=True, kw_only=True)
class Node:
    cell: Cell
    parent: Optional[Cell]
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