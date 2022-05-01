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
from game_utilities import CommsModule
from game_utilities import CommRegistrant

class GameInvalidError(Exception):
    pass

class Game(ABC, CommRegistrant):
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

class Player(ABC):
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

class GameResult(Dict):
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
        if not results is None:
            self.update(results)
    
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
