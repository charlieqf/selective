import requests
import sys

BASE_URL = "http://localhost:5000/api"

def run_test():
    print("1. Register/Login...")
    # Register a test user
    auth_data = {
        "username": "test_learner",
        "email": "learner@test.com",
        "password": "password123",
        "role": "student"
    }
    
    # Try login first
    session = requests.Session()
    resp = session.post(f"{BASE_URL}/auth/login", json={
        "username": auth_data["username"],
        "password": auth_data["password"]
    })
    
    if resp.status_code != 200:
        # Try register
        resp = session.post(f"{BASE_URL}/auth/register", json=auth_data)
        if resp.status_code != 201:
            print(f"Auth failed: {resp.text}")
            return
            
    token = resp.json()['token']
    headers = {"Authorization": f"Bearer {token}"}
    print("   Auth successful.")

    print("\n2. Create a Question...")
    # Create a dummy question
    q_data = {
        "title": "Test Question for Answering",
        "subject": "MATHS",
        "difficulty": 3,
        "content_text": "What is 2+2?",
        "images": [] # Optional for this test
    }
    resp = requests.post(f"{BASE_URL}/questions", json=q_data, headers=headers)
    if resp.status_code != 201:
        print(f"Create question failed: {resp.text}")
        return
    
    q_id = resp.json()['id']
    print(f"   Question created. ID: {q_id}")

    print("\n3. Submit INCORRECT Answer...")
    ans_data = {
        "is_correct": False,
        "content": "5",
        "duration_seconds": 10
    }
    resp = requests.post(f"{BASE_URL}/questions/{q_id}/answers", json=ans_data, headers=headers)
    if resp.status_code != 201:
        print(f"Submit answer failed: {resp.text}")
        return
    
    status = resp.json()['question_status']
    print(f"   Answer submitted. New Status: {status}")
    if status != 'NEED_REVIEW':
        print("   FAIL: Status should be NEED_REVIEW")
    else:
        print("   PASS: Status is NEED_REVIEW")

    print("\n4. Get Review Session...")
    resp = requests.get(f"{BASE_URL}/questions/review-session", headers=headers)
    if resp.status_code != 200:
        print(f"Get review session failed: {resp.text}")
        return
    
    review_list = resp.json()
    print(f"   Got {len(review_list)} questions for review.")
    
    found = any(q['id'] == q_id for q in review_list)
    if found:
        print("   PASS: Question found in review session.")
    else:
        print("   FAIL: Question NOT found in review session.")

    print("\n5. Submit CORRECT Answer...")
    ans_data = {
        "is_correct": True,
        "content": "4",
        "duration_seconds": 5
    }
    resp = requests.post(f"{BASE_URL}/questions/{q_id}/answers", json=ans_data, headers=headers)
    
    status = resp.json()['question_status']
    print(f"   Answer submitted. New Status: {status}")
    if status != 'MASTERED':
        print("   FAIL: Status should be MASTERED")
    else:
        print("   PASS: Status is MASTERED")

if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        print(f"Test failed with exception: {e}")
