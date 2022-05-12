# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 13:22:11 2022

@author: Robert J McGinness
"""

from abc import ABC
from abc import abstractmethod
from typing import Union
from typing import Type
from typing import List
from importlib import import_module

class GameCommsError(Exception):
    pass

# class CommsModule(ABC):
#     def __init__(self, in_: Any, out: Any):
#         self.__in: in_
#         self.__out: out
    
#     @property
#     def in_(self) -> Any:
#         return self.__in
    
#     @property
#     def out(self) -> Any:
#         return self.__out
    
#     @abstractmethod
#     def write(self, data: Any) -> None:
#         ...
     
#     @abstractmethod
#     def read(self) -> Any:
#         ...
    
#     @abstractmethod
#     def close(self) -> None:
#         ...

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
    ######consider parameter for read, write, or append
    '''significantly changed from version 1.0'''
    def __init__(self, init_path, raw=True) -> None:
        super().__init__(init_path)
        self.__raw = raw
        self.__data = None
        self.initialize()
    
    def initialize(self) -> None:
        '''Reads the entire file and stores in __data attribute'''
        open_flag = 'rb' if self.__raw else 'rt'
        # with open(self.path, open_flag) as fle:
        #     self.__data = fle.read()
        
        self.__data = []
        
        for line in open(self.path, open_flag):
            self.__data.append(line)

    @property
    def data_lines(self) -> List[str]:
        return self.__data

    @property
    def data(self) -> Union[bytes, str]:# may not work with bytes
        return '\n'.join(self.__data)

class ClassLoader:
    @staticmethod
    def load_class(class_name: str,
                   module_name: str,
                   package_name: str = '.') -> Type:
        module_type = import_module(module_name, package_name)
        return getattr(module_type, class_name)

    
if __name__ == '__main__':
    file_access = FileDataAccess('../static/mainmenu.html')
    print(file_access.data)