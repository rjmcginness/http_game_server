# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 13:54:49 2022

@author: Robert J McGinness
"""

from typing import List
from typing import Dict
import time

import json

from game_base import GameInvalidError
from game_utilities import DataAccess
from game_utilities import ClassLoader
from game_base import GameInitMeta



class GameEngine:
    def __init__(self, data_access: DataAccess) -> None:
        self.__data_access = data_access
        self.__game_init_list = self.__initialize_games()
        
        self.__cached_games = {}
    
    def __initialize_games(self) -> List:
        init_lines = self.__data_access.data_lines
        game_meta = None
        view_meta = None
        for line in init_lines:
            game_meta, view_meta = json.loads(line, GameInitMeta.decode)
        
        print(game_meta, view_meta)
        
    
    def load_game(self, name: str) -> Dict:
        '''Dynamically loads game class and instantiates an object of that class'''
        
        try:
            cached_game = self.__cached_games[name]
            return {'game' : cached_game['game_class'](name), 
                    'view' : cached_game['view_class'](time.time())}
        except KeyError:
            pass
        
        for game in self.__games:
            if game['name'] == name:
                break
            game = None
        
        try:
            game_class = ClassLoader(game['game_path'], game['game_class'])
            view_class = ClassLoader(game['view_path'], game['view_class'])
        except Exception as e:
            raise GameInvalidError(e) from e
        
        # try:
        #     game_module = import_module(game['game_path'][:-3], '.')
        #     view_module = import_module(game['view_path'][:-3], '.')
        # except Exception as e:
        #     raise GameInvalidError(e)
        
        # game_class = getattr(game_module, game['game_class'])
        # view_class = getattr(view_module, game['view_class'])
        
        self.__cached_games[name] = {'game_class' : game_class,
                                     'view_class' : view_class}
        
        return {'game' : game_class(name, game['game_kwargs']), 
                'view' : view_class(str(time.time()), game['view_kwargs'])}
    
    def run_game(self, game_name: str) -> None:
        game_objects = self.load_game(game_name)
        game_objects['game'].play()

    
    def get_games(self) -> List[str]:
        return [game for game in self.__games]
    
if __name__ == '__main__':
    from game_utilities import FileDataAccess
    
    fa = FileDataAccess('../init/game_init.i', raw=False)
    fa.initialize()
    
    engine = GameEngine(fa)

    