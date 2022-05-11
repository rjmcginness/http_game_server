# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 13:17:21 2022

@author: Robert J McGinness
"""

from abc import ABC
from abc import abstractmethod
from typing import Any

from game_model import GameResult
from game_utilities import CommsModule
from game_utilities import CommRegistrant


class GameView(ABC, CommRegistrant):
    def __init__(self, name: str, comms: CommsModule, version: str = '0.0') -> None:
        self.__name = name
        self.__comms = comms
        self.__version = version
        self.__comms.register_output(self)
    
    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def version(self) -> str:
        return self.__version
    
    @abstractmethod
    def render_result(self, result: GameResult) -> Any:
        ...
    
    # @abstractmethod
    # def get(self) -> Any:
    #     ...
    
    @abstractmethod
    def put(self, data: Any) -> None:
        ...
    
    def introduction(self, data: Any) -> Any:
        pass
    
    @abstractmethod
    def render(self, data: Any) -> Any:
        ...
    
    # def render_all(self) -> Any:
    #     pass
    
    def game_over(self, data: Any) -> Any:
        pass
    
    # def start(self) -> Any:
    #     return (self.introduction(), self.render_all(), self.game_over()
        
    

