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
resp = client.post('/teamchat/groups/create/', data='{"name":"IntegrationGroup"}', content_type='application/json')
print('status:', resp.status_code)
print(resp.content.decode('utf-8'))
