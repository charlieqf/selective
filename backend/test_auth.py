import urllib.request
import urllib.error
import json

BASE_URL = 'http://127.0.0.1:5000/api/auth'

def make_request(url, method='GET', data=None, headers=None):
    if headers is None:
        headers = {}
    
    if data:
        data = json.dumps(data).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            response_body = response.read().decode('utf-8')
            return response.status, json.loads(response_body)
    except urllib.error.HTTPError as e:
        response_body = e.read().decode('utf-8')
        try:
            return e.code, json.loads(response_body)
        except:
            return e.code, {'error': response_body}
    except Exception as e:
        return 500, {'error': str(e)}

def test_auth():
    # 1. 测试注册
    print("Testing Register...")
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    status, response = make_request(f'{BASE_URL}/register', method='POST', data=register_data)
    print(f"Register Status: {status}")
    print(f"Register Response: {response}")

    # 2. 测试登录
    print("\nTesting Login...")
    login_data = {
        "username": "testuser",
        "password": "password123"
    }
    status, response = make_request(f'{BASE_URL}/login', method='POST', data=login_data)
    print(f"Login Status: {status}")
    print(f"Login Response: {response}")
    
    if status == 200:
        return response.get('token')
    return None

def test_me(token):
    # 3. 测试获取当前用户
    print("\nTesting Get Current User...")
    headers = {'Authorization': f'Bearer {token}'}
    status, response = make_request(f'{BASE_URL}/me', method='GET', headers=headers)
    print(f"Me Status: {status}")
    print(f"Me Response: {response}")

if __name__ == "__main__":
    token = test_auth()
    if token:
        test_me(token)
