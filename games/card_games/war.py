# -*- coding: utf-8 -*-
"""
Created on Wed Apr 20 14:13:11 2022

@author: Robert J McGinness
"""
# from sys import path as syspath

# if '~/src/games' not in syspath:
#     syspath.append('~/src/games')

# if '../../rjm_gaming' not in syspath:
#     syspath.append('../../rjm_gaming')

from sys import exit
from typing import List
from typing import Tuple
from card_model import CardGame
from card_model import CardPlayer
from card_model import StandardDeck
from card_model import Card
from game_model import GameResult
from game_engine import CommsModule
from game_engine import GameInvalidError


class War(CardGame):
    def __init__(self, name: str, comms: CommsModule, players: List[CardPlayer] = []):
        if not players:
            player1 = CardPlayer('1', 'Player1')
            player1.isdealer = True
            players = [player1, CardPlayer('2', 'Player2')]
        super().__init__('War',
                         comms,
                         StandardDeck(), 
                         players)
        
        # self.__play: Dict = {player.name + player.player_id: None \
        #                      for player in self._Game__players}
    
    def start_game(self) -> None:
        if not self._CardGame__deck:
            raise GameInvalidError
        self._CardGame__deck.shuffle()
        self.deal()
        
        self._Game__comms.display({'introduction': self._Game__players})
        input_data = self._Game__comms.read()# to pause
        
        for result in self.play_round():
            self._Game__add_result(result)
            self._Game__comms.display(result)
            input_data = self._Game__comms.read()########check for quit
        
        #send winner to display: winner is the one with cards
        self._Game__comms.display({'game_over' : self._Game__players[0] \
                                   if self._Game__players[0].card_count else \
                                   self._Game__players[1]})
        
    def deal_cards(self):
        
        dealer: CardPlayer = None
        player2: CardPlayer = None
        
        for player in self._Game__players:
            if player.isdealer:
                dealer = player
                continue
            player2 = player
        
        while self._CardGame__deck: #will be False if __deck is empty
            player2.take_card(self._CardGame__deck.pop())
            dealer.take_card(self._CardGame__deck.pop())

    def play_round(self) -> GameResult:
        '''Returns the results of each round of play
           Implemented as a generator, as the game can only be played once.
           
           return type: game_engine.GameResult
        '''
        
        player1, player2 = self._Game__players
        while player1.card_count and player2.card_count:#each player has at least 1 card
               
            p1_card = player1.play_card()
            p2_card = player2.play_card()
            
            if p1_card > p2_card:
                player1.add_cards_bottom([p2_card, p1_card])
                yield GameResult(player1, player2, 
                                 game_over=not (player1.card_count and player2.card_count),
                                 winner=player1,
                                 results={'player1' : (p1_card,),
                                         'player2' : (p2_card,)})
            elif p2_card > p1_card:
                player2.add_cards_bottom([p1_card, p1_card])
                yield GameResult(player1, player2, 
                                 game_over= not (player1.card_count and player2.card_count),
                                 winner=player2,
                                 results={'player1' : (p1_card,),
                                         'player2' : (p2_card,)})
            else:
                yield self.__process_tie(player1, player2, p1_card, p2_card)
        
        return #stops generator

    def __process_tie(self, player1: CardPlayer, player2: CardPlayer,
                                  p1_card: Card, p2_card: Card) -> GameResult:
        player1_play = (p1_card,)#create a tuple of cards
        player2_play = (p2_card,)
        
        while player1.card_count & player2.card_count:#both players still have a card
            player1_play, player2_play = self.__get_next_play(player1,
                                                              player2,
                                                              player1_play,
                                                              player2_play)
            
            if not (player1.card_count and player2.card_count):#someone has 0 cards
                break
            
            player1_play, player2_play = self.__get_next_play(player1,
                                                              player2,
                                                              player1_play,
                                                              player2_play)
            
            if not (player1.card_count and player2.card_count):#someone has 0 cards
                break
            
            if not (player1_play[-1] == player2_play[-1]): # compare last cards
                break
        
        return self.__determine_winner(player1, player2, 
                                                   player1_play, player2_play)
    
    def __get_next_play(self, player1: CardPlayer,
                                            player2: CardPlayer,
                                            player1_play: Tuple,
                                            player2_play: Tuple) -> Tuple:
        
        p1_card = player1.play_card()
        p2_card = player2.play_card()
        
        player1_play += (p1_card,) #concatenate new card as tuple to player1_play
        player2_play += (p2_card,)
        
        return player1_play, player2_play
    
    def __determine_winner(self, player1: CardPlayer,
                                   player2: CardPlayer,
                                   player1_play: Tuple,
                                   player2_play: Tuple) -> GameResult:
        
        #last card in play is compared
        p1_card = player1_play[-1]
        p2_card = player2_play[-1]
        
        winner = None
        
        if p1_card == p2_card:
            if player1.card_count == 0:#player with 2 cards loses
                winner = player2
            else:
                winner = player1
        elif p1_card > p2_card:
            winner = player1
        else:
            winner = player2
            
        winner.add_cards_bottom(list(player1_play + player2_play))
        
        game_over = not (player1.card_count and player2.card_count)
                
        return GameResult(player1, player2, 
                                        game_over=game_over,
                                        winner=winner,
                                        results={'player1' : player1_play,
                                                'player2' : player2_play})
        
if __name__ == '__main__':
    exit()
    # from game_engine import TerminalCommsModule
    
    # comms = TerminalCommsModule()
    # g = War('War', comms)
    # g.start_game()
    
    