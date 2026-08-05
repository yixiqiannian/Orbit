import sys
sys.path.insert(0, '.')
from app.core.config import settings
print('WEREAD_API_KEY configured:', bool(settings.WEREAD_API_KEY))
