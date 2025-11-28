"""
Seed script to create test data for E2E tests
Run this before running Playwright tests to ensure data exists
"""
from app import create_app, db
from app.models.user import User
from app.models.question import Question
from werkzeug.security import generate_password_hash

def seed_test_data():
    app = create_app()
    
    with app.app_context():
        # Check if testuser exists
        user = User.query.filter_by(username='testuser').first()
        
        if not user:
            print("Creating testuser...")
            user = User(
                username='testuser',
                email='test@example.com',
                password_hash=generate_password_hash('password'),
                role='student'
            )
            db.session.add(user)
            db.session.commit()
            print("✓ testuser created")
        else:
            print("✓ testuser already exists")
        
        # Create some test questions if they don't exist
        question_count = Question.query.filter_by(author_id=user.id).count()
        
        if question_count < 5:
            print(f"Creating test questions (current: {question_count})...")
            
            subjects = ['MATHS', 'READING', 'WRITING', 'THINKING_SKILLS']
            for i in range(5 - question_count):
                question = Question(
                    author_id=user.id,
                    subject=subjects[i % len(subjects)],
                    difficulty=((i % 5) + 1),
                    title=f'Test Question {i + question_count + 1}',
                    content_text=f'This is test question content {i + question_count + 1}',
                    images=[]
                )
                db.session.add(question)
            
            db.session.commit()
            print(f"✓ Created {5 - question_count} test questions")
        else:
            print(f"✓ Already have {question_count} test questions")
        
        print("\n✅ Test data ready!")
        print(f"   User: testuser / password")
        print(f"   Questions: {Question.query.filter_by(author_id=user.id).count()}")

if __name__ == '__main__':
    seed_test_data()
