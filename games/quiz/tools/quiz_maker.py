# -*- coding: utf-8 -*-
"""
Created on Tue May 17 10:07:26 2022

@author: Robert J McGinness
"""

import json
import time
from typing import List
from typing import Tuple
from string import ascii_lowercase

from quiz import Question

class AppExit(Exception):
    pass

class QuizMaker:
    def __init__(self) -> None:
        self.__quiz_name = None
        self.__question_buffer = []
    
    @property
    def quiz_name(self) -> str:
        return self.__quiz_name

    @quiz_name.setter
    def quiz_name(self, name) -> None:
        self.__quiz_name = name
    
    @property
    def questions(self) -> Tuple:
        return tuple(self.__question_buffer)
    
    @property
    def question_count(self) -> int:
        return len(self.__question_buffer)
    
    @property
    def isempty(self) -> bool:
        '''Returns True if no questions, False otherwise.'''
        return not bool(self.__question_buffer)
    
    def clear(self) -> None:
        self.__quiz_name = None
        self.__question_buffer.clear()
    
    def save_as(self, quiz_file_name: str) -> None:
        '''WARNING THIS WILL OVERWRITE A FILE OF NAME QUIZ_FILE_NAME'''
        # quiz files will not have a file type (just because: not really).
        # This is so I can use the file_nane as the quiz name)
        try:
            dot_idx = quiz_file_name.index('.')
            quiz_file_name = quiz_file_name[:dot_idx]
        except ValueError:
            pass
        
        # save in the directory above this one
        with open('../' + quiz_file_name, 'wt') as quiz_file:
            for question in self.__question_buffer:
                #save file as json encoding
                quiz_file.write(json.dumps(question.encoding) + '\n')
        
    def load_quiz(self, quiz_file_name: str) -> None:
        self.clear()
        if not quiz_file_name:
            return
        
        self.__quiz_name = quiz_file_name
        
        # quiz files are stored in directory above this
        for question in open('../' + quiz_file_name):
            question = json.loads(question, object_hook=Question.decode)
            self.__question_buffer.append(question)
            
    def add_question(self, question: str,
                           answer: str,
                           choices: List[str],
                           question_type: str='multiple_choice') -> None:
        
        new_question = self.__build_question(question, answer, choices)
        
        self.__question_buffer.append(new_question)
    
    def replace_question(self, question_number: int,
                               question: str,
                               answer: str,
                               choices: List[str],
                               question_type: str='multiple_choice') -> None:
        try:
            del self.__question_buffer[question_number]
            new_question = self.__build_question(question, answer, choices)
            self.__question_buffer.insert(question_number, new_question)
        except IndexError:
            return
    
    def remove_question(self, question_number: int) -> None:
        try:
            del self.__question_buffer[question_number]
        except IndexError:
            return
        
    def __build_question(self, question: str,
                               answer: str,
                               choices: List[str],
                               question_type: str='multiple_choice') -> Question:
        
        return Question(question, answer, str(time.time()), choices,
                                                            'multiple_choice')
        


def show_introduction() -> None:
    '''Prints the output to terminal for the introduction for this tool'''
    
    horiz_rule = '-'*30
    
    output = 'Welcome to QuizMaker!\n' + horiz_rule + '\n\n'
    output += 'Select an option:' + '\n'
    output += '1. New Quiz\n2. Load Quiz\n3. Modify Quiz\n4. Show Questions\n5. Save\n6. Exit'
    
    print(output)
    
def get_question_input(question_part: str) -> str:
    ''' Asks user for input for part of a question, based on 
        question_part argument
    '''
    data = ''
    while not data  or data.isspace():
        data = input(f"Enter {question_part}: ").strip()
    
    return data
        
def build_new_questions(quiz_maker: QuizMaker) -> None:
    
    question_tuple = ()
    # QUESTION ENTRY LOOP
    while True:
        
        question_tuple = build_new_question(quiz_maker)
        quiz_maker.add_question(*question_tuple)
        # print(f'Enter question {quiz_maker.question_count + 1}') 
        
        # option =  input('Press enter to continue or type c and ' + \
        #                 'press enter to stop adding questions:')
        # # if option.strip().lower() == 'c':
        #     # exit loop to main loop
        #     break
        
        # # enter data for new question in pieces
        # question = get_question_input("question")
        # answer = get_question_input("answer")
        
        # # choices will appear in question in order entered
        # choices = []
        # choices.append(get_question_input("choice 1"))
        # choices.append(get_question_input("choice 2"))
        # choices.append(get_question_input("choice 3"))
        # choices.append(get_question_input("choice 4"))
        
        # ######NOT POSSIBLE TO ENTER ANYTHING BUT MULTIPLE CHOICE RIGHT NOW
        
        # quiz_maker.add_question(question, answer, choices)

