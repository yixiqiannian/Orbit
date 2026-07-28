import sys
sys.path.insert(0, '.')
from app.core.security import create_access_token
token = create_access_token(data={'sub': '1'})
print(token)
