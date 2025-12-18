"""
Check user account and optionally set password for Google OAuth user
"""
from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    email = 'charlieqf@gmail.com'
    user = User.query.filter_by(email=email).first()
    
    if not user:
        print(f"❌ No user found with email: {email}")
    else:
        print(f"✅ Found user:")
        print(f"   ID: {user.id}")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Auth Provider: {user.auth_provider}")
        print(f"   Has Password: {user.password_hash is not None}")
        
        if user.password_hash is None:
            print("\n⚠️  This is a Google-only account without a password.")
            print("   Setting password to 'password123'...")
            user.set_password('password123')
            db.session.commit()
            print("✅ Password set successfully!")
            print(f"\n📝 You can now login with:")
            print(f"   Username: {user.username}")
            print(f"   Password: password123")
        else:
            print("\n✅ This account already has a password set.")
            print("   If you forgot it, we can reset it.")
            # Uncomment to reset:
            # user.set_password('password123')
            # db.session.commit()
            # print("Password reset to: password123")
