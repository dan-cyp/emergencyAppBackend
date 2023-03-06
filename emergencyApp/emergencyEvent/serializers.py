from rest_framework import serializers

from .models import Citizen, EmergencyEvent

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
    class Meta:
        model = EmergencyEvent
        fields = ('id', 'latitude', 'longitude', 'citizenId')


class EmergencyEventSerializer(serializers.ModelSerializer):
    citizen = CitizenSerializer()
    class Meta:
        model = EmergencyEvent
        fields = "__all__"