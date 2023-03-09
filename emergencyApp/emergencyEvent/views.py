import json
from datetime import datetime

from django.shortcuts import render
from django.utils.cache import patch_cache_control
from django.db import transaction
from django.forms.models import model_to_dict
from rest_framework import viewsets
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Citizen, EmergencyEvent#, AccessedTime
from .serializers import CitizenSerializer, EmergencyEventReceiveSerializer, EmergencyEventSerializer#, AccessedTimeSerializer
from .consumers import EmergencyEventConsumer

class CitizenViewSet(viewsets.ViewSet):

    @extend_schema(responses=CitizenSerializer)
    def list(self, request):
        queryset = Citizen.objects.all()
        serializer = CitizenSerializer(queryset, many=True)
        response = Response(serializer.data)
        return response

    @extend_schema(request=CitizenSerializer, responses=CitizenSerializer)
    def create(self, request):
        serializer = CitizenSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            transaction.commit()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class EmergencyEventViewSet(viewsets.ViewSet):

    querysetZero = EmergencyEvent.objects.all()
    serializerZero = EmergencyEventSerializer

    @extend_schema(responses=EmergencyEventSerializer)
    def list(self, request):
        queryset = EmergencyEvent.objects.all()
        serializer = EmergencyEventSerializer(queryset, many=True)
        response = Response(serializer.data)

        return response

    @extend_schema(request=EmergencyEventReceiveSerializer, responses=EmergencyEventSerializer)
    def create(self, request):
        serializer = EmergencyEventReceiveSerializer(data=request.data)
        if serializer.is_valid():

            citizenId = request.data["citizenId"]

            #Get all EmergencyEvents
            eeQueryset = EmergencyEvent.objects.all()
            eeSerializer = EmergencyEventSerializer(eeQueryset, many=True)
            emergencyEventsAll = eeSerializer.data 
            emergencyEventsCitizen = []
            for ee in emergencyEventsAll:
                if ee["citizen"]["id"] == citizenId:
                    emergencyEventsCitizen.append(ee)

            # CREATE NEW EmergencyEvent - nothing yet there
            if len(emergencyEventsCitizen) == 0:
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print("NEW EMERGENCY: " + str(request.data))
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                serializer.save()
                transaction.commit()
                # notify channels!!! <-- HERE -->
                return Response(serializer.data, status=201)
            else:
                latestEmergencyEvent = emergencyEventsCitizen[len(emergencyEventsCitizen) - 1]
                # CREATE NEW EmergencyEvent - because last was closed
                if(latestEmergencyEvent["checked"]):
                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    print("NEW EMERGENCY: " + str(request.data))
                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    serializer.save()
                    transaction.commit()
                    # notify channels!!! <-- HERE -->
                    return Response(serializer.data, status=201)
                # UPDATE EXISTING
                else:
                    print("SHOULD UPDATEEEEEEEE")
                    # get by id and update
                    idOfLatestEmergencyEvent = latestEmergencyEvent["id"]
                    poss = latestEmergencyEvent["poss"]
                    newPos = request.data["pos"]
                    poss.append(newPos)

                    emergencyEventToUpdate = self.querysetZero.get(id=idOfLatestEmergencyEvent)

                    serializerToUpdate = self.serializerZero(emergencyEventToUpdate, {"poss": poss} , partial=True)
                    serializerToUpdate.is_valid(raise_exception=True)
                    serializerToUpdate.save()
                    print("UPDATEEEEED SUCCESFULLY")
                    return Response(serializerToUpdate.data, status=200)

        return Response(serializer.errors, status=400)
    
def lobby(request):
    return render(request, 'emergencyEvent/lobby.html')