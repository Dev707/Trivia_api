import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r'/*': {'origins': '*'}})

    '''
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    '''
    @TODO: 
    Create an endpoint to handle GET requests 
    for all available categories.
    '''

    '''
    @TODO: 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    '''
    def paginate_questions(request, questions):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        questions = [q.format() for q in questions]
        current_q = questions[start:end]
        return current_q

    @app.route('/categories', methods=['GET'])
    def get_categories():
        categories = Category.query.order_by(Category.id).all()
        if (len(categories) == 0):
            abort(404)
        return jsonify({
            'success': True,
            'categories': {category.id: category.type
                           for category in categories}
        })

    @app.route('/questions', methods=['GET'])
    def get_questions():
        try:
            questions = Question.query.order_by(Question.id).all()
            categories = Category.query.order_by(Category.id).all()
            current_questions = paginate_questions(request, questions)
            if len(current_questions) == 0:
                abort(404)
            return jsonify({
                'success': True,
                'questions': paginate_questions(request, questions),
                'total_questions': len(questions),
                'categories': {category.id: category.type
                               for category in categories}
            })
        except Exception:
            abort(404)

    '''
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''
    @app.route('/questions/<int:q_id>', methods=['DELETE'])
    def delete_question(q_id):
        try:
            question = Question.query.filter_by(id=q_id).one_or_none()
            if question is None:
                abort(404)
            question.delete()
            return jsonify({
                'success': True,
                'deleted': q_id
            })
        except Exception:
            abort(422)

    '''
    @TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''
    @app.route('/questions', methods=['POST'])
    def post_question():
        try:
            body = request.get_json()
            if (body.get('searchTerm')):
                search_term = body.get('searchTerm')
                selection = Question.query.filter(
                    Question.question.ilike(f'%{search_term}%')).all()
                paginated = paginate_questions(request, selection)
                return jsonify({
                    'success': True,
                    'questions': paginated,
                    'total_questions': len(Question.query.all())
                })
            else:
                new_question = body.get('question')
                new_answer = body.get('answer')
                new_difficulty = body.get('difficulty')
                new_category = body.get('category')
                if ((new_question is None) or (new_answer is None)
                        or (new_difficulty is None) or (new_category is None)):
                    abort(422)
                question = Question(question=new_question, answer=new_answer,
                                    difficulty=new_difficulty, category=new_category)
                question.insert()
                return jsonify({
                    'success': True,
                    'question_id': question.id
                })
        except Exception:
            abort(422)

    '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 

    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''
    @app.route('/categories/<category_id>/questions', methods=['GET'])
    def retrieve_questions_category(category_id):
        try:
            questions = Question.query.order_by(Question.id).filter_by(
                category=category_id).all()
            if len(questions) == 0:
                abort(404)
            categories = Category.query.order_by(Category.id).all()
            paged_questions = paginate_questions(request, questions)
            return jsonify({
                'success': True,
                'questions': paged_questions,
                'total_questions': len(questions),
                'categories': {category.id: category.type
                               for category in categories},
                'current_category': category_id
            })
        except Exception:
            abort(404)

    '''
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''
    @app.route('/quizzes', methods=['POST'])
    def quiz():
        try:
            body = request.get_json()
            pre_questions = body.get('previous_questions')
            quiz_cat = body.get('quiz_category')
            next_q = None
            #print(body)
            if quiz_cat['id'] == 0:
                questions = Question.query.all()
            else:
                questions = Question.query.filter_by(
                  category=int(quiz_cat.get('id'))).all()
            for q in questions:
                if q.id not in pre_questions:
                    next_q = q
                    break
            if next_q is None:
                return jsonify({'Success': True, 'question': False})
            return jsonify({
              'success': True,
              'question': next_q.format()
            })
        except Exception:
            abort(422)

    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        }), 500

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    return app
