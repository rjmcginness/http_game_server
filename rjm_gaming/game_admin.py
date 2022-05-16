# -*- coding: utf-8 -*-
"""
Created on Mon May 16 13:28:12 2022

@author: Robert J McGinness
"""

from typing import Optional

from abc import ABC
from abc import abstractmethod

from game_base import Game
from game_network import HTTPRequest
from config import Config

class GameAdmin(ABC):
    def __init__(self, game: Game, config: Config=None) -> None:
        self.__game = game
    
    @abstractmethod
    def administer(self, request: HTTPRequest) -> str:
        ...