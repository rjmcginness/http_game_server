# -*- coding: utf-8 -*-
"""
Created on Tue May 10 13:30:39 2022

@author: Robert J McGinness
"""

from abc import ABC
from abc import abstractmethod
from typing import Optional
from typing import List
from typing import Any
from typing import Dict

from game_base import GameResult
from game_network import HTTPRequest


class GameView(ABC):
    def __init__(self, html_file: Optional[str] = None,
                       css_files: Optional[List[str]] = None,
                       scripts: Optional[List[str]] = None) -> None:
        self.__html_file = html_file
        self.__css_files = css_files
        self.__scripts = scripts
    
    @property
    def html_file(self) -> Optional[str]:
        return self.__html_file
    
    @property
    def css_files(self) -> Optional[List[str]]:
        return self.__css_files
    
    @property
    def scripts(self) -> Optional[List[str]]:
        return self.__scripts
    
    def render_file(self, file_name: str) -> str:
        with open(file_name, 'rt') as file:
            return file.read()
        
        return
    
    @abstractmethod
    def render(self, data: Any) -> str:
        ...
    
    @abstractmethod
    def render_with_file(self, **kwargs) -> str:
        ...
    
    @abstractmethod
    def render_result_with_file(self, result: GameResult,
                                      file_name:str) -> str:
        ...
    
    @abstractmethod
    def render_result(self, result: GameResult) -> str:
        ...
    
    @abstractmethod
    def get_play(self, request: HTTPRequest) -> Dict:
        ...

