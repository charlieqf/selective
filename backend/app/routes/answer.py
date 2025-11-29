from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.question import Question
from app.models.answer import Answer
from app.models.user import User
from sqlalchemy import func

bp = Blueprint('answers', __name__, url_prefix='/api')

@bp.route('/questions/<int:question_id>/answers', methods=['POST'])
@jwt_required()
def submit_answer(question_id):
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    question = Question.query.get_or_404(question_id)
    
    # Security Check: Ensure user owns the question
    if str(question.author_id) != str(current_user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Validate input
    if 'is_correct' not in data:
        return jsonify({'error': 'is_correct is required'}), 400
        
    is_correct = data['is_correct']
    content = data.get('content', '')
    duration_seconds = data.get('duration_seconds', 0)
    
    # Create Answer record
    answer = Answer(
        question_id=question_id,
        user_id=current_user_id,
        content=content,
        is_correct=is_correct,
        duration_seconds=duration_seconds
    )
    db.session.add(answer)
    
    # Update Question stats
    db.session.flush() # Ensure the new answer is counted
    
    total_attempts = Answer.query.filter_by(question_id=question_id).count()
    total_correct = Answer.query.filter_by(question_id=question_id, is_correct=True).count()
    
    question.attempts = total_attempts
    if total_attempts > 0:
        question.success_rate = round((total_correct / total_attempts) * 100.0, 1)
    else:
        question.success_rate = 0.0
    
    # Update Question status logic
    # MVP Logic:
    # - If Correct: NEED_REVIEW -> MASTERED (or ANSWERED -> MASTERED)
    # - If Incorrect: * -> NEED_REVIEW
    if is_correct:
        question.status = 'MASTERED'
    else:
        question.status = 'NEED_REVIEW'
    
    db.session.commit()
    
    return jsonify({
        'message': 'Answer submitted successfully',
        'answer': answer.to_dict(),
        'question_status': question.status
    }), 201

@bp.route('/questions/<int:question_id>/answers', methods=['GET'])
@jwt_required()
def get_answer_history(question_id):
    current_user_id = get_jwt_identity()
    
    # Ensure question exists and belongs to user
    question = Question.query.get_or_404(question_id)
    
    if str(question.author_id) != str(current_user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    answers = Answer.query.filter_by(
        question_id=question_id, 
        user_id=current_user_id
    ).order_by(Answer.created_at.desc()).all()
    
    return jsonify([a.to_dict() for a in answers]), 200

@bp.route('/questions/review-session', methods=['GET'])
@jwt_required()
def get_review_session():
    current_user_id = get_jwt_identity()
    
    # Get limit from query params, default 10
    limit = request.args.get('limit', 10, type=int)
    subject = request.args.get('subject')
    
    query = Question.query.filter_by(
        author_id=current_user_id,
        status='NEED_REVIEW'
    )
    
    if subject:
        query = query.filter_by(subject=subject)
        
    # Randomize and limit
    questions = query.order_by(func.random()).limit(limit).all()
    
    return jsonify([q.to_dict() for q in questions]), 200
