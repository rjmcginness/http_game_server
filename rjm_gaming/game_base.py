# -*- coding: utf-8 -*-
"""
Created on Tue May 10 11:51:26 2022

@author: Robert J McGinness
"""
from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from typing import List
from typing import Optional
from typing import Tuple
from typing import Dict
from typing import Type

from game_authentication import ServerClient

class GameInvalidError:
    pass

class GameResult:
    def __init__(self, players: Tuple[Player],
                        game_name: str = '',
                        result_id: int = 0,
                        game_over: bool = False,
                        winner: Optional[Player] = None,
                        **kwargs) -> None:
        
        self.__players = players
        # self.__session = session
        self.__game_name = game_name
        self.__id = result_id
        self.__game_over = game_over
        self.__winner = winner
        self.__results: Dict = kwargs
    
    @property 
    def players(self) -> Tuple:
        return self.__players
    
    # @property
    # def session(self) -> str:
    #     return self.__session
    
    @property
    def game_name(self) -> str:
        return self.__game_name
    
    @property 
    def result_id(self) -> int:
        return self.__id
    
    @property 
    def game_over(self) -> bool:
        return self.__game_over
    
    @property 
    def winner(self) -> Player:
        return self.__winner
    
    @property 
    def result_data(self) -> Dict:
        return self.__results
    
    @property
    def encoding(self) -> Dict:
        return {'_meta':{'module':self.__module__,
                         'cls':self.__class__.__name__},
                'game_name':self.__game_name,
                'id':self.__id,
                'players':[player.encoding for player in self.__players],
                'game_over':self.__game_over,
                'winner':self.__winner.encoding if self.__winner else None,
                'results':self.__results}
    
    @classmethod
    def decode(cls: Type, obj: object) -> "GameResult":
        try:
            if obj['_meta']['cls'] == cls.__name__:
                players = []
                for player_data in obj['players']:
                    players.append(Player.build(player_data))
                
                winner = Player.build(obj['winner'])
                
                return cls(*players, game_name=obj['game_name'],
                                              result_id=obj['id'],
                                              game_over=obj['game_over'],
                                              winner=winner,
                                              results=obj['results'])
        except (KeyError, ImportError):
            return obj
        
    
    def __repr__(self) -> str:
        return str(self.encoding)
    
class Player(ServerClient):
    def __init__(self, name: str,
                 client_id: str,
                 experience: float=0.0,
                 score: float = 0.0,
                 iswinner: bool = False) -> None:
        
        super().__init__(name, client_id)
        self.__experience = experience
        self.__score = score
        self.__iswinner = iswinner
    
    @property
    def experience(self) -> float:
        return self.__experience
    
    @experience.setter
    def experience(self, exp) -> None:
        self.__experience = exp
    
    @property
    def score(self) -> float:
        return self.__score
    
    @score.setter
    def score(self, new_score: float) -> None:
        self.__score = new_score
    
    @property
    def iswinner(self) -> bool:
        return self.__iswinner

    @iswinner.setter
    def iswinner(self, win: bool) -> None:
        self.__iswinner = win
    
    @property
    def encoding(self) -> Dict:
        return {'_meta':{'module':self.__module__,
                         'cls':self.__class__.__name__},
                'name':self.name,
                'id':self.client_id,
                'auth':self.isauthenticated,
                'experience':self.__experience,
                'score':self.__score,
                'winner':self.__iswinner}
    
    @classmethod
    def decode(cls: Type, obj: object):
        try:
            if obj['_meta']['cls'] == cls.__name__:
                return cls(obj['name'],
                           obj['id'],
                           experience=obj['experience'],
                           score=obj['score'],
                           iswinner=obj['winner'])
        except KeyError:
            return obj
    
class Game(ABC):
    ''' A Game is a state machine.  This is
        an abstract base class used for which
        the next_result method must be implemented
        by instantiable subclasses
    '''
    def __init__(self, players: Optional[List[Player]] = None) -> None:
        ''' Since every Game has at least one player,
            the initializer provides the option to
            instantiate a Game object with a list of
            players.
            This will default to None.  Players may
            be added or removed via other methods.
        '''
        if not players:
            self.__players = []
        else:
            self.__players = players
        
        self.__results: List[GameResult] = []
    
    def add_player(self, player: Player) -> None:
        '''Add a new player to the game'''
        self.__players.append(player)
    
    def remove(self, player: Player) -> None:
        '''Removes player from Game, if present'''
        try:
            self.__players.remove(player)
        except ValueError:
            pass
    
    def isplaying(self, player: Player) -> bool:
        ''' Determines if a player is in this game
            Returns True is player is in game, 
            False otherwise.
        '''
        return player in self.__players
    
    @property
    def players(self) -> Tuple[Player]:
        return tuple(self.__players)
    
    @property
    def player_count(self) -> int:
        '''Returns the number of players in the Game'''
        return len(self.__players)
    
    @property
    def results(self) -> Tuple:
        ''' Returns a copy of all GameResults so far
            as a Tuple
        '''
        return tuple(self.__results[:])
    
    def play_next(self, **kwargs) -> GameResult:
        ''' Called by the Client Service object to
            allow the game to control logic.  The result
            returned may be rendered to the player(s).
            All GameResults are also maintained by the
            Game object.
        '''
        result = self.next_result(**kwargs)
        self.__results.append(result)
        
        return result
    
    @abstractmethod
    def _next_result(self, **kwargs) -> GameResult:
        ''' Creates the next result of the Game, based
            on the game's logic.  This should be
            implemented for each game subclass intended
            to work as a full-standing game
        '''
        ...
    
    