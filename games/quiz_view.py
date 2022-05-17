# -*- coding: utf-8 -*-
"""
Created on Wed May 11 12:00:52 2022

@author: Robert J McGinness
"""

from typing import Dict
from typing import List

from rjm_gaming.game_view import GameView
from rjm_gaming.game_base import GameResult
from quiz import QuizSubmission



class QuizView(GameView):
    
    ########################################################
    ######???CONSIDER READING IN ALL FILES UP FRONT TO SAVE PROCESSING
    ######TIME LATER
    
    def introduction(self, **kwargs) -> str:
        """ Expects kwargs['request'].session to be client id.
            Renders HTML start form
        """
        
        start_html = self.render_file('../static/game/quiz/quiz_start.html')
        
        start_html = start_html.replace('%QUIZ%', 'Quiz')
        start_html = start_html.replace('%NAME%', kwargs['player'].name)
        
        
        session = kwargs['request'].session
        
        return session.form_insert(start_html)
    
    def game_over(self, **kwargs) -> str:
        """ Requires kwargs['session'] to contain the client id
            and kwargs['questions'] to contain all of the 
            QuizSubmission objects at submission
        """
        results_html = self.render_file('../static/game/quiz/' +\
                                             'quiz_results.html')
        
        game_result = kwargs['game_result']
        results = game_result.result_data
        
        results_html = results_html.replace('%QUIZ%', game_result.game_name)
        results_html = results_html.replace('%NAME%', game_result.players[0].name)
        results_html = results_html.replace('%SCORE%', str(results['num_correct']))
        results_html = results_html.replace('%TOTAL%', str(len(results['questions'])))
        results_html = results_html.replace('%PERCENT%', results['percent'])
        
        results = self.__build_results(game_result.result_data['questions'])
        results_html = results_html.replace('</field', results + '</field')
        
        session = kwargs['session']
        
        return session.form_insert(results_html)
    
    def __build_results(self, submissions: List[QuizSubmission]) -> str:
        
        questions = ''
        for i, submission in enumerate(submissions):
            question_tag = '<p>Question %NUM%: %CORRECT%</p>'
            
            question_tag = question_tag.replace('%NUM%', str(i+1))
            
            result = 'correct'
            if not submission.iscorrect:
                result = 'X'
                if not submission.isanswered:
                    result = 'unanswered'
            
            question_tag = question_tag.replace('%CORRECT%', result)
            questions += question_tag
        
        return questions

    def render(self, **kwargs) -> str:
        """ Expects kwargs['request'].session to contain client 
            id. 
            Renders HTML of each GameResult or the final
            results when game over
        """
        if kwargs['game_result'].game_over:
            return self.game_over(**kwargs)
        
        return self.render_with_file(self.html_file, **kwargs)
    
    def render_with_file(self, file_name: str, **kwargs) -> str:
        """ Renders an HTML file with passed GameResult.
            Expects an HTTPSession value for kwargs['session']
        """
        session = kwargs['session']
        result = kwargs['game_result']
        game_html = self.render_result_with_file(result, file_name)
        
        return session.form_insert(game_html) # add session information and return
    
    def render_result_with_file(self, result: GameResult,
                                      file_name:str) -> str:
        ''' Adds result data to an html file'''
        
        game_html = self.render_file(file_name) # defined in superclass
        
        game_html = game_html.replace('%QUIZ%', result.game_name)
        game_html = game_html.replace('%NAME%', result.players[0].name)
        
        result_data = result.result_data
        question = result_data['question']
        has_skip_button = bool(result_data['next_question'])
        has_back_button = bool(result_data['prev_question'])
        
        
        game_html = game_html.replace('%QUESTION NUMBER%', f'Question {question.q_id}')
        question_html = self.__build_question(question.question)
        game_html = game_html.replace('<fieldset>', '<fieldset>' + question_html)
        
        if not has_skip_button:
            game_html = game_html.replace('value="Skip"', 'hidden ' + 'value="Skip"')
        
        if not has_back_button:
            game_html = game_html.replace('value="Back"', 'hidden ' + 'value="Back"')
        
        choices_list = question.choices
        game_html = game_html.replace('</fieldset>',
                            self.__build_choices(choices_list, result_data['answer']) + '</fieldset>')
        
        return game_html
    
    def __build_question(self, question: str) -> str:
        question_html = '<p>QUESTION</p>'
        
        return question_html.replace('QUESTION', question)
    
    def __build_choices(self, choices: List[str], answer: str) -> str:
        radio_button = '<input type="radio" id="XXX" name="answer" value="CHOICE"/>'
        label = '<label for="XXX">CHOICE</label><br/>'
        
        all_choices_html = ''
        counter = 1
        for choice in choices:
            choice_html = radio_button + label
            choice_html = choice_html.replace('XXX', str(counter))
            choice_html = choice_html.replace('CHOICE', choice)
            
            # show answer, if already given
            if answer and answer == choice.replace(' ', '+'): # dealing with spaces changed to + in html form
                choice_html = choice_html.replace('/>', ' checked />')
            all_choices_html += choice_html
            counter += 1
        
        return all_choices_html
    
    def render_result(self, result: GameResult) -> str:
        '''Return html string of result that can be sent to browser'''
        return self.render_result_with_file(result, self.html_file)
    
    def get_play(self, request: str) -> Dict:
        ''' Process new Play Request from browser.
            Return request as game-appropriate 
            key-value pairs.
        '''
        #package request in key-value pairs matching what quiz.py needs
        
        request = request.split(' ')[1]#get the middle with query
        play = {'input': None}
        try:
            input_idx = request.index('?')
            query = request[input_idx:]
            play['input'] = self.__parse_query(query, 'input=')
            play['answer'] = self.__parse_query(query, 'answer=')
        except IndexError:
            play['input'] = 'start'
        
        return play
    
    def __parse_query(self, query_line: str, target: str) -> str:
        value = ''
        try:
            query_sections = query_line.split('&')
            for section in query_sections:
                if target in section:
                    value = section.split('=')[1]
        except IndexError:
            return None
        
        return value

