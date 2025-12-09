from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.item import Item
from app.models.answer import Answer
from app.models.user import User
from sqlalchemy import func

bp = Blueprint('answers', __name__, url_prefix='/api')

@bp.route('/items/<int:item_id>/answers', methods=['POST'])
@jwt_required()
def submit_answer(item_id):
    # Logic uses Item
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    item = Item.query.get_or_404(item_id)
    
    # Security Check: Ensure user owns the item
    if str(item.author_id) != str(current_user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Validate input
    if 'is_correct' not in data:
        return jsonify({'error': 'is_correct is required'}), 400
        
    is_correct = data['is_correct']
    content = data.get('content', '')
    duration_seconds = data.get('duration_seconds', 0)
    
    # Create Answer record
    answer = Answer(
        item_id=item_id,
        user_id=current_user_id,
        content=content,
        is_correct=is_correct,
        duration_seconds=duration_seconds
    )
    db.session.add(answer)
    
    # Update Item stats
    db.session.flush() # Ensure the new answer is counted
    
    total_attempts = Answer.query.filter_by(item_id=item_id).count()
    total_correct = Answer.query.filter_by(item_id=item_id, is_correct=True).count()
    
    item.attempts = total_attempts
    if total_attempts > 0:
        item.success_rate = round((total_correct / total_attempts) * 100.0, 1)
    else:
        item.success_rate = 0.0
    
    # Update Item status logic
    if is_correct:
        item.status = 'MASTERED'
        item.needs_review = False  # Clear review flag on correct answer
    else:
        item.status = 'ANSWERED'  # Still counts as answered
        item.needs_review = True  # Mark for review on wrong answer
    
    db.session.commit()
    
    return jsonify({
        'message': 'Answer submitted successfully',
        'answer': answer.to_dict(),
        'item_status': item.status
    }), 201

@bp.route('/items/<int:item_id>/answers', methods=['GET'])
@jwt_required()
def get_answer_history(item_id):
    current_user_id = get_jwt_identity()
    
    # Ensure item exists and belongs to user
    item = Item.query.get_or_404(item_id)
    
    if str(item.author_id) != str(current_user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    answers = Answer.query.filter_by(
        item_id=item_id, 
        user_id=current_user_id
    ).order_by(Answer.created_at.desc()).all()
    
    return jsonify([a.to_dict() for a in answers]), 200

@bp.route('/items/review-session', methods=['GET'])
@jwt_required()
def get_review_session():
    current_user_id = get_jwt_identity()
    
    # Get limit from query params, default 10
    limit = request.args.get('limit', 10, type=int)
    subject = request.args.get('subject')
    
    query = Item.query.filter_by(
        author_id=current_user_id,
        needs_review=True
    )
    
    if subject:
        query = query.filter_by(subject=subject)
        
    # Randomize and limit
    items = query.order_by(func.random()).limit(limit).all()
    
    return jsonify([q.to_dict() for q in items]), 200
