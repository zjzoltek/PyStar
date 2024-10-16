from errors import IncorrectNumberOfArgsError, InvalidArgError
from log import logging


class Console:
    def __init__(self, prompt_end: str = '=>'):
        self._prompt_end = prompt_end
        self._logger = logging.getLogger(Console.__name__)
    
    def request(self, prompt: str) -> list[str]:
        return input(f'{prompt}{self._prompt_end}').split(' ')
    
    def switch(self, prompt: str) -> bool:
        valid_answers: set[str] = {'y', 'yes', 'n', 'no'}
        affirmative_answers: set[str] = {'y', 'yes'}
        
        while True:
            try:
                args = self.request(prompt)

                if len(args) != 1:
                    raise 
                
                answer = args[0].lower()
                
                if answer not in valid_answers:
                    raise f'Input must be one of: {valid_answers}'
                
                return answer in affirmative_answers
            except Exception as e:
                self.err(e)
                continue

    def out(self, content: str):
        self._logger.info(content)
        
    def err(self, content: str):
        self._logger.error(content)