if __name__ == '__main__':
    import time
    from quiz import Question
    from quiz import Answer
    from rjm_gaming.game_base import GameResult
    from rjm_gaming.game_base import Player
    from rjm_gaming.game_network import HTTPSession
    
    qv = QuizView(str(time.time()), '../static/game/quiz.html')
    
    q = Question("Where do sharks live?",
                'ocean',
                1,
                ['desert', 'lake', 'ocean', 'mountain'],
                'multiple choice')
    q2 = Question("Where do sharks live?",
                'ocean',
                2,
                ['desert', 'lake', 'ocean', 'mountain'],
                'multiple choice')
    q3 = Question("Where do sharks live?",
                'ocean',
                3,
                ['desert', 'lake', 'ocean', 'mountain'],
                'multiple choice')
    
    results = {}
    
    
    result = GameResult([Player("Bronwyn", str(time.time()))],
                      game_name='Quiz',
                      result_id=1, 
                      question_num=1,
                      question=q,
                      answer=None,
                      prev_question=None,
                      next_question=q,
                      **results)
    
    print(qv.render_result(result))
    
    submission1 = QuizSubmission(q, Answer('ocean'))
    submission2 = QuizSubmission(q2, Answer('mountain'))
    submission3 = QuizSubmission(q3, None)
    
    submissions = [submission1,
                   submission2,
                   submission3]
    
    results = {}
    session = HTTPSession(str(time.time()))
    
    results['questions'] = submissions
    results['percent'] = str(100/3) + '%'
    results['num_correct'] = 1
    
    print('\n\n', results['num_correct'], '\n\n')
    
    
    result = GameResult([Player("Bronwyn", str(time.time()))],
                      game_name='Quiz',
                      game_over=True,
                      result_id=1, 
                      question_num=1,
                      question=None,
                      answer=None,
                      prev_question=None,
                      next_question=q,
                      **results)
    
    output = dict(session=session, game_result=result)
    
    print(qv.render(**output))
    
    print()
    print(qv.get_play('GET /quiz?answer=ocean&input=Answer HTTP/1.1'))