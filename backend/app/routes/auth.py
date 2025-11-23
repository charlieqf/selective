from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User
from app.schemas.auth import RegisterSchema, LoginSchema
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta

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
        user = User(
            username=data['username'],
            email=data['email'],
            role='student'  # TODO: Support other roles via admin API or invitation
        )
        user.set_password(data['password'])
        
        db.session.add(user)
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
        
        if user and user.check_password(data['password']):
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
