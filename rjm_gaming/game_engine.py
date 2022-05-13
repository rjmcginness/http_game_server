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
from game_base import ClassInitMeta



class GameEngine:
    def __init__(self, data_access: DataAccess) -> None:
        self.__data_access = data_access
        self.__game_init_list = self.__initialize_games()
    
    def __initialize_games(self) -> List:
        ''' Deserializes GameMeta data from the DataAccess connection
            Returns a list of dictionaries containing keys name and 
            class_meta.  The value for name is teh name of the game.
            The value for class_meta is also a dictionary.  The keys 
            are game and view, which have ClassInitMeta objects for
            the game class and game view class, respectively.
        '''
        init_lines = self.__data_access.data_lines
        game_initializers = []
        for line in init_lines:
            game_name = line.split('~')
            initialization = game_name[1] # reusing the game_name variable
            game_name = game_name[0]
            game_data = dict(name=game_name)
            game_data['class_meta'] = json.loads(initialization, 
                                            object_hook=ClassInitMeta.decode)
            game_initializers.append(game_data)
    
        return game_initializers
        
    
    def load_game(self, name: str) -> Dict:
        ''' Instantiates objects of the game and game view classes
            from the ClassInitMeta objects for each.
            Returns a dictionary with key-value pairs game:Game 
            instance and view:GameView instance.  These Game and 
            GameView objects can be used by the ClientService to 
            control and render the game.
        '''
        
        try:
            game_meta = None
            view_meta = None
            for game in self.__game_init_list:
                if game['name'] == name:
                    game_meta = game['class_meta']['game']
                    view_meta = game['class_meta']['view']
                    break
                    
            game_obj = game_meta.instance()
            view_obj = view_meta.instance()
            
            return dict(game=game_obj, view=view_obj)
        
        except Exception as e:
            raise GameInvalidError(e) from e
    
    def get_games(self) -> List[str]:
        '''Returns a list of game names loaded into the engine'''
        return list(self.__game_init_list)
    
if __name__ == '__main__':
    from game_utilities import FileDataAccess
    
    fa = FileDataAccess('../init/game_init.i', raw=False)
    fa.initialize()
    
    engine = GameEngine(fa)
    engine.load_game('Quiz')

    