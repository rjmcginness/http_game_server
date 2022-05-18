# -*- coding: utf-8 -*-
"""
Created on Mon May 16 13:28:12 2022

@author: Robert J McGinness
"""

from abc import ABC
from abc import abstractmethod
from typing import Tuple

from game_network import HTTPRequest
from config import Config

class GameAdmin(ABC):
    def __init__(self, config: Config=None) -> None:
        self.__config = config
    
    @abstractmethod
    def administer(self, request: HTTPRequest) -> Tuple:
        ...