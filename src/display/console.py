from typing import Optional

from log import logging
from validation.has_length import HasLength
from validation.is_in import IsIn
from validation.validator import Validator


class Console:
    def __init__(self, prompt_end: str = '=>'):
        self._prompt_end = prompt_end
        self._logger = logging.getLogger(Console.__name__)
    
    def request(self, prompt: str, v: Optional[Validator] = None) -> list[str]:
        args = input(f'{prompt}{self._prompt_end}').split(' ')
        if v:
            v.validate(args)

        return args
    
    def switch(self, prompt: str) -> bool:
        yes = ('y', 'yes')
        no = ('n', 'no')
        
        args = list(map(lambda arg: arg.lower(), self.request(prompt, Validator(HasLength(1)))))
        
        return Validator(IsIn([*yes, *no])).validate(args)

    def out(self, content: str):
        self._logger.info(content)
        
    def err(self, content: str):
        self._logger.error(content)
