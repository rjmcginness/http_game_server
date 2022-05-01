#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  1 01:05:29 2022

@author: robertjmcginness
"""

import json
from typing import Dict
from game_model import GameResult
from game_model import Player

class PlayerEncoder(json.JSONEncoder):
    def default(self, obj: object) -> Dict:
        if isinstance(obj, Player):
            return obj.encoding
        return super().default(obj)

class GameResultEncoder(json.JSONEncoder):
    def default(self, obj: object) -> Dict:
        if isinstance(obj, GameResult):
            return obj.encoding
        return super.default(obj)
      
    
if __name__ == '__main__':
    p1 = Player('1', 'Pleyer One')
    gr = GameResult(*[p1, Player('2', 'Player Two',2)],
                      game_name='War',
                      winner=p1,
                      results={'blah':'blah'})
    print(gr)
    print()
    print('JSON')
    json_data = json.dumps(gr, cls=GameResultEncoder)
    print(json_data)
    data = json.loads(json_data, object_hook=GameResult.decode)
    print(type(data),data)
    print()
    json_data = json.dumps(p1, cls=PlayerEncoder)
    print(json_data)
    p1 = json.loads(json_data, object_hook=Player.decode)
    print(type(p1), p1)