import json
from datetime import datetime

from django.shortcuts import render
from django.utils.cache import patch_cache_control
from django.db import transaction
from django.forms.models import model_to_dict

from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Citizen, EmergencyEvent#, AccessedTime
from .serializers import CitizenSerializer, EmergencyEventReceiveSerializer, EmergencyEventSerializer, EmergencyEventConfirmationSerializer
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


            # Retrieve the channel layer
            channel_layer = get_channel_layer()
            group_name = "emergencyEvents"


            citizenId = request.data["citizenId"]

            #Get all EmergencyEvents
            eeQueryset = EmergencyEvent.objects.all()
            eeSerializer = EmergencyEventSerializer(eeQueryset, many=True)
            emergencyEventsAll = eeSerializer.data 
            emergencyEventsCitizen = []
            for ee in emergencyEventsAll:
                if ee["citizen"]["id"] == citizenId:
                    emergencyEventsCitizen.append(ee)
            
            latestEmergencyEvent = None
            if len(emergencyEventsCitizen) > 0:
                latestEmergencyEvent = emergencyEventsCitizen[len(emergencyEventsCitizen) - 1]

            # CREATE NEW EmergencyEvent - nothing yet there
            if latestEmergencyEvent == None or len(emergencyEventsCitizen) == 0 or latestEmergencyEvent["checked"]:
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print("NEW EMERGENCY: " + str(request.data))
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

                event = serializer.create(serializer.validated_data)
                response_serializer = EmergencyEventSerializer(event)

                # notify channels!!! 
                newEmergencyEvent = response_serializer.data
                # this needs to be there in order to send
                newEmergencyEvent["type"] = "send_message"
                async_to_sync(channel_layer.group_send)(group_name, newEmergencyEvent)

                return Response(response_serializer.data, status=201)
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
                # notify channels!!! 
                newEmergencyEvent = serializerToUpdate.data
                # this needs to be there in order to send
                newEmergencyEvent["type"] = "send_message"
                async_to_sync(channel_layer.group_send)(group_name, newEmergencyEvent)
                print("UPDATEEEEED SUCCESFULLY")
                return Response(serializerToUpdate.data, status=200)

        return Response(serializer.errors, status=400)

class EmergencyEventConfirmationViewSet(viewsets.ViewSet):
    serializer_class = EmergencyEventConfirmationSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return JsonResponse({"message": "Successfully confirmed event"})

def lobby(request):
    return render(request, 'emergencyEvent/lobby.html')