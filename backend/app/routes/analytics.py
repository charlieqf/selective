from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.question import Question
from sqlalchemy import func

bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    user_id = get_jwt_identity()
    
    # 总体统计
    total = Question.query.filter_by(author_id=user_id).count()
    answered = Question.query.filter_by(author_id=user_id).filter(
        Question.status.in_(['ANSWERED', 'MASTERED'])
    ).count()
    mastered = Question.query.filter_by(author_id=user_id, status='MASTERED').count()
    need_review = Question.query.filter_by(author_id=user_id, status='NEED_REVIEW').count()
    
    # 按科目统计 - 使用数据库中的大写枚举值
    by_subject = {}
    subjects = ['READING', 'WRITING', 'MATHS', 'THINKING_SKILLS']
    for subject in subjects:
        subject_total = Question.query.filter_by(author_id=user_id, subject=subject).count()
        subject_answered = Question.query.filter_by(author_id=user_id, subject=subject).filter(
            Question.status.in_(['ANSWERED', 'MASTERED'])
        ).count()
        subject_mastered = Question.query.filter_by(author_id=user_id, subject=subject, status='MASTERED').count()
        by_subject[subject] = {
            'total': subject_total,
            'answered': subject_answered,
            'mastered': subject_mastered
        }
    
    # 按难度统计
    by_difficulty = {}
    for i in range(1, 6):
        count = Question.query.filter_by(author_id=user_id, difficulty=i).count()
        by_difficulty[str(i)] = count
    
    return jsonify({
        'total_questions': total,
        'answered_questions': answered,
        'mastered_questions': mastered,
        'need_review_questions': need_review,
        'by_subject': by_subject,
        'by_difficulty': by_difficulty
    }), 200


@bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    user_id = get_jwt_identity()
    limit = request.args.get('limit', 10, type=int)
    subject = request.args.get('subject')
    
    # 简化推荐逻辑(Week 5会完善)
    query = Question.query.filter_by(author_id=user_id)
    
    if subject:
        query = query.filter_by(subject=subject)
    
    # 优先级: NEED_REVIEW > UNANSWERED, 按难度升序
    need_review = query.filter_by(status='NEED_REVIEW').order_by(Question.difficulty.asc()).limit(limit).all()
    
    if len(need_review) < limit:
        remaining = limit - len(need_review)
        unanswered = query.filter_by(status='UNANSWERED').order_by(Question.difficulty.asc()).limit(remaining).all()
        recommendations = need_review + unanswered
    else:
        recommendations = need_review
    
    from app.schemas.question import QuestionSchema
    schema = QuestionSchema(many=True)
    return jsonify(schema.dump(recommendations)), 200
