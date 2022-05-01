# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 15:13:44 2022

@author: Robert J McGinness
"""

# if '/Users/robertjmcginness/src/pyth' not in path:
#     path.append('/Users/robertjmcginness/src/pyth')
    
# path.remove('/Users/robertjmcginness/src/pyth/rjm_gaming')

# if '/Users/robertjmcginness/src/pyth/rjm_gaming' not in path:
#     path.append('/Users/robertjmcginness/src/pyth/rjm_gaming')

import game_engine
import game_utilities
import sys



if __name__ == '__main__':
    comms = game_utilities.TerminalCommsModule()
    file_access = game_utilities.FileDataAccess('./game_init.i')
    file_access.initialize()
    engine = game_engine.Engine(comms, file_access)
    
    print("Welcome to the RJM Gaming Metaverse.")
    
    while True:
        try:
            print('\n' + 'MENU'.center(30, '*'))
        
            game_map = {}
            for i, game_meta in enumerate(engine.get_games()):
                print(game_meta['name'] + '\t\t' + str(i + 1))
                game_map[str(i+1)] = game_meta['name']
                
            print("\n\nType the game number and press enter to play")
            print("or press ctrl+c or cmd+c at any time to quit")
            
            game_selection = input()
                                   
            print('\nStarting ' + game_map[game_selection])
            engine.run_game(game_map[game_selection])
        except KeyError:
            print("Invalid game selection.")
            continue
        except KeyboardInterrupt:
            print("Thank you for playing!\nExiting...")
            break

    sys.exit()