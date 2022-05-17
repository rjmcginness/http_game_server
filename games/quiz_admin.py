# -*- coding: utf-8 -*-
"""
Created on Mon May 16 13:36:34 2022

@author: Robert J McGinness
"""

import time
import json

from rjm_gaming.game_admin import GameAdmin
from rjm_gaming.game_network import HTTPRequest
from rjm_gaming.game_network import parse_query
from rjm_gaming.game_network import remove_http_pluses
from rjm_gaming.game_network import HTTPHeader
from config import Config
from quiz import Question


class QuizAdmin(GameAdmin):
    def __init__(self, config: Config) -> None:
        super().__init__(config)
        self.__admin_html = None
        self.__question_buffer = []
        self.__quiz_name = None
        
        with open(config.ADMIN_PAGE, 'rt') as admin_file:
            self.__admin_html = admin_file.read()
        
    def administer(self, request: HTTPRequest) -> str:

        query_input = parse_query(request['request_type'], 'input=')
        self.__quiz_name = parse_query(request['request_type'], 'name=')

        if query_input == 'Save+Quiz':
            self.__question_buffer.append(self.__build_question(request))
            self.__write_quiz()
            
        if  query_input == 'Add+Question': # a new question has been entered on the page
            self.__question_buffer.append(self.__build_question(request))
        
        return self.__build_question_page(request)
    
    def clear(self) -> None:
        self.__name = None
        self.__question_buffer.clear()
    
    def __write_quiz(self) -> None:
        '''WARNING THIS WILL OVERWRITE AN EXISTING FILE'''
        if not self.__question_buffer: # empty list
            return
        
        if not self.__name:
            self.__name = 'quiz'
        
        # encode each question as json, then write to file
        with open('/quiz/' + self.__name + '.quiz', 'wt') as quiz_file:
            for question in self.__question_buffer:
                quiz_file.write(json.dumps(question.encoding) + '\n')
        
        self.clear()
    
    def __build_question(self, request: HTTPRequest) -> Question:
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
        
        return Question(question,
                        answer,
                        str(time.time()),
                        [choice1, choice2, choice3, choice4],
                        'multiple_choice')
    
    def __build_question_page(self, request: HTTPRequest) -> str:
        header = HTTPHeader()
        header.content_type = 'text/html; charset=utf-8'
        header.connection = 'close'
        
        output = ''
        
        if self.__quiz_name:
            output = self.__admin_html.replace('placeholder="Quiz Name"',
                                               f'value="{self.__quiz_name}"')
        
        return request.session.form_insert(output)
        
        
        
        