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
import json

from game_authentication import ServerClient
from game_utilities import ClassLoader

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
    def __init__(self, name: str,
                  players: Optional[List[Player]] = None,
                  **kwargs) -> None:
        ''' Since every Game has at least one player,
            the initializer provides the option to
            instantiate a Game object with a list of
            players.
            This will default to None.  Players may
            be added or removed via other methods.
            kwargs can be used for subclasses and
            reflection
        '''
        self.__name = name
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
    def name(self) -> str:
        return self.__name
    
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
    
class ClassInitMeta(json.JSONEncoder):
    def __init__(self, class_name: str,
                       module_name: str,
                       package_name: str = '.') -> None:
        
        self.__class = ClassLoader.load_class(class_name,
                                              module_name,
                                              package_name)
        self.__module = self.__class.__module__
        self.__package = package_name
        self.__init_params = list(self.__class.__init__.__annotations__)
        self.__init_params.remove('return')
        self.__kwargs = {param: '' for param in self.__init_params}
        
    @property
    def game_class(self) -> Type:
        return self.__class
    
    @property
    def init_params(self) -> Dict:
        return self.__kwargs
    
    def add_kwarg(self, key: str, value: str) -> None:
        self.__kwargs[key] = value
    
    def default(self, obj: object) -> Dict:
        if isinstance(obj, self.__class):
            return self.encoding
        
        return json.JSONEncoder.default(self, obj)
    
    @property
    def encoding(self) -> Dict:
        
        return {'_meta':{'module':self.__module,
                         'cls':self.__class.__name__,
                         'pkg':self.__package},
                'kwargs': self.__kwargs}

    @classmethod
    def decode(cls, obj: object) -> "ClassInitMeta":
        
        try:
            class_name = obj['_meta']['cls']
            module_name = obj['_meta']['module']
            package_name = obj['_meta']['pkg']
            meta = cls(class_name, module_name, package_name)
            
            for kw, arg in obj['kwargs'].items():
                if arg is not None and arg != '':
                    meta.add_kwarg(kw, arg)
                
            return meta
        except (KeyError, ImportError):
            return obj
        
class GameInitMeta(ClassInitMeta):
    def __init__(self, specifier: str,
                       class_name: str,
                       module_name: str,
                       package_name: str = '.') -> None:
        super().__init__(class_name, module_name, package_name)
        self.__specifier = specifier
    
    @property
    def encoding(self) -> Dict:
        
        return {self.__specifier:super().encoding}

    @classmethod
    def decode(cls, obj: object) -> "GameInitMeta":
        
        try:
            specifier = obj['specifier']
            class_name = obj['_meta']['cls']
            module_name = obj['_meta']['module']
            package_name = obj['_meta']['pkg']
            meta = cls(specifier, class_name, module_name, package_name)
            
            for kw, arg in obj['kwargs'].items():
                if arg is not None and arg != '':
                    meta.add_kwarg(kw, arg)
                
            return meta
        except (KeyError, ImportError):
            return obj




if __name__ == '__main__':
    from rjm_gaming.game_view import GameView
    import json
    
    def initialize_games(self) -> List:
        for line in open('../init/game_init.i'):
            game_meta, view_meta = json.loads(line, GameInitMeta.decode)
            print(game_meta, view_meta)
       
            
        
        
    game_meta = ClassInitMeta('Game', 'rjm_gaming.game_base')
    view_meta = ClassInitMeta('GameView', 'rjm_gaming.game_view')
    meta = {'game':game_meta, 'view':view_meta}
    json_meta = json.dumps(meta)
    print(json.loads(json_meta, object_hook=GameInitMeta.decode))