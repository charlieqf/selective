from flask import Blueprint, request, jsonify
from app import db
from app.models.question import Question
from app.schemas.question import QuestionSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
import cloudinary.uploader

bp = Blueprint('questions', __name__, url_prefix='/api/questions')

@bp.route('', methods=['GET'])
@jwt_required()
def get_questions():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    subject = request.args.get('subject')
    difficulty = request.args.get('difficulty', type=int)
    status = request.args.get('status')
    sort_by = request.args.get('sort_by', 'created_at')
    sort_direction = request.args.get('sort_direction', 'desc')
    
    current_user_id = get_jwt_identity()
    
    # Scope to current user's questions only
    query = Question.query.filter_by(author_id=current_user_id)
    
    if subject:
        query = query.filter_by(subject=subject)
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if status:
        query = query.filter_by(status=status)
    
    # 添加排序参数
    allowed_sort_fields = ['created_at', 'difficulty', 'updated_at']
    if sort_by not in allowed_sort_fields:
        sort_by = 'created_at'
    
    # 应用排序
    if sort_direction == 'asc':
        query = query.order_by(getattr(Question, sort_by).asc())
    else:
        query = query.order_by(getattr(Question, sort_by).desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    schema = QuestionSchema(many=True)
    return jsonify({
        'questions': schema.dump(pagination.items),
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@bp.route('', methods=['POST'])
@jwt_required()
def create_question():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    schema = QuestionSchema()
    errors = schema.validate(data)
    if errors:
        return jsonify({'error': 'Validation failed', 'details': errors}), 400
        
    try:
        question = Question(
            title=data.get('title'),
            subject=data['subject'],
            difficulty=data.get('difficulty', 3),
            status=data.get('status', 'UNANSWERED'),
            content_text=data.get('content_text'),
            author_id=current_user_id
        )
        question.set_images(data.get('images', []))
        
        db.session.add(question)
        db.session.commit()
        
        return jsonify(schema.dump(question)), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Create question error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_question(id):
    question = Question.query.get_or_404(id)
    current_user_id = get_jwt_identity()
    
    # Security: Ownership check
    if str(question.author_id) != str(current_user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    schema = QuestionSchema()
    return jsonify(schema.dump(question)), 200

@bp.route('/<int:id>', methods=['PATCH'])
@jwt_required()
def update_question(id):
    question = Question.query.get_or_404(id)
    current_user_id = get_jwt_identity()
    
    # Security: Ownership check
    if str(question.author_id) != str(current_user_id):
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json()
    schema = QuestionSchema(partial=True)
    errors = schema.validate(data)
    if errors:
        return jsonify({'error': 'Validation failed', 'details': errors}), 400
        
    try:
        if 'title' in data:
            question.title = data['title']
        if 'subject' in data:
            question.subject = data['subject']
        if 'difficulty' in data:
            question.difficulty = data['difficulty']
        if 'status' in data:
            question.status = data['status']
        if 'content_text' in data:
            question.content_text = data['content_text']
        if 'images' in data:
            question.set_images(data['images'])
            
        db.session.commit()
        return jsonify(schema.dump(question)), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Update question error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_question(id):
    question = Question.query.get_or_404(id)
    current_user_id = get_jwt_identity()
    
    # Security: Ownership check
    if str(question.author_id) != str(current_user_id):
        return jsonify({'error': 'Unauthorized'}), 403
        
    try:
        # Cleanup Cloudinary images
        images = question.get_images()
        for img in images:
            if 'public_id' in img:
                cloudinary.uploader.destroy(img['public_id'])
                
        db.session.delete(question)
        db.session.commit()
        return jsonify({'message': 'Question deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Delete question error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
