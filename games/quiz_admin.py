# -*- coding: utf-8 -*-
"""
Created on Mon May 16 13:36:34 2022

@author: Robert J McGinness
"""

from rjm_gaming.game_admin import GameAdmin
from rjm_gaming.game_network import HTTPRequest
from rjm_gaming.game_network import parse_query
from rjm_gaming.game_network import remove_http_pluses
from rjm_gaming.game_base import Game
from config import Config


class QuizAdmin(GameAdmin):
    def __init__(self, game: Game, config: Config) -> None:
        super().__init__(game, config)
        self.__admin_html = None
        self.__question_buffer = []
        
        with open(config.ADMIN_PAGE, 'rt') as admin_file:
            self.__admin_html = admin_file.read()
        
    def administer(self, request: HTTPRequest) -> str:

        query_input = parse_query(request['request_type'], 'input=')

        if  query_input == 'new_question': # a new question has been entered on the page
            self.__question_buffer.append(self.__build_question(request))
        
        return self.__build_question_page(request)
    
    def __build_question(self, request: HTTPRequest) -> str:
        question = parse_query(request['request_type'], 'question=')
        answer = parse_query(request['request_type'], 'answer=')
        choice1 = parse_query(request['request_type'], 'choice1=')
        choice2 = parse_query(request['request_type'], 'choice2=')
        choice3 = parse_query(request['request_type'], 'choice3=')
        choice4 = parse_query(request['request_type'], 'choice4=')
        
        '''Dealing with spaces in html and the problem of a + in an answer'''
        question = remove_http_pluses(question)
        answer = remove_http_pluses(answer)
        choice1 = remove_http_pluses(choice1)
        choice2 = remove_http_pluses(choice2)
        choice3 = remove_http_pluses(choice3)
        choice4 = remove_http_pluses(choice4)