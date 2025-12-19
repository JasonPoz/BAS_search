from rest_framework import serializers
from .models import DroneTerm

class DroneTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = DroneTerm
        fields = ['id', 'term_eng', 'term_rus', 'abbr_eng', 'abbr_rus', 'definition_eng', 'definition_rus']
