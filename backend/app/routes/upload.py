from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import cloudinary.uploader
import cloudinary.api
from app import db
from app.models.pending_upload import PendingUpload
from app.models.item import Item

bp = Blueprint('upload', __name__, url_prefix='/api/upload')

# Trigger redeploy for 15MB limit fix
print("--- UPLOAD BLUEPRINT LOADED (15MB Fix v2) ---", flush=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

import inspect
import os

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/debug-info', methods=['GET'])
def debug_info():
    """Debug endpoint to verify runtime code"""
    import sys
    try:
        source = inspect.getsource(upload_image)
    except:
        source = "Could not get source"
        
    return jsonify({
        "status": "active",
        "file": __file__,
        "cwd": os.getcwd(),
        "source_snippet": source[:500],
        "size_limit_check": "15MB" if "15 *" in source else "Unknown",
        "blueprint_prefix": bp.url_prefix
    })

@bp.route('', methods=['POST'])
@jwt_required()
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        try:
            # Check file size
            file.seek(0, 2)
            size = file.tell()
            file.seek(0)
            
            print(f"File upload: {file.filename}, Size: {size} bytes", flush=True)
            
            if size > 15 * 1024 * 1024: # 15MB
                return jsonify({'error': f'File too large (max 15MB), got {size/1024/1024:.2f}MB'}), 400
            
            current_user_id = get_jwt_identity()
            
            upload_result = cloudinary.uploader.upload(
                file,
                folder="selective-questions",
                resource_type="image"
            )
            
            # Track this upload in database (multi-worker safe)
            public_id = upload_result['public_id']
            pending_upload = PendingUpload(
                public_id=public_id,
                user_id=int(current_user_id)
            )
            db.session.add(pending_upload)
            db.session.commit()
            
            # Cleanup expired uploads periodically (async in production)
            try:
                PendingUpload.cleanup_expired()
            except Exception as e:
                print(f"Cleanup warning: {e}")
            
            return jsonify({
                'url': upload_result['secure_url'],
                'public_id': public_id
            }), 201
            
        except Exception as e:
            db.session.rollback()
            print(f"Upload error: {str(e)}")
            return jsonify({'error': 'Upload failed'}), 500
            
    return jsonify({'error': 'Invalid file type'}), 400

@bp.route('', methods=['DELETE'])
@jwt_required()
def delete_image():
    data = request.get_json()
    public_id = data.get('public_id')
    
    if not public_id:
        return jsonify({'error': 'public_id is required'}), 400
    
    current_user_id = get_jwt_identity()
    
    try:
        # Check if image belongs to user's items (formerly questions)
        items = Item.query.filter_by(author_id=current_user_id).all()
        
        image_found = False
        for item in items:
            images = item.get_images()
            for img in images:
                if img.get('public_id') == public_id:
                    image_found = True
                    break
            if image_found:
                break
        
        # If not in items, check pending uploads (DB-backed, multi-worker safe)
        pending_upload = None
        if not image_found:
            # Verify prefix first
            if not public_id.startswith('selective-questions/'):
                return jsonify({'error': 'Unauthorized: Invalid public_id'}), 403
            
            # Check database for pending upload
            pending_upload = PendingUpload.query.filter_by(public_id=public_id).first()
            if pending_upload:
                # Verify the user owns this pending upload
                if str(pending_upload.user_id) != str(current_user_id):
                    return jsonify({'error': 'Unauthorized: You cannot delete this image'}), 403
                # Don't delete from DB yet - wait for Cloudinary success
            else:
                # Not in items and not in pending uploads - unauthorized
                return jsonify({'error': 'Unauthorized: Image not found or does not belong to you'}), 403
        
        # Delete from Cloudinary FIRST
        result = cloudinary.uploader.destroy(public_id)
        if result.get('result') == 'ok' or result.get('result') == 'not found':
            # Only now remove from database (if it was a pending upload)
            if not image_found and pending_upload:
                db.session.delete(pending_upload)
                db.session.commit()
            return jsonify({'message': 'Image deleted successfully'}), 200
        else:
            # Cloudinary failed - don't touch database, user can retry
            return jsonify({'error': 'Failed to delete image from storage'}), 400
            
    except Exception as e:
        db.session.rollback()
        print(f"Delete image error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
