# -*- coding: utf-8 -*-
"""
Created on Wed May 11 12:00:52 2022

@author: Robert J McGinness
"""

from typing import Any
from typing import Dict
from typing import List

from rjm_gaming.game_view import GameView
from rjm_gaming.game_base import GameResult
from rjm_gaming.game_network import HTTPRequest



class QuizView(GameView):
    
    def render(self, data: Any) -> str:
        '''UNIMPLEMENTED HERE'''
        pass
    
    def render_with_file(self, **kwargs) -> str:
        '''UNIMPLEMENTED HERE'''
        pass
    
    def render_result_with_file(self, result: GameResult,
                                      file_name:str) -> str:
        ''' Adds result data to an html file'''
        if result.game_over:
            print('FINISH THIS')
        
        game_html = self.render_file(file_name) # defined in superclass
        
        
        ######ADD PLAYER INFORMATION, NAME, SCORE ETC from result.players[0]
        
        result_data = result.result_data
        question = result_data['question']
        has_skip_button = bool(result['next_question'])
        has_back_button = bool(result['prev_question'])
        
        game_html += self.__build_question(question.q_id, question.question)
        
        if not has_skip_button:
            game_html += game_html.replace('=skip', '=skip' + ' hidden')
        
        if not has_back_button:
            game_html += game_html.replace('=back', '=back' + ' hidden')
        
        choices_list = question.choices
        game_html = game_html.replace('<form>', '<form>' + \
                                          self.__build_choices(choices_list))
    
    def __build_question(self, number: int, question: str) -> str:
        question_html = '<p>NUM. QUESTION</p>'
        question_html = question_html.replace('NUM', number)
        
        return question_html.replace('QUESTION', question)
    
    def __build_choices(self, choices: List[str]) -> str:
        radio_button = '<input type="radio" id="XXX" name="XXX" value="XXX"/>'
        label = '<label for="XXX">CHOICE</label><br/>'
        
        all_choices_html = ''
        counter = 1
        for choice in choices:
            choice_html = radio_button + label
            choice_html = choice_html.replace('XXX', str(counter))
            choice_html = choice_html.replace('CHOICE', choice)
            all_choices_html += choice_html
            counter += 1
        
        return all_choices_html
    
    def render_result(self, result: GameResult) -> str:
        '''Return html string of result that can be sent to browser'''
        return self.render_result_with_file(result, self.html_file)
    
    def get_play(self, request: HTTPRequest) -> Dict:
        ''' Process new Play Request from browser.
            Return request as game-appropriate 
            key-value pairs.
        '''
        print('FINISH THIS')
        ######package request in key-value pairs matching what quiz.py needs
        ######to see

