# -*- coding: utf-8 -*-
"""
Created on Tue May 10 13:59:48 2022

@author: Robert J McGinness
"""

from rjm_gaming.game_base import Game
from rjm_gaming.game_base import GameResult


class Question:
    def __init__(self, question: str,
                 answer: str,
                 choices: Optional[List[str]] = None,
                 question_type: Optional[str] = None) -> None:
        self.question = question
        self.answer = answer
        self.choices = choices
        self.question_type = question_type

class Quiz(Game):
    def __init__(self, name: str, player: Player, quiz_file: str) -> None:
        super().__init__([player])
        self.__name = name
        self.__quiz_file = quiz_file
        self.__initialize()
        self.__questions
        
    def __initialize(self) -> None:
        for question_data in open(quiz_file, 'rt'):
            self.questions.append(self.__parse_question(question_data))
    
    def __parse_question(self, question_data: str) -> Question:
        
        
    def next_result(self, **kwargs) -> GameResult:
        


