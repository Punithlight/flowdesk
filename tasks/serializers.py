from rest_framework import serializers
from .models import tasks


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = tasks
        fields = '__all__'