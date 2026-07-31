import os, sys, pathlib
BASE = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
os.environ.setdefault('DJANGO_SETTINGS_MODULE','flowdesk.settings')
import django
django.setup()
from teamchat.models import Group
print('Groups with name IntegrationGroup:', Group.objects.filter(name='IntegrationGroup').count())
print('All groups:', list(Group.objects.values_list('id','name')[:20]))
