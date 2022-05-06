# -*- coding: utf-8 -*-
"""
Created on Fri May  6 00:53:17 2022

@author: Robert J McGinness
"""

from game_network import ServerClient
from game_network import HTTPCommsModule
from config import Config

class MainMenu:
    def __init__(self, config: Config, comms: HTTPCommsModule, client: ServerClient) -> None:
        self.__config = config
        self.__comms = comms
        self.__client = client
        self.__exit: bool = False
        self.__request = None
        self.__render()
    
    @property
    def exit_requested(self) -> bool:
        return self.__exit
    
    def __render(self) -> None:
        self.__comms.render_file(self.__config.MENU_FILE)
        self.__request = self.__comms.read() # Read request from rendered menu
        if 'exit' in self.__request:
            self.__exit = True