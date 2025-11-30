from flask import Blueprint, request, jsonify
from app import db
from app.models.item import Item
from app.models.collection import Collection
from app.schemas.item import ItemSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
import cloudinary.uploader

bp = Blueprint('items', __name__, url_prefix='/api/items')

@bp.route('', methods=['GET'])
@jwt_required()
def get_items():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Filters
    subject = request.args.get('subject')
    collection_id = request.args.get('collection_id', type=int)
    difficulty = request.args.get('difficulty', type=int)
    status = request.args.get('status')
    
    sort_by = request.args.get('sort_by', 'created_at')
    sort_direction = request.args.get('sort_direction', 'desc')
    
    current_user_id = get_jwt_identity()
    
    # Scope to current user's items only
    query = Item.query.filter_by(author_id=current_user_id)
    
    if collection_id:
        query = query.filter_by(collection_id=collection_id)
    # Legacy subject filter support
    elif subject:
        query = query.filter_by(subject=subject)
        
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    if status:
        query = query.filter_by(status=status)
    
    # Sorting
    allowed_sort_fields = ['created_at', 'difficulty', 'updated_at']
    if sort_by not in allowed_sort_fields:
        sort_by = 'created_at'
    
    if sort_direction == 'asc':
        query = query.order_by(getattr(Item, sort_by).asc())
    else:
        query = query.order_by(getattr(Item, sort_by).desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    schema = ItemSchema(many=True)
    return jsonify({
        'items': schema.dump(pagination.items),
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@bp.route('', methods=['POST'])
@jwt_required()
def create_item():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    schema = ItemSchema()
    errors = schema.validate(data)
    if errors:
        return jsonify({'error': 'Validation failed', 'details': errors}), 400
        
    # Security: Validate collection ownership
    collection_id = data.get('collection_id')
    if collection_id:
        collection = Collection.query.get(collection_id)
        if not collection:
            return jsonify({'error': 'Invalid collection_id: Collection not found'}), 404
        if str(collection.user_id) != str(current_user_id):
            return jsonify({'error': 'Invalid collection_id: Access denied'}), 403
        
    try:
        item = Item(
            title=data.get('title'),
            subject=data.get('subject'), # Legacy
            collection_id=collection_id, # New
            difficulty=data.get('difficulty', 3),
            status=data.get('status', 'UNANSWERED'),
            content_text=data.get('content_text'),
            author_id=current_user_id
        )
        item.set_images(data.get('images', []))
        
        # Promote pending uploads
        from app.models.pending_upload import PendingUpload
        for img in data.get('images', []):
            if 'public_id' in img:
                PendingUpload.query.filter_by(public_id=img['public_id']).delete()
        
        db.session.add(item)
        db.session.commit()
        
        return jsonify(schema.dump(item)), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Create item error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_item(id):
    item = Item.query.get_or_404(id)
    current_user_id = get_jwt_identity()
    
    # Security: Ownership check
    if str(item.author_id) != str(current_user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    schema = ItemSchema()
    return jsonify(schema.dump(item)), 200

@bp.route('/<int:id>', methods=['PATCH'])
@jwt_required()
def update_item(id):
    item = Item.query.get_or_404(id)
    current_user_id = get_jwt_identity()
    
    # Security: Ownership check
    if str(item.author_id) != str(current_user_id):
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json()
    schema = ItemSchema(partial=True)
    errors = schema.validate(data)
    if errors:
        return jsonify({'error': 'Validation failed', 'details': errors}), 400
        
    try:
        if 'title' in data:
            item.title = data['title']
        if 'subject' in data:
            item.subject = data['subject']
        if 'collection_id' in data:
            collection_id = data['collection_id']
            # Security: Validate collection ownership if changing collection
            if collection_id:
                collection = Collection.query.get(collection_id)
                if not collection:
                    return jsonify({'error': 'Invalid collection_id: Collection not found'}), 404
                if str(collection.user_id) != str(current_user_id):
                    return jsonify({'error': 'Invalid collection_id: Access denied'}), 403
            item.collection_id = collection_id
            
        if 'difficulty' in data:
            item.difficulty = data['difficulty']
        if 'status' in data:
            item.status = data['status']
        if 'content_text' in data:
            item.content_text = data['content_text']
        if 'images' in data:
            item.set_images(data['images'])
            # Promote pending uploads
            from app.models.pending_upload import PendingUpload
            for img in data['images']:
                if 'public_id' in img:
                    PendingUpload.query.filter_by(public_id=img['public_id']).delete()
            
        db.session.commit()
        return jsonify(schema.dump(item)), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Update item error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_item(id):
    item = Item.query.get_or_404(id)
    current_user_id = get_jwt_identity()
    
    # Security: Ownership check
    if str(item.author_id) != str(current_user_id):
        return jsonify({'error': 'Unauthorized'}), 403
        
    try:
        # Cleanup Cloudinary images
        images = item.get_images()
        for img in images:
            if 'public_id' in img:
                cloudinary.uploader.destroy(img['public_id'])
                
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': 'Item deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Delete item error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
