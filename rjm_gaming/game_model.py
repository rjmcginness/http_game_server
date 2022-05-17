# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 09:55:36 2022

@author: Robert J McGinness
"""
from __future__ import annotations

from abc import abstractmethod
from abc import ABC
from typing import List
from typing import Tuple
from typing import Dict
from typing import Optional
from typing import Type
from importlib import import_module
from game_utilities import CommsModule


class GameInvalidError(Exception):
    pass

class Game(ABC):
    def __init__(self, name: str, comms: CommsModule, players: List[Player] = []) -> None:
        self.__name = name
        self.__comms = comms
        self.__players: List["Player"] = players
        self.__result_history: List["GameResult"] = []
        self.__comms.set_logic(self)
    
    @property 
    def name(self) -> str:
        return self.__name
    
    def play(self) -> None:
        self.start_game()
    
    @abstractmethod 
    def start_game(self) -> None:
        ...
    
    def add_player(self, player: Player) -> None:
        self.__players.append(player)
    
    def remove_player(self, player: Player) -> None:
        self.__players.remove(player)
    
    @property
    def players(self) -> Tuple:
        return tuple(self.__players)
    
    @property 
    def player_count(self) -> int:
        return len(self.__players)
    
    def isplaying(self, player: "Player") -> int:
        '''
        returns the index if the player is in the game, 
        otherwise raises ValueErrorexception
        '''
        return self._Game__players.index(player)
    
    @property
    def history(self) -> List["GameResult"]:
        return self.__result_history[:] #makes a copy
    
    def __add_result(self, result: "GameResult") -> None:
        self.__result_history.append(result)

class Player():
    def __init__(self, player_id: str, name: str, experience: int = None) -> None:
        self.__id = player_id
        self.__name = name
        self.__experience = experience
    
    @property 
    def player_id(self) -> str:
        return self.__id
    
    @property 
    def name(self) -> str:
        return self.__name
    
    @property 
    def experience(self) -> int:
        return self.__experience
    
    @experience.setter 
    def experience(self, expr: int) -> None:
        self.__experience = expr
    
    def __eq__(self, player2) -> bool:
        return (self.__id == player2.player_id and self.__name == player2.name)
    
    def __repr__(self) -> str:
        return self.__name + " id:" + self.__id
    
    @property
    def encoding(self) -> Dict:
        return {'_meta':{'module':self.__module__,
                         'cls':self.__class__.__name__},
                'name':self.__name,
                'id':self.__id,
                'experience':self.__experience}
    
    @classmethod
    def decode(cls: Type, obj: object):
        try:
            if obj['_meta']['cls'] == cls.__name__:
                return cls(obj['id'], obj['name'], experience=obj['experience'])
        except KeyError:
            return obj
    
    @staticmethod
    def build(player_data: Dict) -> Player:
        if player_data == 'null':
            return None
        
        class_module = import_module(player_data['_meta']['module'], '.')
        class_name = player_data['_meta']['cls']
        player_class = getattr(class_module, class_name)
        
        return player_class.decode(player_data)

class GameResult:
    def __init__(self, *players: Player,
                         game_name: str = '',
                         result_id: int = 0,
                         game_over: bool = False,
                         winner: Optional[Player] = None,
                         results: Optional[Dict] = None) -> None:
        self.__game_name = game_name
        self.__id = result_id
        self.__players = tuple(players)
        self.__game_over = game_over
        self.__winner = winner
        self.__results: Dict = {}
        if not results is None:
            self.__results.update(results)
    
    @property 
    def result_id(self) -> int:
        return self.__id
    
    @property 
    def game_over(self) -> bool:
        return self.__game_over
    
    @property 
    def players(self) -> Tuple:
        return self.__players
    
    @property 
    def winner(self) -> Player:
        return self.__winner
    
    @property 
    def result_data(self) -> Dict:
        return self.__results.copy()
    
    @property
    def encoding(self) -> Dict:
        return {'_meta':{'module':self.__module__,
                         'cls':self.__class__.__name__},
                'game_name':self.__game_name,
                'id':self.__id,
                'players':[player.encoding for player in self.__players],
                'game_over':self.__game_over,
                'winner':self.__winner.encoding,
                'results':self.__results}
    
    @classmethod
    def decode(cls: Type, obj: object) -> GameResult:
        return_object = obj
        try:
            if obj['_meta']['cls'] == cls.__name__:
                players = []
                for player_data in obj['players']:
                    players.append(Player.build(player_data))
                
                winner = Player.build(obj['winner'])
                
                return_object = cls(*players, game_name=obj['game_name'],
                                              result_id=obj['id'],
                                              game_over=obj['game_over'],
                                              winner=winner,
                                              results=obj['results'])
        except KeyError:
            return_object = obj
        
        return return_object
    
    def __repr__(self) -> str:
        return str(self.encoding)



if __name__ == '__main__':
    exit()
    # import json
    # p1 = Player('1', 'Pleyer One')
    # gr = GameResult(*[p1],
    #                   game_name='War',
    #                   winner=p1,
    #                   results={'blah':'blah'})
    # print(gr)
    # print()
    # print('JSON')
    # json_data = json.dumps(gr, object_hook=GameResult.encode)
    # print(json_data)
    # data = json.loads(json_data, object_hook=GameResult.decode)
    # print(type(data),data)
    # print()
    # json_data = json.dumps(p1, cls=PlayerEncoder)
    # print(json_data)
    # p1 = json.loads(json_data, object_hook=Player.decode)
    # print(type(p1), p1)