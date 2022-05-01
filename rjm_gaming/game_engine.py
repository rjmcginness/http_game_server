# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 13:54:49 2022

@author: Robert J McGinness
"""

from typing import List
from typing import Dict
from importlib import import_module
import time

from game_model import GameInvalidError
from game_utilities import CommsModule
from game_utilities import TerminalCommsModule
from game_utilities import DataAccess
from game_utilities import FileDataAccess


class Engine:
    def __init__(self, comms: CommsModule, data_access: DataAccess) -> None:
        self.__comms = comms
        self.__data_access = data_access
        self.__games = self.__data_access.games
        self.__cached_games = {}
    
    def load_game(self, name: str) -> Dict:
        '''Dynamically loads game class and instantiates an object of that class'''
        
        try:
            cached_game = self.__cached_games[name]
            return {'game' : cached_game['game_class'](name, self.__comms), 
                    'view' : cached_game['view_class'](self.__comms, time.time())}
        except KeyError:
            pass
        
        for game in self.__games:
            if game['name'] == name:
                break
            game = None
        
        try:
            game_module = import_module(game['game_path'][:-3], '.')
            view_module = import_module(game['view_path'][:-3], '.')
        except Exception as e:
            raise GameInvalidError(e)
        
        game_class = getattr(game_module, game['game_class'])
        view_class = getattr(view_module, game['view_class'])
        
        self.__cached_games[name] = {'game_class' : game_class,
                                     'view_class' : view_class}
        
        return {'game' : game_class(name, self.__comms), 
                'view' : view_class(self.__comms, time.time())}
    
    def run_game(self, game_name: str) -> None:
        game_objects = self.load_game(game_name)
        game_objects['game'].play()
        self.__comms.unregister(game_objects['view'])
        self.__comms.delete_logic()
            
    @property
    def comms(self) -> CommsModule:
        return self.__comms
    
    def get_games(self) -> List[str]:
        return [game for game in self.__games]
    
if __name__ == '__main__':
    
    comms = TerminalCommsModule()
    
    fa = FileDataAccess('./game_init.i')
    fa.initialize()
    print(fa.games)
    
    engine = Engine(comms, fa)
    engine.run_game('War')
    