import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    
    '''
    Set up CORS. Allow '*' for origins.
    '''
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    '''
    Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
       response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
       response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
       return response
    ''' 
    Create an endpoint to handle GET requests 
    for all available categories.
    '''
    @app.route('/categories')
    def get_categories():
       categories = Category.query.order_by(Category.id).all()
       return jsonify(
           {
               'categories': {category.id: category.type for category in categories}
               
           }
           )
  
    '''
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    '''
    @app.route("/questions")
    def retrieve_questions():
          #page =  request.args.get("page", 1, type=int)
          selection = Question.query.order_by(Question.id).all()
          current_questions = paginate_questions(request, selection)
          categories = Category.query.order_by(Category.id).all()
          
          if len(current_questions) == 0:
              abort(404)
  
          return jsonify(
              {
                  "success": True,
                  "questions": current_questions,
                  "total_questions": len(Question.query.all()),
                  "categories" : {category.id: category.type for category in categories},
                  "current_category" : None
              }
          )
    
  
    '''
    Create an endpoint to DELETE question using a question ID.
    '''
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
         try:
             question = Question.query.filter(Question.id == question_id).one_or_none()
  
             if question is None:
                 abort(404)
  
             question.delete()
             selection = Question.query.order_by(Question.id).all()
             current_questions = paginate_questions(request, selection)
  
             return jsonify(
                 {
                     "success": True,
                     "deleted": question_id,
                     "questions": current_questions,
                     "total_questions": len(Question.query.all()),
                 }
             )
  
         except:
             abort(422)
  
    '''
    @TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.
    '''
    @app.route("/questions", methods=["POST"])
    def create_question():
      body = request.get_json()
  
      question = body.get("question", None)
      answer = body.get("answer", None)
      category = body.get("category", None)
      difficulty = body.get("difficulty", None)
      try:
          question = Question(question=question, answer=answer, category=category, difficulty=difficulty)
          question.insert()
  
          selection = Question.query.order_by(Question.id).all()
          current_questions = paginate_questions(request, selection)
  
          return jsonify(
              {
                  "success": True,
                  "created": question.id,
                  "questionss": current_questions,
                  "total_questions": len(Question.query.all()),
                  "difficulty": difficulty
              }
          )
  
      except:
          abort(422)
  
    '''
    @TODO: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question.  
    '''
    @app.route("/questions/search", method=["POST"])
    def search_question():
        req = request.get_json()
        search_term = req.get("searchTerm", None)
        questions = Question.query.order_by(Question.id).all()
        selection = []
        for q in questions:
            if search_term in q.question:
                selection.append(search_term)
        current_questions = paginate_questions(request, selection)
        
        return jsonify(
            {
                "questions"})

    """
    @TODO:
    Create a GET endpoint to get questions based on category.
    """
    @app.route("/categories/<int:id>/questions")
    def questions_in_category(id):
        
        category = Category.query.filter_by(id=id).one_or_none()
        if category:
            
            questionsInCat = Question.query.filter_by(category=str(id)).all()
            currentQuestions = paginate_questions(request, questionsInCat)
    
            return jsonify({
                'success': True,
                'questions': currentQuestions,
                'total_questions': len(questionsInCat),
                'current_category': category.type
            })
        
        else:
            abort(404)
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    """
    @app.route('/quizzes', methods=['POST'])
    def quiz():
        # get the qestion category an the previous question
        body = request.get_json()
        quizCategory = body.get('quiz_category')
        previousQuestion = body.get('previous_questions')
    
        try:
            if (quizCategory['id'] == 0):
                questionsQuery = Question.query.all()
            else:
                questionsQuery = Question.query.filter_by(
                    category=quizCategory['id']).all()
    
            randomIndex = random.randint(0, len(questionsQuery)-1)
            nextQuestion = questionsQuery[randomIndex]
    
            stillQuestions = True
            while nextQuestion.id not in previousQuestion:
                nextQuestion = questionsQuery[randomIndex]
                return jsonify({
                    'success': True,
                    'question': {
                        "answer": nextQuestion.answer,
                        "category": nextQuestion.category,
                        "difficulty": nextQuestion.difficulty,
                        "id": nextQuestion.id,
                        "question": nextQuestion.question
                    },
                    'previousQuestion': previousQuestion
                })
    
        except Exception as e:
            print(e)
            abort(404)
    
    
    '''
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource Not Found"
        }), 404
    
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Not Processable"
        }), 422
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        }), 400
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        }), 500
    return app

    
