from dataclasses import dataclass
from typing import Optional
from models.cell import *

@dataclass
class StartEnd:
    start: Optional[Cell]
    end: Optional[Cell]
    
    def is_empty(self) -> bool:
        return self.start is None and self.end is None
    
    def reset(self) -> None:
        if self.start:
            self.start.mark_as_open()
        
        if self.end:
            self.end.mark_as_open()
            
        self.start = self.end = None
    
    def progress(self, p: Optional[Cell]) -> None:
        if p is None:
            return
        
        if self.start is not None and self.end is not None:
            self.reset()
        
        if self.start is None:
            self.start = p
        elif self.end is None:
            self.end = p