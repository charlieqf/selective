from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.collection import Collection
from app.models.item import Item
from sqlalchemy.exc import IntegrityError
from datetime import datetime

bp = Blueprint('collections', __name__, url_prefix='/api/collections')

@bp.route('', methods=['GET'])
@jwt_required()
def get_collections():
    current_user_id = get_jwt_identity()
    # List active collections
    collections = Collection.query.filter_by(
        user_id=current_user_id, 
        is_deleted=False
    ).order_by(Collection.created_at.desc()).all()
    
    return jsonify([c.to_dict() for c in collections]), 200

@bp.route('', methods=['POST'])
@jwt_required()
def create_collection():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    name = data.get('name')
    if not name:
        return jsonify({'error': 'Name is required'}), 400
        
    try:
        collection = Collection(
            user_id=current_user_id,
            name=name,
            icon=data.get('icon'),
            color=data.get('color')
        )
        db.session.add(collection)
        db.session.commit()
        return jsonify(collection.to_dict()), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'A collection with this name already exists'}), 409
    except Exception as e:
        db.session.rollback()
        print(f"Create collection error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/<int:id>', methods=['PATCH'])
@jwt_required()
def update_collection(id):
    current_user_id = get_jwt_identity()
    collection = Collection.query.get_or_404(id)
    
    if str(collection.user_id) != str(current_user_id):
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json()
    
    # Handle Rename
    if 'name' in data:
        collection.name = data['name']
        
    if 'icon' in data:
        collection.icon = data['icon']
    if 'color' in data:
        collection.color = data['color']
        
    # Handle Soft Delete
    if 'is_deleted' in data:
        collection.is_deleted = data['is_deleted']
        if collection.is_deleted:
            collection.deleted_at = datetime.utcnow()
        else:
            collection.deleted_at = None
            
    try:
        db.session.commit()
        return jsonify(collection.to_dict()), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'A collection with this name already exists'}), 409

@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_collection(id):
    """Hard Delete (Cascade)"""
    current_user_id = get_jwt_identity()
    collection = Collection.query.get_or_404(id)
    
    if str(collection.user_id) != str(current_user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Only allow hard delete if already soft deleted (optional safety check, but good practice)
    if not collection.is_deleted:
         return jsonify({'error': 'Collection must be in trash to delete permanently'}), 400

    try:
        # Cascade delete items (DB only)
        # Note: We skip Cloudinary deletion for performance as per design
        Item.query.filter_by(collection_id=id).delete()
        
        db.session.delete(collection)
        db.session.commit()
        return jsonify({'message': 'Collection and all items deleted permanently'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Delete collection error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/trash', methods=['GET'])
@jwt_required()
def get_trash():
    current_user_id = get_jwt_identity()
    collections = Collection.query.filter_by(
        user_id=current_user_id, 
        is_deleted=True
    ).order_by(Collection.deleted_at.desc()).all()
    
    return jsonify([c.to_dict() for c in collections]), 200

@bp.route('/<int:id>/restore', methods=['POST'])
@jwt_required()
def restore_collection(id):
    current_user_id = get_jwt_identity()
    collection = Collection.query.get_or_404(id)
    
    if str(collection.user_id) != str(current_user_id):
        return jsonify({'error': 'Unauthorized'}), 403
        
    if not collection.is_deleted:
        return jsonify({'message': 'Collection is already active'}), 200
        
    try:
        collection.is_deleted = False
        collection.deleted_at = None
        db.session.commit()
        return jsonify(collection.to_dict()), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'An active collection with this name already exists. Please rename it first.'}), 409
