from typing import Optional, Sequence, Any
from collections import deque

from log import logging
from validation.has_length import HasLength
from validation.is_in import IsIn
from validation.validator import Validator


class Console:
    def __init__(self, prompt_end: str = '=>') -> None:
        self._prompt_end = prompt_end
        self._logger = logging.getLogger(Console.__name__)
    
    def request(self, prompt: str, set_validator: Optional[Validator[Any]] = None, item_validator: Optional[Validator[str]] = None) -> list[str]:
        args = input(f'{prompt}{self._prompt_end}').split(' ')
        if set_validator:
            set_validator.validate(args)
        if item_validator:
            deque(map(item_validator.validate, args), maxlen=0)

        return args
    
    def switch(self, prompt: str) -> bool:
        yes = ('y', 'yes')
        no = ('n', 'no')

        args = list(map(lambda arg: arg.lower(), self.request(prompt, Validator(HasLength(1)))))

        validated_args = Validator(IsIn([*yes, *no])).validate(args)
        return validated_args[0] in yes

    def out(self, content: str) -> None:
        self._logger.info(content)

    def err(self, content: str) -> None:
        self._logger.error(content)
