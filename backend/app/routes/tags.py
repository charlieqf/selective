from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.tag import Tag
from app import db

bp = Blueprint('tags', __name__, url_prefix='/api/tags')

@bp.route('', methods=['GET'])
@jwt_required()
def get_tags():
    """Get all tags for the current user"""
    user_id = get_jwt_identity()
    
    # Optional search parameter for autocomplete
    search = request.args.get('search', '')
    
    query = Tag.query.filter_by(user_id=user_id)
    
    if search:
        query = query.filter(Tag.name.ilike(f'%{search}%'))
    
    tags = query.order_by(Tag.name).all()
    
    return jsonify([tag.to_dict() for tag in tags]), 200
