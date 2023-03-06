from django.shortcuts import render
from django.utils.cache import patch_cache_control
from django.db import transaction
from rest_framework import viewsets
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import Citizen, EmergencyEvent
from .serializers import CitizenSerializer, EmergencyEventShortSerializer, EmergencyEventSerializer

class CitizenViewSet(viewsets.ViewSet):
    queryset = Citizen.objects.all()

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

    queryset = EmergencyEvent.objects.all()

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
            print("EMERGENCY: ")
            print(request.data)
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            serializer.save()
            transaction.commit()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


