# rjm_games_V2
HTTP Game Server
utilizes game_engine from version 1
complete redesign


5/13/2022  Getting there.  Able to request and render files all the way to start page.
            Currently, debugging quiz.py and quiz_view.py.
            Still need to fix the issue with having to stop loading page and re-requesting
            page to load.  This may have something to do with favicon.ico.  Might need to
            send a fake (or real) icon.  May want to make it non-cacheable, so that it is
            predictable, when the browser will request it.
            
           Able to load quiz with single question.  Still need to solve the loading problem.
            Considering trying to read after each send, then setting a short timeout on the
            socket.  This will have to be contained in a try-except block, but may be
            necessary to hunt and kill favicon.
            
5/14/2022  Fixed the favicon issue.  Code waits for it after first HTTP/1.1 200 response,
            then sends back HTTP/1.1 404.  This version works, because the favicon stays
            cached on the browser.  Implementation would have to change (easy fix looking
            no-cache in favicon request, then calling HTTPCommsModule.hunt_and_kill_favicon
            after HTTP 200 responses and fetches for css, etc.
           
           Also fixed the page loading issue, which was separate.  This was not all caused
            favicon.  Closer attention to the Connection header was needed.  If a fetch is 
            not expected (i.e. becuase of favicon, text/css, text/javascript, image/, etc),
            the value should be Connection: close.  Otherwise, Connection: keep-alive.
           
           Last thing is to debug the game visualization and implementation.  That will be
            focus this week.  Solving that will provide a deliverable for the project.  It 
            is unlikely there will be time to implement database storage for game
            information (initialization, results, users).  Also, it seems that the back
            buttons may not be working properly, though further testing is needed.

5/15/2022  Fully working version of Server and Quiz game.  Still may not record answers 
            correctly when you used back and forward buttons during the Quiz game.  NOT yet
            implemented: user registration and real user validation.  These will be in the
            admin "link." Also in admin, I will try to implement forms to create a quiz.
            It would also be nice to complete the css request.  This was solved in
            servertest.py, butnot sure there is time to implement and test properly.

5/16/2022  Added Registry to enter new users.  Working end-to-end.  Authenticator does not
            against the registered users yet.  Instead of implementing the Admin
            funtionality of writing new quizes, this will be a separate terminal tool, in
            view of time.

5/17/2022  Full-implementation.  Added User registration with file storage, rather than
            database persistence.  Authorization is now active.  Again, this uses file
            persistence rather than database.
            Also implemented terminal tool for creating quizzes.  Quizzes must be stored
            in the games/quiz directory, which is a directory above
            that of the tool, called Quiz Maker.  Quiz Maker is implemented is quiz_maker.py
            Currently, the only quiz file that will be loaded is test_quiz.  Time
            permitting, the admin functionality of the web site will allow changing this
            file.  If possible prior to submission, the threading of the server should be
            assessed for more robust server closure.  At this stage, the project could be
            submitted.
