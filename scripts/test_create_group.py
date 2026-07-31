import os, sys, pathlib
# Ensure project root is on sys.path
BASE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','flowdesk.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
from django.test import Client
User = get_user_model()
username='testgroupuser'
user = User.objects.filter(username=username).first()
if not user:
    print('Creating test user')
    user = User.objects.create_user(username=username, email='test@example.com', password='testpass')
else:
    print('Test user exists')
client = Client()
client.force_login(user)
resp = client.post('/teamchat/groups/create/', data='{"name":"IntegrationGroup"}', content_type='application/json', HTTP_HOST='127.0.0.1')
print('status:', resp.status_code)
content = resp.content.decode('utf-8')
print('content (first 1000 chars):')
print(content[:1000])
