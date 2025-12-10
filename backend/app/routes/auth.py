from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User
from app.models.collection import Collection
from app.schemas.auth import RegisterSchema, LoginSchema
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
from config import Config

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # 1. 输入验证
    schema = RegisterSchema()
    errors = schema.validate(data)
    if errors:
        return jsonify({'error': 'Validation failed', 'details': errors}), 400
        
    # 2. 业务逻辑检查
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409
        
    try:
        # 3. 创建用户
        # Validate and use role from request, default to 'student' if invalid
        ALLOWED_ROLES = ['student', 'parent', 'tutor']
        role = data.get('role', 'student')
        if role not in ALLOWED_ROLES:
            role = 'student'
        
        user = User(
            username=data['username'],
            email=data['email'],
            role=role
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Create default collections
        for subject_key, subject_info in Config.SUBJECTS.items():
            collection = Collection(
                user_id=user.id,
                name=subject_info['name'],
                type='SUBJECT',
                icon=subject_info['icon'],
                color=subject_info['color']
            )
            db.session.add(collection)
        db.session.commit()
        
        # 4. 生成Token
        access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=7))
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'token': access_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        # Log the full error server-side here
        print(f"Registration error: {str(e)}") 
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # 1. 输入验证
    schema = LoginSchema()
    errors = schema.validate(data)
    if errors:
        return jsonify({'error': 'Validation failed', 'details': errors}), 400
        
    try:
        user = User.query.filter_by(username=data['username']).first()
        
        if not user:
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Block password login for Google-only users
        if user.auth_provider == 'google' and user.password_hash is None:
            return jsonify({'error': 'This account uses Google Sign-In. Please sign in with Google.'}), 401
        
        if user.check_password(data['password']):
            access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=7))
            
            return jsonify({
                'message': 'Login successful',
                'user': user.to_dict(),
                'token': access_token
            }), 200
            
        return jsonify({'error': 'Invalid username or password'}), 401
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    return jsonify(user.to_dict()), 200


@bp.route('/google', methods=['POST'])
def google_login():
    """
    Google OAuth login endpoint.
    Receives Google ID token, validates it, and creates/links user account.
    """
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests
    
    data = request.get_json()
    
    # 1. Validate request
    credential = data.get('credential') if data else None
    if not credential:
        return jsonify({'error': 'Missing credential'}), 400
    
    # 2. Verify CSRF token (from cookie and body)
    # Note: In development (localhost), Google may not set the g_csrf_token cookie
    # So we make this check optional when both are missing
    csrf_token_cookie = request.cookies.get('g_csrf_token')
    csrf_token_body = data.get('g_csrf_token')
    
    # Only enforce CSRF if at least one token is present (production behavior)
    if csrf_token_cookie or csrf_token_body:
        if not csrf_token_cookie or not csrf_token_body:
            return jsonify({'error': 'Missing CSRF token'}), 400
        if csrf_token_cookie != csrf_token_body:
            return jsonify({'error': 'Invalid CSRF token'}), 400
    
    # 3. Verify Google ID token
    try:
        idinfo = id_token.verify_oauth2_token(
            credential, 
            google_requests.Request(), 
            Config.GOOGLE_CLIENT_ID
        )
    except ValueError as e:
        return jsonify({'error': 'Invalid Google token', 'details': str(e)}), 401
    
    # 4. Validate issuer
    if idinfo.get('iss') not in ['accounts.google.com', 'https://accounts.google.com']:
        return jsonify({'error': 'Invalid token issuer'}), 401
    
    # 5. Require verified email
    if not idinfo.get('email_verified', False):
        return jsonify({'error': 'Email not verified with Google'}), 401
    
    # 6. Extract user info
    google_id = idinfo['sub']
    email = idinfo['email']
    name = idinfo.get('name', email.split('@')[0])
    picture = idinfo.get('picture')
    
    try:
        # 7. Find or create user with account linking logic
        user = User.query.filter_by(google_id=google_id).first()
        
        if user:
            # Existing Google user - update avatar if changed
            if picture:
                user.avatar_url = picture
        else:
            # Check if email exists (account linking case)
            existing_by_email = User.query.filter_by(email=email).first()
            
            if existing_by_email:
                # Check for conflicting google_id on another account
                if existing_by_email.google_id and existing_by_email.google_id != google_id:
                    return jsonify({'error': 'This email is linked to a different Google account'}), 409
                
                # Link Google to existing account
                existing_by_email.google_id = google_id
                existing_by_email.avatar_url = picture
                # Keep auth_provider as 'local' - user can use both methods
                user = existing_by_email
            else:
                # Create new user with unique username
                username = generate_unique_username(name)
                user = User(
                    username=username,
                    email=email,
                    google_id=google_id,
                    auth_provider='google',
                    avatar_url=picture,
                    role='student'
                )
                db.session.add(user)
                db.session.flush()  # Get user.id for collections
                
                # Create default collections (same as register)
                for subject_key, subject_info in Config.SUBJECTS.items():
                    collection = Collection(
                        user_id=user.id,
                        name=subject_info['name'],
                        type='SUBJECT',
                        icon=subject_info['icon'],
                        color=subject_info['color']
                    )
                    db.session.add(collection)
        
        db.session.commit()
        
        # 8. Return JWT token
        access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=7))
        return jsonify({'user': user.to_dict(), 'token': access_token}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Google login error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


def generate_unique_username(name: str) -> str:
    """
    Generate a unique username from a name.
    Uses deterministic suffixing to guarantee uniqueness.
    """
    import re
    import random
    import string
    import uuid
    
    # Sanitize: lowercase, alphanumeric only
    base = re.sub(r'[^a-z0-9]', '', name.lower())
    if len(base) < 3:
        base = 'user'
    base = base[:20]  # Limit length
    
    # Try base first
    if not User.query.filter_by(username=base).first():
        return base
    
    # Try with random suffix (up to 10 attempts)
    for _ in range(10):
        suffix = ''.join(random.choices(string.digits, k=4))
        candidate = f"{base}{suffix}"
        if not User.query.filter_by(username=candidate).first():
            return candidate
    
    # Fallback: UUID-based (guaranteed unique)
    return f"{base}_{uuid.uuid4().hex[:8]}"

