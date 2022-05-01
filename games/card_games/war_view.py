# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 13:56:44 2022

@author: rmcginness
"""

# from sys import path
from typing import Any
from sys import exit

# if '/Users/robertjmcginness/src/pyth' not in path:
#     path.append('/Users/robertjmcginness/src/pyth')
    
# path.remove('/Users/robertjmcginness/src/pyth/rjm_gaming')

# if '/Users/robertjmcginness/src/pyth/rjm_gaming' not in path:
#     path.append('/Users/robertjmcginness/src/pyth/rjm_gaming')

    
# print(path)


from game_view import GameView
from game_utilities import CommsModule
from game_model import GameResult
from card_model import Card



class WarTerminalView(GameView):
    def __init__(self, comms: CommsModule, view_id: str = '') -> None:
        super().__init__('War', comms, view_id)
        
    def put(self, data: Any) -> Any:
        if data == '':
            data = 'enter'
        
        if data.lower() == 'q':
            data = 'quit'
        
        return {'input' : data}
        
    def render(self, data: Any) -> Any:
        if isinstance(data, GameResult):
            return self.render_result(data)
        
        try:
            return self.introduction(data['introduction'])
        except KeyError:
            pass
        
        try:
            return self.game_over(data['game_over'])
        except KeyError:
            pass
        
        return '' # render nothing
        
    def render_result(self, result: GameResult) -> Any:
        
        player1_play = result['player1']
        player2_play = result['player2']
        
        p1_card = player1_play[0]
        p2_card = player2_play[0]
        
        card_count = len(player1_play)
        
        output_str = self.__render_players(result.players) + '\n'
        
        output_str += self.__render_card(p1_card, p2_card)#show these face up
        
        #only need to check length of player1_play as player2_play length is same
        if card_count == 1: 
            output_str += '\n' + (result.winner.name + \
                                            ' wins battle!').center(45) + '\n'
            if not result.game_over:
                return output_str + self.__render_stats(result.players) + \
                                            '\npress enter for next round\n\n'
            return output_str
        
        self._GameView__comms.write(output_str + \
                                    '\nDraw. Press enter to continue play')
        self._GameView__comms.read_input()
        
        for card_idx in range(1, card_count - 1):#STARTS AT 1 (ONE)
            output_str += self.__render_card(player1_play[card_idx],
                                             player2_play[card_idx],
                                             face_up=(card_idx % 2 == 0))
            if card_idx % 2 == 0:
                self._GameView__comms.write(output_str + \
                                            '\npress enter to play card')
            else:
                self._GameView__comms.write(output_str + \
                                            '\npress enter to continue play')
            self._GameView__comms.read_input()
                
        #last card: determines winner index = -1, always face up
        output_str += self.__render_card(player1_play[-1],
                                             player2_play[-1],
                                             face_up=True)
        
        output_str += '\n' + (result.winner.name + \
                                        ' wins battle!').center(45) + '\n'
        
        if not result.game_over:
            return output_str + self.__render_stats(result.players) + \
                                        '\npress enter for next round\n\n'
        return output_str
                
    def __render_card(self, p1_card: Card, p2_card: Card, face_up=True) -> str:
        
        if face_up:
            return str(p1_card).center(20) + '\t\t' + \
                                            str(p2_card).center(20) + '\n'
        
        return '*********'.center(20) + '\t\t' + \
                                                '*********'.center(20) + '\n'
    
    def introduction(self, data: Any) -> str:
        
        return '\n' + "Welcome to War!".center(45) + \
               '\n\n' + 'Press enter to start\n\n'
    
    def __render_stats(self, data: Any) -> str:
        player1, player2 = data
        output_str = '\n\tCards Remaining: '
        output_str += player1.name + ' ' + str(player1.card_count)
        output_str += '\t'
        output_str += player2.name + ' ' + str(player2.card_count)
        output_str += '\n'
        
        return output_str
    
    def __render_players(self, data: Any) -> str:
        player1, player2 = data
        p1_name = str(player1.name + ' (' + player1.player_id + ')').center(20)
        p2_name = str(player2.name + ' (' + player2.player_id + ')').center(20)
        
        return p1_name + '\t\t' + p2_name + '\n'
    
    def game_over(self, data:Any) -> str:
        '''Uses duck typing as a CardPlayer object is sent by the game
           The CardPlayer object sent represents the winner
        '''
        return 'The War has Ended!'.center(45) + '\n\n' + \
                                                    data.name.center(45) + \
                                                    '\n' + 'Wins'.center(45) +\
                                                    '\n\n'

if __name__ == '__main__':
    exit()
        
#     from game_utilities import TerminalCommsModule
    
#     war_view = WarTerminalView(TerminalCommsModule())
    
#     print(war_view.introduction({'hi':'1'}))