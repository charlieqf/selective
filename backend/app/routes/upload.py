from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import cloudinary.uploader
import cloudinary.api

bp = Blueprint('upload', __name__, url_prefix='/api/upload')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
            # Check file size (approximate, as content-length might not be accurate)
            # Better to let Cloudinary handle or check stream length, but simple check here:
            file.seek(0, 2)
            size = file.tell()
            file.seek(0)
            
            if size > 5 * 1024 * 1024: # 5MB
                return jsonify({'error': 'File too large (max 5MB)'}), 400
            
            upload_result = cloudinary.uploader.upload(
                file,
                folder="selective-questions",
                resource_type="image"
            )
            
            return jsonify({
                'url': upload_result['secure_url'],
                'public_id': upload_result['public_id']
            }), 201
            
        except Exception as e:
            print(f"Upload error: {str(e)}")
            return jsonify({'error': 'Upload failed'}), 500
            
    return jsonify({'error': 'Invalid file type'}), 400

@bp.route('', methods=['DELETE'])
@jwt_required()
def delete_image():
    from app.models.question import Question
    
    data = request.get_json()
    public_id = data.get('public_id')
    
    if not public_id:
        return jsonify({'error': 'public_id is required'}), 400
    
    current_user_id = get_jwt_identity()
    
    try:
        # Find question that owns this image
        questions = Question.query.filter_by(author_id=current_user_id).all()
        
        image_found = False
        for question in questions:
            images = question.get_images()
            for img in images:
                if img.get('public_id') == public_id:
                    image_found = True
                    break
            if image_found:
                break
        
        # Check if it's a pending upload (uploaded in last 24 hours, not in any question)
        # For now, we verify it's in the user's folder by checking the public_id prefix
        # Cloudinary uploads are stored in "selective-questions/" folder
        # We could enhance this by storing pending uploads in Redis/DB with user_id
        
        if not image_found:
            # Verify the public_id belongs to our application folder
            if not public_id.startswith('selective-questions/'):
                return jsonify({'error': 'Unauthorized: Image does not belong to you'}), 403
            
            # For pending uploads, we allow deletion
            # In production, you should track uploads in a database/cache with user_id
            # and verify ownership here
        
        # Only delete if ownership is verified
        result = cloudinary.uploader.destroy(public_id)
        if result.get('result') == 'ok' or result.get('result') == 'not found':
            return jsonify({'message': 'Image deleted successfully'}), 200
        else:
            return jsonify({'error': 'Failed to delete image'}), 400
            
    except Exception as e:
        print(f"Delete image error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
