# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 13:22:11 2022

@author: Robert J McGinness
"""

from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import Tuple
from typing import Optional
from sys import stdin
from sys import stdout

class GameCommsError(Exception):
    pass


class CommRegistrant:
    '''Dummy type to unlink the untilities from specific
       view or game objects
    '''
    pass

class CommsModule(ABC):
    def __init__(self):
        self.__in: Any
        self.__out: Any
        self.__io = []
        self.__logic = None
    
    @property
    def in_(self) -> Any:
        return self.__in
    
    @property
    def out(self) -> Any:
        return self.__out
    
    @abstractmethod
    def write(self, data: Any) -> None:
        ...
     
    
    def read(self) -> Any:
        '''Implemented only to read from one io point'''
        try:
            input_data = self.__io[0].put(self.read_input())#only for one io point
        except Exception as e:
            raise GameCommsError(e)
        return input_data
    
    @abstractmethod
    def read_input(self) -> Any:
        ...
    
    def display(self, data: Any) -> Any:
        '''Uses duck typing to call render on view object
           registered as an io point
        '''
        for output in self.__io:
            self.write(output.render(data))
    
    def set_logic(self, registrant: CommRegistrant) -> None:
        self.__logic = registrant
    
    def register_output(self, output: CommRegistrant) -> None:
        if output not in self.__io:
            self.__io.append(output)
            
    def unregister(self, output: CommRegistrant) -> None:
        try:
            self.__io.remove(output)
        except:
            return
    def delete_logic(self) -> None:
        self.__logic = None

class StandardCommsModule(CommsModule):
    def __init__(self) -> None:
        super().__init__()
        self._CommsModule__in = stdin
        self._CommsModule__out = stdout
        
    def write(self, data: Any) -> None:
        self._CommsModule__out.write(data)
    
    def read_input(self) -> Any:
        return self._CommsModule__in.read()
    
class TerminalCommsModule(StandardCommsModule):
    def __init__(self) -> None:
        super().__init__()
    
    def read_input(self) -> Any:
        '''Overridden to read a line of input from the terminal'''
        return input()
    

class DataAccess(ABC):
    def __init__(self, init_path) -> None:
        self.__path = init_path
        
    @property
    def path(self) -> str:
        return self.__path
    
    @abstractmethod
    def initialize(self) -> None:
        ...
    
class FileDataAccess(DataAccess):
    def __init__(self, init_path) -> None:
        super().__init__(init_path)
        self.__games: Tuple = ()
    
    def initialize(self) -> None:
        for game in open(self.path, 'rt'):
            game_path = game.split()
            # class listed first, path ends line and has \n
            self.__games += (dict(name=game_path[0],
                                  game_path=game_path[1],
                                  game_class=game_path[2],
                                  view_path=game_path[3],
                                  view_class=game_path[4]),)

    @property
    def games(self) -> Optional[Tuple]:
        return self.__games[:]