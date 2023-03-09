from rest_framework import serializers

from .models import Citizen, EmergencyEvent, Location#, AccessedTime

class CitizenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Citizen
        fields = "__all__"

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"

class EmergencyEventReceiveSerializer(serializers.ModelSerializer):
    citizenId = serializers.IntegerField()

    pos = serializers.JSONField()

    class Meta:
        model = EmergencyEvent
        fields = ('id', 'pos', 'citizenId')

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
        fields = ('id', 'citizen', 'poss', 'createdDateTime', 'checked')
    
    def update(self, instance, validated_data):
        poss_data = validated_data.pop('poss', None)
        if poss_data is not None and len(poss_data) > 0:
            pos = poss_data[-1]
            location = Location.objects.create(**pos)
            instance.poss.add(location)  # add the new location to the event
        return super().update(instance, validated_data)
