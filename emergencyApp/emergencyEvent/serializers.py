from rest_framework import serializers
from django.shortcuts import get_object_or_404

from .models import Citizen, EmergencyEvent, Location#, AccessedTime

class CitizenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Citizen
        fields = "__all__"
        read_only_fields = ['id']

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"
        read_only_fields = ['id']

class EmergencyEventReceiveSerializer(serializers.ModelSerializer):
    citizenId = serializers.IntegerField()

    pos = serializers.JSONField()

    class Meta:
        model = EmergencyEvent
        fields = ['id', 'citizenId', 'pos']

    def create(self, validated_data):
        citizen_id = validated_data.pop('citizenId')
        citizen = Citizen.objects.get(id=citizen_id)
        pos_data = validated_data.pop('pos')
        event = EmergencyEvent.objects.create(citizen=citizen, **validated_data)
        for loc_data in pos_data.values():
            location = Location.objects.create(**loc_data)
            event.poss.add(location)
        return event


class EmergencyEventSerializer(serializers.ModelSerializer):
    citizen = CitizenSerializer()
    poss = LocationSerializer(many=True)

    class Meta:
        model = EmergencyEvent
        fields = ['id', 'citizen', 'poss', 'createdDateTime', 'checked']
        read_only_fields = ['id', 'citizen', 'poss', 'createdDateTime']
    
    def update(self, instance, validated_data):
        poss_data = validated_data.pop('poss', None)
        if poss_data is not None and len(poss_data) > 0:
            pos = poss_data[-1]
            location = Location.objects.create(**pos)
            instance.poss.add(location)  # add the new location to the event
        return super().update(instance, validated_data)

class EmergencyEventConfirmationSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    def create(self, validated_data):
        emergency_event_id = validated_data.pop('id')
        emergency_event = get_object_or_404(EmergencyEvent, id=emergency_event_id)
        emergency_event.checked = validated_data.get('checked', True)
        emergency_event.save()
        return emergency_event