from dataclasses import dataclass
from typing import Optional
from cell import *

@dataclass
class StartEnd:
    start: Optional[Cell]
    end: Optional[Cell]
    
    def is_empty(self) -> bool:
        return self.start is None and self.end is None
    
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