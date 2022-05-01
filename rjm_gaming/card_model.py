# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 09:28:23 2022

@author: Robert J McGinness
"""

from enum import Enum
from typing import List
from typing import Tuple
from typing import Dict
from abc import abstractmethod
from random import sample
from game_model import Game
from game_model import Player
from game_model import GameResult
from game_engine import CommsModule
from typing import Optional

class Suits(Enum):
    HEART = 'heart'
    DIAMOND = 'diamond'
    CLUB = 'club'
    SPADE = 'spade'

class Ranks(Enum):
    ACE = 1
    KING = 13
    QUEEN = 12
    JACK = 11
    TEN = 10
    NINE = 9
    EIGHT = 8
    SEVEN = 7
    SIX = 6
    FIVE = 5
    FOUR = 4
    THREE = 3
    TWO = 2

class AceHighRanks(Enum):
    ACE = 14
    KING = 13
    QUEEN = 12
    JACK = 11
    TEN = 10
    NINE = 9
    EIGHT = 8
    SEVEN = 7
    SIX = 6
    FIVE = 5
    FOUR = 4
    THREE = 3
    TWO = 2
    
class Card:
 
    def __init__(self, suit: str, rank: str, value: str) -> None:
        self.__suit = suit
        self.__rank = rank
        self.__rank_value = value
    
    @property 
    def suit(self) -> str:
        return self.__suit
    
    @property 
    def rank(self) -> str:
        return self.__rank
    
    @property 
    def rank_value(self) -> int:
        return self.__rank_value
    
    def __repr__(self) -> str:
        return self.__suit + ' ' + self.__rank
    
    def __eq__(self, card2) -> bool:
        return self.__rank_value == card2.rank_value
    
    def __gt__(self, card2) -> bool:
        return self.__rank_value > card2.rank_value

    def __lt__(self, card2) -> bool:
        return self.__rank_value < card2.rank_value
    
    @property
    def encoding(self) -> Dict:
        return {'_meta':'_Card',
                'suit':self.__suit,
                'rank':self.__rank,
                'value':self.__value}

class Deck(List[Card]):
    
    def __init__(self) -> None:
        self.create()
    
    @abstractmethod 
    def create(self) -> None:
        ...
    
    def shuffle(self) -> None:
        shuffled_deck = sample(self, len(self))
        self.clear()
        self += shuffled_deck
 
    def get_next_card(self) -> Card:
        return self.pop()
    
    def peek_next_card(self) -> Card:
        return self[-1]
    
    def return_card(self, card) -> None:
        self.append(card)
    
    def deal(self, number) -> [List[Card]]:
        return [self.pop() for _ in range(number)]

class StandardDeck(Deck):
    def __init__(self) -> None:
        super().__init__()
    
    def create(self) -> None:
        self += [Card(s.name, r.name, r.value) for s in Suits for r in AceHighRanks]
        
class CardPlayer(Player):
    ''' Subclass of Player
        Additional Attributes: hand, score, isdealer
    '''
    def __init__(self, player_id: str, 
                       name: str, 
                       experience: Optional[int] = None) -> None:
        super().__init__(player_id, name, experience)
        self.__hand: List[Card] = []
        self.__score: int = 0
        self.__isdealer = False
    
    def take_card(self, card: Card) -> None:
        self.__hand.append(card)
        
    def take_cards(self, cards: List[Card]) -> None:
        self.__hand += cards
    
    def add_card_bottom(self, card: Card) -> None:
        self.__hand.insert(0, card)
    
    def add_cards_bottom(self, cards: List[Card]) -> None:
        self.__hand = cards + self.__hand
    
    def play_card(self, card_number: int = -1) -> Card:
        card = self.__hand[card_number]  #raises Index Error if no such card_number
        del self.__hand[card_number] #removes card from hand
        return card
    
    def play_next_cards(self, number: int = 1) -> Tuple[Card]:
        return tuple(self.play_card() for _ in range(number))
    
    @property 
    def isdealer(self) -> bool:
        return self.__isdealer 
    
    @isdealer.setter 
    def isdealer(self, deals: bool) -> None:
        self.__isdealer = deals
    
    @property 
    def card_count(self) -> int:
        return len(self.__hand)
    
    @property
    def encoding(self) -> Dict:
        enc = super.encoding
        enc['_meta'] = '_CardPlayer'
        return enc.update({'hand':self.__hand,
                           'score':self.__score,
                           'dealer':self.__isdealer})
        
class CardGame(Game):
    def __init__(self, name: str,
                 comms: CommsModule,
                 deck: Deck,
                 players: List[CardPlayer] = []) -> None:
        super().__init__(name, comms, players)
        self.__deck = deck
        self.__deal_clockwise = True
        self.__dealer_index: Optional[int] = self.__get_dealer_index()
    
    def __get_dealer_index(self) -> Optional[Player]:
        for idx in range(self.player_count):
            if self._Game__players[idx].isdealer:
                return idx
        return None
    
    @property 
    def dealer(self) -> CardPlayer:
        return self._Game__players[self.__dealer_index]
    
    @dealer.setter 
    def dealer(self, player: Optional[Player]) -> None:
        try:
            self._Game__players[self.__dealer_index].isdealer = False
            self.__dealer_index = None
            new_dealer_idx = self.isplaying(player)
            self._Game__players[new_dealer_idx].isdealer = True
        except (IndexError, AttributeError, ValueError):
            self.__dealer_index = None
        
    def change_dealer(self, dist: int = 1, 
                          dir_clockwise: bool = True, 
                          player: CardPlayer = None, 
                          rand: bool = False) -> None:
        
        try:
            self._Game__players[self.__dealer_index].isdealer = False
            self.__dealer_index = (self.__dealer_index + 1) % self.player_count
            self._Game__players[self.__dealer_index].isdealer = True
        except (IndexError, AttributeError):
            self.__dealer_index = None
    
    @property
    def deal_is_clockwise(self) -> bool:
        return self.__deal_clockwise
    
    @deal_is_clockwise.setter 
    def deal_is_clockwise(self, clockwise: bool) -> None:
        self.__deal_clockwise = clockwise
    
    def clone_deck(self) -> List[Card]:
        return self.__deck[:]
    
    @abstractmethod
    def deal_cards(self) -> None:
        ...
    
    def deal(self) -> None:
        self.deal_cards()
    
    @abstractmethod 
    def play_round(self) -> 'GameResult':
        ...

    
if __name__ == '__main__':
    sd = StandardDeck()
    c1 = sd.peek_next_card()
    
    for card in sd:
        if c1 == card:
            print(c1.rank_value, card.rank_value)
        if c1 < card:
            print(c1.rank_value, card.rank_value)
    
    

        