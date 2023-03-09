from rest_framework import serializers

from .models import Citizen, EmergencyEvent#, AccessedTime

class CitizenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Citizen
        fields = "__all__"

class EmergencyEventShortSerializer(serializers.ModelSerializer):
    citizenId = serializers.PrimaryKeyRelatedField(
        queryset=Citizen.objects.all(),
        source="citizen",
        allow_null=True
    )
    
    pos = serializers.JSONField()
    
    class Meta:
        model = EmergencyEvent
        fields = ('id', 'pos', 'citizenId')
    
    def create(self, validated_data):
        validated_data['posArray'] = "[" + str(validated_data['pos']) + "]"
        return super().create(validated_data)

class EmergencyEventSerializer(serializers.ModelSerializer):
    citizen = CitizenSerializer()
    pos = serializers.JSONField()
    class Meta:
        model = EmergencyEvent
        fields = "__all__"