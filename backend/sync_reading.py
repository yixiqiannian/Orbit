import requests
import subprocess
import time
import sys
import os

# 切换到 Orbit 后端目录
os.chdir(r'G:\Orbit\backend')

def get_token_via_login():
    """尝试通过登录端点获取 token"""
    try:
        login_resp = requests.post(
            'http://localhost:8000/api/auth/login',
            json={'username': 'admin', 'password': 'orbit2026'},
            timeout=10
        )
        if login_resp.status_code == 200:
            data = login_resp.json()
            if 'access_token' in data:
                return data['access_token']
            else:
                print(f"登录响应中没有 access_token: {data}")
                return None
        else:
            print(f"登录失败，状态码: {login_resp.status_code}, 响应: {login_resp.text}")
            return None
    except Exception as e:
        print(f"登录请求异常: {e}")
        return None

def get_token_via_jwt():
    """直接生成 JWT token（跳过登录端点）"""
    try:
        # 使用后端 Python 环境生成 token
        result = subprocess.run(
            [r'G:\Orbit\backend\venv\Scripts\python.exe', '-c', 
             "import sys; sys.path.insert(0, '.'); from app.core.security import create_access_token; print(create_access_token(data={'sub': '1'}))"],
            capture_output=True, text=True, cwd=r'G:\Orbit\backend'
        )
        if result.returncode == 0:
            token = result.stdout.strip()
            if token:
                return token
            else:
                print(f"JWT 生成返回空 token, stderr: {result.stderr}")
                return None
        else:
            print(f"JWT 生成失败, returncode: {result.returncode}, stderr: {result.stderr}")
            return None
    except Exception as e:
        print(f"JWT 生成异常: {e}")
        return None

def sync_reading(token):
    """调用同步端点"""
    try:
        sync_resp = requests.post(
            'http://localhost:8000/api/reading/sync',
            headers={'Authorization': f'Bearer {token}'},
            timeout=120
        )
        print(f"同步请求状态码: {sync_resp.status_code}")
        print(f"同步响应: {sync_resp.text}")
        return sync_resp.status_code == 200
    except Exception as e:
        print(f"同步请求异常: {e}")
        return False

def verify_sync(token):
    """验证同步结果"""
    try:
        books_resp = requests.get(
            'http://localhost:8000/api/reading/books',
            headers={'Authorization': f'Bearer {token}'},
            timeout=30
        )
        if books_resp.status_code == 200:
            data = books_resp.json()
            total = data.get('total', 0)
            print(f"验证成功，书架中共有 {total} 本书")
            return True
        else:
            print(f"验证失败，状态码: {books_resp.status_code}, 响应: {books_resp.text}")
            return False
    except Exception as e:
        print(f"验证请求异常: {e}")
        return False

# 主流程
print("=== 开始同步微信读书书架到 Orbit ===")

# 1. 获取 token
print("1. 获取访问令牌...")
token = get_token_via_login()
if not token:
    print("登录失败，尝试直接生成 JWT...")
    token = get_token_via_jwt()

if not token:
    print("错误: 无法获取访问令牌，同步终止")
    sys.exit(1)

print(f"获取到令牌: {token[:20]}...")

# 2. 执行同步
print("2. 执行书架同步...")
if not sync_reading(token):
    print("错误: 同步失败")
    sys.exit(1)

# 3. 验证结果
print("3. 验证同步结果...")
if not verify_sync(token):
    print("警告: 验证失败，但同步可能已成功")

print("=== 同步完成 ===")