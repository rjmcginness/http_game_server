# -*- coding: utf-8 -*-
"""
Created on Mon May 16 13:36:34 2022

@author: Robert J McGinness
"""

from typing import Dict

from rjm_gaming.game_network import HTTPRequest
from rjm_gaming.game_network import parse_query
from config import Config


class Registry:
    def __init__(self, config: Config) -> None:
        self.__config = config
        self.__reqistry_html = None
        self.__login_html = None
        self.__registrants: Dict = self.__get_registrants(config)
        
        with open(config.REGISTRY_PAGE, 'rt') as registry_file:
            self.__reqistry_html = registry_file.read().strip()
    
        with open(config.LOGIN_FORM, 'rt') as login_file:
            self.__login_html = login_file.read().strip()
    
        
    def process(self, request: HTTPRequest) -> str:

        query_input = parse_query(request.request_type, 'input=').lower()

        # user information submitted for registration
        if query_input == 'register':
            name, password = self.__build_registrant(request)   
            if name not in self.__registrants: # user does not exist
                self.__add_registrant(name, password)
                return self.__build_login_page(request)
            else:
                return self.__build_bad_registry(request)
        
        # user cancelled registration process
        if query_input == 'exit':
            return self.__build_login_page(request)
        
        # return the registration page
        return self.__build_registration_page(request)
    
    def __get_registrants(self, config: Config) -> Dict:
        registrants = {}
        for user in open(self.__config.USER_DB, 'rt'):
            user_pass = user.split('~')
            registrants[user_pass[0].strip()] = user_pass[1].strip()
        
        return registrants
    
    def __add_registrant(self, name: str, password: str) -> None:
        self.__registrants[name] = password
        with open(self.__config.USER_DB, 'a') as registry:
            registry.write(name + '~' + password + '\n')
    
    def __build_login_page(self, request: HTTPRequest) -> str:
        return request.session.form_insert(self.__login_html + '\r\n')
    
    def __build_registration_page(self, request: HTTPRequest) -> str:
        return request.session.form_insert(self.__registry_html + '\r\n')
    
    def __build_bad_registry(self, request: HTTPRequest) -> str:
        output = self.__registry_html.replace('</body>', '<br/><br/><h3>User Exists</h3></body>')
        return request.session.form_insert((output))
        
        
        
        