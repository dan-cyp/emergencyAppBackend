from datetime import datetime

from django.shortcuts import render
from django.utils.cache import patch_cache_control
from django.db import transaction
from rest_framework import viewsets
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import Citizen, EmergencyEvent, AccessedTime
from .serializers import CitizenSerializer, EmergencyEventShortSerializer, EmergencyEventSerializer, AccessedTimeSerializer

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
    # def retrieve(self, request, pk=None):
    #     return Response(data="Hello World from Emergency App - Michalovce")

    @extend_schema(responses=EmergencyEventSerializer)
    def list(self, request):
        queryset = EmergencyEvent.objects.all()
        serializer = EmergencyEventSerializer(queryset, many=True)
        response = Response(serializer.data)
        return response
    
    @extend_schema(request=EmergencyEventShortSerializer, responses=EmergencyEventSerializer)
    def create(self, request):
        serializer = EmergencyEventShortSerializer(data=request.data)
        if serializer.is_valid():
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("EMERGENCY: " + str(request.data))
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            serializer.save()
            transaction.commit()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class EmergencyEventRecentViewSet(viewsets.ViewSet):

    @extend_schema(responses=EmergencyEventSerializer)
    def list(self, request):
        # Get last AccessTime Point
        atQueryset = AccessedTime.objects.all()
        atSerializer = AccessedTimeSerializer(atQueryset.last())
        lastAccessedTimeDb = atSerializer.data

        # Get all EmergencyEvents
        eeQueryset = EmergencyEvent.objects.all()
        eeSerializer = EmergencyEventSerializer(eeQueryset, many=True)

        if lastAccessedTimeDb is None:
            print('No last access time')
        else:
            # Filter since last access time
            accessedTimeStr = lastAccessedTimeDb['accessedTime']
            accessedTime = datetime.strptime(accessedTimeStr, '%Y-%m-%dT%H:%M:%S.%fZ')

            newEmergencyEvents = []
            for ee in eeSerializer.data:
                createdDateTime = datetime.strptime(ee['createdDateTime'], '%Y-%m-%dT%H:%M:%S.%fZ')
                if createdDateTime > accessedTime:
                    newEmergencyEvents.append(ee)

            # Log new accessedTime
            newAccessTime = {'accessedTime': datetime.now()}
            atSerializer = AccessedTimeSerializer(data=newAccessTime)
            if(atSerializer.is_valid()):
                atSerializer.save()

            return Response(newEmergencyEvents)
                
        
        # Log new accessedTime
        newAccessTime = {'accessedTime': datetime.now()}
        atSerializer = AccessedTimeSerializer(data=newAccessTime)
        if(atSerializer.is_valid()):
            atSerializer.save()
        return Response(eeSerializer.data)