def build_new_question(quiz_maker: QuizMaker) -> Tuple:
    print(f'Enter question {quiz_maker.question_count + 1}') 
    
    option =  input('Press enter to continue or type c and ' + \
                    'press enter to stop adding questions:')
    
    if option.strip().lower() == 'c':
        # exit loop to main loop
        return ()
    
    # enter data for new question in pieces
    question = get_question_input("question")
    answer = get_question_input("answer")
    
    # choices will appear in question in order entered
    choices = []
    choices.append(get_question_input("choice 1"))
    choices.append(get_question_input("choice 2"))
    choices.append(get_question_input("choice 3"))
    choices.append(get_question_input("choice 4"))
    
    ######NOT POSSIBLE TO ENTER ANYTHING BUT MULTIPLE CHOICE RIGHT NOW
    
    return question, answer, choices

def show_questions(quiz_maker: QuizMaker) -> None:
    
    print(f'\nQuestions for {quiz_maker.quiz_name}:')
    # using some duck typing (do not know actual type of question)
    for i, question in enumerate(quiz_maker.questions):
        print(f'\tQuestion {i+1}.')
        print(f'\t\tQuestion: {question.question}')
        print(f'\t\tAnswer: {question.answer}')
        print('\t\tChoices: ')
        for j, choice in zip(ascii_lowercase, question.choices):
            print(f'\t\t\t{j}. {choice}')
    
    input("\nPress enter to continue\n") # block so user can view questions

def run_modify(quiz_maker: QuizMaker) -> None:
    
    option = ''
    while not option or option.isspace(): # loop until good input
        print('\nOptions:\n1. Add Question\n2. Replace Question\n3. Delete Question')
        option = input('Enter selection: ').strip().lower()
    
    if option in ['add', 'a', '1', '1.']:
        build_new_question(quiz_maker)
        return
    
    if option in ['replace', 'r', 'rep', '2', '2.']:
        question_number = input('Enter question number to modify: ')
        question_tuple = build_new_question(quiz_maker)
        quiz_maker.replace(question_number, *question_tuple)

    if option in ['delete', 'd', 'del', '3', '3.']:
        question_number = input('Enter question number to modify: ')
        quiz_maker.remove_question(question_number)

def save_quiz(quiz_maker: QuizMaker) -> None:
    ''' If the quiz has questions, double checks with user,
        then saves the quiz to a file with the name of quiz.
    '''
    if not quiz_maker.isempty:
        option = input("Would you like to save your progress? ").strip().lower()
        if option in ('yes', 'y', 'save'):
            quiz_maker.save_as(quiz_maker.quiz_name)
            print(f"Quiz saved as quiz/{quiz_maker.quiz_name}\n")
    print("Quiz has no questions to save\n")
    
def main():
    from sys import exit
    
    quiz_maker = QuizMaker()
    try:
        while True: # MAIN LOOP
            show_introduction()
            user_choice = input("Enter selection: ").strip().lower()
            
            # see, if user wants to make a new quiz
            if user_choice in ['new quiz', 'new', 'quiz', '1', '1.']:
                quiz_maker.clear() # make sure there is no remaining data in quiz maker
                
                quiz_name = ''
                try:
                    while not quiz_name or quiz_name.isspace():
                            quiz_name = input('Please enter the name of the quiz' + \
                                          ' (ctrl+c to quit): ').strip()
                except KeyboardInterrupt:
                    continue
                    
                quiz_maker.quiz_name = quiz_name
                build_new_questions(quiz_maker)
                
                continue # continue main loop
            
            # see, if user selected save
            if user_choice in ['load', 'l', '2', '2.']:
                quiz_file_name = get_question_input('quiz file name to load')
                quiz_maker.load_quiz(quiz_file_name)
                continue
            
            # see, if user selected modify
            ######ONLY ALLOWS APPENDING NEW QUESTIONS RIGHT NOW
            if user_choice in ['modify', 'mod', 'm', '3', '3.']:
                if not quiz_maker.quiz_name:
                    quiz_file_name = get_question_input('quiz file name to load')
                    quiz_maker.load_quiz(quiz_file_name)
                    
                show_questions(quiz_maker)
                
                run_modify(quiz_maker)
                
                continue
            
            # see, if user selected save
            if user_choice in ['show', 'sh', '4', '4.']:
                show_questions(quiz_maker)
                continue
            
            # see, if user selected save
            if user_choice in ['save', 's', '5', '5.']:
                save_quiz(quiz_maker)
                continue
            
            # see, if user wants to exit
            if user_choice in ('exit', 'e', 'q', 'quit', 'close', '6', '6.'):
                save_quiz(quiz_maker)
                raise AppExit()
                
    except (KeyboardInterrupt, AppExit):
        print("\nThank you for choosing the RJM Gaming Metaverse!")
        exit()
        
if __name__ == '__main__':
    main()
    
    