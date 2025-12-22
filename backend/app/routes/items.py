from flask import Blueprint, request, jsonify
from app import db
from datetime import datetime
from app.models.item import Item
from app.models.collection import Collection
from app.models.tag import Tag
from app.schemas.item import ItemSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from marshmallow import ValidationError
import cloudinary.uploader
from sqlalchemy.orm.attributes import flag_modified

bp = Blueprint('items', __name__, url_prefix='/api/items')

# Module-level schema instances (singletons for performance)
item_schema = ItemSchema()
item_schema_partial = ItemSchema(partial=True)

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
    tags = request.args.getlist('tag')  # Multiple tag filters
    
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
    
    # Needs review filter
    needs_review = request.args.get('needs_review')
    if needs_review and needs_review.lower() == 'true':
        query = query.filter_by(needs_review=True)
    
    # Tag filtering (AND logic)
    for tag_name in tags:
        query = query.filter(Item.tags.any(func.lower(Tag.name) == tag_name.lower()))
    
    # Sorting
    allowed_sort_fields = ['created_at', 'difficulty', 'updated_at']
    if sort_by not in allowed_sort_fields:
        sort_by = 'created_at'
    
    if sort_direction == 'asc':
        query = query.order_by(getattr(Item, sort_by).asc())
    else:
        query = query.order_by(getattr(Item, sort_by).desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Use to_dict() to ensure tags are included (ItemSchema has tags as load_only)
    return jsonify({
        'items': [item.to_dict() for item in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@bp.route('', methods=['POST'])
@jwt_required()
def create_item():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    try:
        data = item_schema.load(data)
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
        
    # Security: Validate collection ownership
    collection_id = data.get('collection_id')
    collection = None
    if collection_id:
        collection = Collection.query.get(collection_id)
        if not collection:
            return jsonify({'error': 'Invalid collection_id: Collection not found'}), 404
        if str(collection.user_id) != str(current_user_id):
            return jsonify({'error': 'Invalid collection_id: Access denied'}), 403

    # Derive subject from collection if not provided (keeps analytics compatible during migration)
    subject_value = data.get('subject')
    if not subject_value and collection and collection.type == 'SUBJECT':
        subject_value = collection.name
        
    try:
        item = Item(
            title=data.get('title'),
            subject=subject_value, # Legacy subject kept in sync for analytics/filters
            collection_id=collection_id, # New
            difficulty=data.get('difficulty', 3),
            status=data.get('status', 'UNANSWERED'),
            content_text=data.get('content_text'),
            author_id=current_user_id
        )
        item.set_images(data.get('images', []))
        
        # Handle tags
        tag_names = data.get('tags', [])
        for tag_name in tag_names:
            tag_name = tag_name.strip()
            
            # Validation
            if not tag_name:
                return jsonify({'error': 'Tag name cannot be empty'}), 400
            if len(tag_name) > 30:
                return jsonify({'error': 'Tag name cannot exceed 30 characters'}), 400
            
            # Find or create tag (case-insensitive)
            tag = Tag.query.filter(
                Tag.user_id == current_user_id,
                func.lower(Tag.name) == tag_name.lower()
            ).first()
            
            if not tag:
                tag = Tag(user_id=current_user_id, name=tag_name)
                db.session.add(tag)
                db.session.flush()  # Get ID
            
            item.tags.append(tag)
        
        # Promote pending uploads
        from app.models.pending_upload import PendingUpload
        for img in data.get('images', []):
            if 'public_id' in img:
                PendingUpload.query.filter_by(public_id=img['public_id']).delete()
        
        db.session.add(item)
        db.session.commit()
        
        return jsonify(item.to_dict()), 201
        
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
    
    return jsonify(item.to_dict()), 200

@bp.route('/<int:id>', methods=['PATCH'])
@jwt_required()
def update_item(id):
    item = Item.query.get_or_404(id)
    current_user_id = get_jwt_identity()
    
    # Security: Ownership check
    if str(item.author_id) != str(current_user_id):
        return jsonify({'error': 'Unauthorized'}), 403
        
    data = request.get_json()
    try:
        data = item_schema_partial.load(data)
    except ValidationError as e:
        return jsonify({'error': 'Validation failed', 'details': e.messages}), 400
        
    try:
        # Track subject to allow derivation when only collection changes
        subject_value = item.subject
        collection = None

        if 'title' in data:
            item.title = data['title']
        if 'subject' in data:
            subject_value = data['subject']
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
            # If subject not explicitly provided, derive from subject-type collection
            if 'subject' not in data and collection and collection.type == 'SUBJECT':
                subject_value = collection.name
            
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
        
        # Handle tags update
        # NOTE: Tags are replaced entirely, not merged. Send full list to update.
        if 'tags' in data:
            # Clear existing tags
            item.tags = []
            
            # Add new tags
            tag_names = data.get('tags', [])
            for tag_name in tag_names:
                tag_name = tag_name.strip()
                
                # Validation
                if not tag_name:
                    return jsonify({'error': 'Tag name cannot be empty'}), 400
                if len(tag_name) > 30:
                    return jsonify({'error': 'Tag name cannot exceed 30 characters'}), 400
                
                # Find or create tag (case-insensitive)
                tag = Tag.query.filter(
                    Tag.user_id == current_user_id,
                    func.lower(Tag.name) == tag_name.lower()
                ).first()
                
                if not tag:
                    tag = Tag(user_id=current_user_id, name=tag_name)
                    db.session.add(tag)
                    db.session.flush()  # Get ID
                
                item.tags.append(tag)

        # Apply subject updates after derivation logic
        if subject_value != item.subject:
            item.subject = subject_value
            
        db.session.commit()
        return jsonify(item.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Update item error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/<int:id>/rotate', methods=['PATCH'])
@jwt_required()
def rotate_image(id):
    """Update rotation for a specific image"""
    item = Item.query.get_or_404(id)
    current_user_id = get_jwt_identity()
    
    # Security: Author only
    if str(item.author_id) != str(current_user_id):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'error': 'Invalid or missing JSON body'}), 400
        
    image_index = data.get('image_index')
    if image_index is None:
        image_index = 0
    
    # Ensure image_index is an integer
    try:
        image_index = int(image_index)
    except (TypeError, ValueError):
        return jsonify({'error': 'image_index must be an integer'}), 400
        
    rotation = data.get('rotation', 0)
    
    # Validate
    if rotation not in [0, 90, 180, 270]:
        return jsonify({'error': 'Invalid rotation'}), 400
    
    # Update JSON
    if not item.images or image_index >= len(item.images):
        return jsonify({'error': 'Invalid image index'}), 400
        
    # Copy list to trigger SQLAlchemy change detection
    images = list(item.images)
    
    # Ensure image object is dict
    if not isinstance(images[image_index], dict):
        images[image_index] = {'url': images[image_index]}
    
    images[image_index]['rotation'] = rotation
    item.images = images
    flag_modified(item, 'images')
    
    # Explicitly update timestamp to ensure cache busting mechanism works
    item.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({
        'rotation': rotation,
        'image_index': image_index,
        'updated_at': item.updated_at.isoformat()
    })

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

@bp.route('/<int:id>/status', methods=['PATCH'])
@jwt_required()
def update_item_status(id):
    """Update item learning status (UNANSWERED, ANSWERED, MASTERED)"""
    current_user_id = get_jwt_identity()
    
    # Return 404 for non-owned items (hides existence)
    item = Item.query.filter_by(id=id, author_id=current_user_id).first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    # Validate request body exists
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'error': 'Request body required'}), 400
    if 'status' not in data:
        return jsonify({'error': 'status field is required'}), 400
    
    new_status = data.get('status')
    # Match DB CHECK constraint - no NEED_REVIEW
    allowed_statuses = ['UNANSWERED', 'ANSWERED', 'MASTERED']
    if new_status not in allowed_statuses:
        return jsonify({'error': f'Invalid status. Allowed: {allowed_statuses}'}), 400
    
    item.status = new_status
    db.session.commit()
    
    return jsonify({
        'status': item.status, 
        'id': item.id,
        'needs_review': item.needs_review
    }), 200

@bp.route('/<int:id>/review', methods=['PATCH'])
@jwt_required()
def toggle_review(id):
    """Toggle needs_review flag independently of status"""
    current_user_id = get_jwt_identity()
    
    item = Item.query.filter_by(id=id, author_id=current_user_id).first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({'error': 'Request body required'}), 400
    
    # Accept explicit value or toggle
    if 'needs_review' in data:
        item.needs_review = bool(data['needs_review'])
    else:
        # Toggle if no explicit value
        item.needs_review = not item.needs_review
    
    db.session.commit()
    
    return jsonify({
        'id': item.id,
        'needs_review': item.needs_review,
        'status': item.status
    }), 200

