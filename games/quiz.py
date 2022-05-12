# -*- coding: utf-8 -*-
""" 
Created on Tue May 10 13:59:48 2022

@author: Robert J McGinness
"""
from __future__ import annotations

import json
from typing import Optional
from typing import List
from typing import Dict
from typing import Type
from typing import Any
from random import sample

from rjm_gaming.game_base import Game
from rjm_gaming.game_base import GameResult
from rjm_gaming.game_base import Player


class Question:
    def __init__(self, question: str,
                 answer: str,
                 q_id: str,
                 choices: Optional[List[str]] = None,
                 question_type: Optional[str] = None) -> None:
        self.question = question
        self.answer = answer
        self.q_id = q_id
        self.choices = choices
        self.question_type = question_type
    
    def __eq__(self, q2) -> bool:
        return (self.question == q2.question and \
                    self.answer == q2.answer and \
                    self.q_id == q2.q_id)
    @property
    def encoding(self) -> Dict:
        ''' This encodes Question instances as a
            dictionary (key:value pairs).  This allows
            it to be converted to a string by the json
            module.  The string, thus created, can be
            converted back to a Question object
        '''
        return {'_meta':{'module': self.__module__,
                         'cls': self.__class__.__name__},
                'question': self.question,
                'answer': self.answer,
                'id': self.q_id,
                'choices': self.choices,
                'type': self.question_type}
    
    @classmethod
    def decode(cls: Type, obj: object) -> "Question":
        ''' This can be used with json module to convert 
            a string (that has a key:value pair format)
            to a Question instance.
            In essence this make the Question class a
            factory for instances of itself.
        '''
        return_object = obj
        try:
            if obj['_meta']['cls'] == cls.__name__:
                return_object = cls(obj['question'],
                                    obj['answer'],
                                    obj['id'],
                                    obj['choices'],
                                    obj['type'])
        except KeyError:
            return_object = obj
        
        return return_object

    # def __repr__(self) -> str:
    #     return self.encode()

class Answer:
    def __init__(self, answer: Optional[Any] = None) -> None:
        self.__value = answer
    
    @property
    def value(self) -> Any:
        return self.__value
    
    @value.setter
    def value(self, val: Any) -> None:
        self.__value = val

class QuizSubmission:
    def __init__(self, question: Question,
                       answer: Optional[Answer] = None) -> None:
        self.__question = question
        self.answer = answer
        
    
    @property
    def question(self) -> Question:
        return self.__question
    
    @property
    def answer(self) -> Answer:
        return self.__answer
    
    @answer.setter
    def answer(self, ans: Any) -> None:
        self.__answer = ans
        self.__isanswered = True if ans is not None else False
        self.__iscorrect = (self.__isanswered and \
                            (self.__answer.value == self.__question.answer))
    
    @property
    def isanswered(self) -> bool:
        return self.__isanswered

    @property
    def iscorrect(self) -> bool:
        return self.__iscorrect
    
    
            
class Quiz(Game):
    def __init__(self, name: str, player: Player, quiz_file: str) -> None:
        super().__init__(name, [player])
        self.__quiz_file = quiz_file
        self.__questions = []
        self.__load_quiz()
        self.__quiz_submissions = self.__initialize()
        
        self.__current_submission = self.__quiz_submissions[0]
    
        
    def __load_quiz(self) -> None:
        '''Load and deserialize Questions from quiz file'''
        for question_data in open(self.__quiz_file, 'rt'):
            self.__questions.append(self.__parse_question(question_data.strip()))
         
    def __parse_question(self, question_data: str) -> Question:
        '''Deserialize Question object from json data'''
        return json.loads(question_data, object_hook=Question.decode)
    
    def __initialize(self) -> List[QuizSubmission]:
        ''' Create and store QuizSubmission objects randomly
            arranged from Questions.  Answers are all None.
        '''
        submissions = []
        for i, question in enumerate(sample(self.__questions, 
                                            len(self.__questions))):
            question.q_id = i  
            submissions.append(QuizSubmission(question, None))
            
        return submissions
         
    def _next_result(self, **kwargs) -> GameResult:
        
        command = kwargs['input'].lower()
        
        # process start of new quiz
        if command == 'start':
            return GameResult(self.players,
                              game_name='Quiz',
                              result_id=1, 
                              question=self.__current_question.question,
                              prev_question=None,
                              next_question=self.__next_submission())
        
        results = {} # additional key-value pairs for results
        game_over = False
        
        # process submission of quiz
        if command == 'submit':
            answer = kwargs['answer']
            self.__current_submission.answer = Answer(answer)
            # results['game_over'] = True
            game_over = True
            # results['results'] = tuple(enumerate(self.__quiz_submissions))
            results['num_correct'] = len(list(filter(q for q in \
                                                     self.__quiz_submissions \
                                                     if q.iscorrect)))
            results['percent'] = f"{100*results['num_correct']/len(self.__quiz_submissions)}%"
            results['questions'] = tuple(self.__quiz_submissions)

        # process a submitted answer
        if command == 'answer':
            answer = kwargs['answer']
            self.__current_submission.answer = Answer(answer)
            self.__current_submission = self.__next_submission()
        
        # process a skipped answer
        if command == 'skip':
            self.__current_submission.answer = None
            self.__current_submission = self.__next_submission()
        
        # process going back to the last question
        if command == 'back':
            answer = kwargs['answer']
            self.__current_submission.answer = Answer(answer)
            self.__current_submission = self.__prev_submission()
            
        return GameResult(self.players,
                          game_name='Quiz',
                          result_id=len(self.results) + 1,
                          game_over=game_over,
                          question_num=self.__current_submission.question.q_id,
                          question=self.__current_submission.question,
                          answer=self.__current_submission.answer.value,
                          prev_question=self.__prev_submission(),
                          next_question=self.__next_submission(),
                          **results)
            
    def __prev_submission(self) -> QuizSubmission:
        try:
            idx = self.__quiz_submissions.index(self.__current_submission)
            
            return self.__quiz_submissions[idx-1]
        except IndexError:
            return None
    
    def __next_submission(self) -> QuizSubmission:
        try:
            idx = self.__quiz_submissions.index(self.__current_submission)
            
            return self.__quiz_submissions[idx + 1]
        except IndexError:
            return None
        
if __name__ == '__main__':
    # from sys import exit
    # exit()
    #######################################################
    ######TEST LOADING QUIZ
    
    #######################################################
    ######TEST RUNNING GAME AND GENERATING A GAMERESULT
    
    import json
    import time
    
    q = Question("Where do sharks live?",
                 'ocean',
                 ['desert', 'lake', 'ocean', 'maountain'],
                 str(time.time()),
                 'multiple choice')
    
    json_data = json.dumps(q.encoding)
    print(json_data)
    
    
    
    # import time
    # q = Question("Where do sharks live?",
    #              'ocean',
    #              ['desert', 'lake', 'ocean', 'maountain'],
    #              time.ctime(),
    #              'multiple choice')
    
    # json_data = json.dumps(q.encode())
    # print('TYPE', type(json_data))
    # q2 = json.loads(json_data, object_hook=Question.decode)
    
    # print(f'{json_data=}\n')
    # print(f'{q2=}')
    
    
    # qs = QuizSubmission(q2, None)
    # print(qs.question, qs.answer, qs.isanswered, qs.iscorrect)
    
    # qs = QuizSubmission(q2, Answer('ocean'))
    # print(qs.question.answer, qs.answer, qs.isanswered, qs.iscorrect)
    
