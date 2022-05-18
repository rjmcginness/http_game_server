# -*- coding: utf-8 -*-
"""
Created on Mon May 16 13:36:34 2022

@author: Robert J McGinness
"""

from typing import Tuple
from pathlib import Path


from rjm_gaming.game_admin import GameAdmin
from config import Config
from rjm_gaming.game_network import HTTPRequest
from rjm_gaming.game_network import HTTPHeader


class QuizAdmin(GameAdmin):
    def __init__(self, config: Config) -> None:
        super().__init__(config)
        self.__admin_html = None
        
        with open('../static/quiz/admin.html', 'rt') as admin_file:
            self.__admin_html = admin_file.read()
        
    def administer(self, request: HTTPRequest) -> Tuple:
        header = HTTPHeader()
        header.content_type = 'text/html; charset=utf-8'
        header.connection = 'close'
        
        
        
        games_html = ''
        for name in game_names:
            games_html += self.__build_game_html(name, '/admin')
            
        games_menu = games_menu.replace('%GAMES%', games_html)
        
        # prep file after adding game html
        games_menu = self.__prep_output_file(games_menu, request)
        
        header.content_length = len(games_menu)
    
    def __discover_quizzes() -> Tuple:
        path = Path('./quiz')
        return tuple([file for file in path.iterdir() if not file.isdir()])
    
    def __build_game_html(self, game_name: str, action: str) -> str:
        game_link = f'<form action="{action}" method="get">'
        game_link += f'<input type="submit" value="{game_name}" name="game" />'
        game_link += '</form>'
        
        return game_link
    