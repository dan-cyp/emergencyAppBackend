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
from .serializers import CitizenSerializer, EmergencyEventShortSerializer, EmergencyEventSerializer#, AccessedTimeSerializer
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

        # Log new accessedTime
        # newAccessTime = {'accessedTime': datetime.now()}
        # atSerializer = AccessedTimeSerializer(data=newAccessTime)
        # if(atSerializer.is_valid()):
        #     atSerializer.save()
        return response
    
    # @extend_schema(request=EmergencyEventShortSerializer, responses=EmergencyEventSerializer)
    # def create(self, request):
    #     serializer = EmergencyEventShortSerializer(data=request.data)
    #     if serializer.is_valid():
            
            
    #         # get LAST emergency event of CITIZEN or NONE
    #         queryset2 = EmergencyEvent.objects.all()
    #         serializer2 = EmergencyEventShortSerializer(queryset2, many=True)
    #         if(serializer2.is_valid()):
    #             allEmergencyEvents = serializer2.data
            
    #         # CREATE NEW - doesn't exist, or closed
    #         # EDIT EXISTING - Event exists and is not closed
    
    #         print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    #         print("NEW EMERGENCY: " + str(request.data))
    #         print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    #         # serializer.save()
    #         transaction.commit()

    #         # SENDING THIS MESSAGE TO WEB SOCKET CONSUMERS
    #         # Retrieve the channel layer
    #         channel_layer = get_channel_layer()
    #         group_name = "emergencyEvents"

    #         print(serializer.data)

    #         newEmergencyEventModel = EmergencyEvent.objects.get(id=serializer.data['id'])
    #         serializerNew = EmergencyEventSerializer(newEmergencyEventModel)
    #         newEmergencyEvent = serializerNew.data
    #         # this needs to be there in order to send
    #         newEmergencyEvent["type"] = "send_message"
    #         async_to_sync(channel_layer.group_send)(group_name, newEmergencyEvent)

    #         return Response(serializer.data, status=201)
    #     return Response(serializer.errors, status=400)



    @extend_schema(request=EmergencyEventShortSerializer, responses=EmergencyEventSerializer)
    def create(self, request):
        serializer = EmergencyEventShortSerializer(data=request.data)
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
                return Response(serializer.data, status=201)
            # CREATE NEW EmergencyEvent - because last was closed
            else:
                latestEmergencyEvent = emergencyEventsCitizen[len(emergencyEventsCitizen) - 1]
                # CREATE NEW
                if(latestEmergencyEvent["checked"]):
                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    print("NEW EMERGENCY: " + str(request.data))
                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    serializer.save()
                    transaction.commit()
                    return Response(serializer.data, status=201)
                # UPDATE EXISTING
                else:
                    print("SHOULD UPDATEEEEEEEE")
                    # get by id and update
                    idOfLatestEmergencyEvent = latestEmergencyEvent["id"]
                    oldPosArray = latestEmergencyEvent["posArray"]
                    emergencyEventToUpdate = self.querysetZero.get(id=idOfLatestEmergencyEvent)

                    oldPosArray = oldPosArray.replace("'", "\"")
                    python_obj = json.loads(oldPosArray)
                    python_obj.append({"lat": 5.5, "lng": 6.6})
                    python_obj_string = json.dumps(python_obj)

                    serializerToUpdate = self.serializerZero(emergencyEventToUpdate, {"posArray": python_obj_string} , partial=True)
                    serializerToUpdate.is_valid(raise_exception=True)
                    serializerToUpdate.save()
                    return Response(serializerToUpdate.data, status=201)
                    print("UPDATEEEEED SUCCESFULLY")

        return Response(serializer.errors, status=400)






# class EmergencyEventHasNewViewSet(viewsets.ViewSet):

#     def list(self, request):
#         response = {"hasNewEmergencyEvents": False}

#     #     # Get last AccessTime Point
#         atQueryset = AccessedTime.objects.all()
#         atSerializer = AccessedTimeSerializer(atQueryset.last())
#         lastAccessedTimeDb = atSerializer.data

#         #Get all EmergencyEvents
#         eeQueryset = EmergencyEvent.objects.all()
#         eeSerializer = EmergencyEventSerializer(eeQueryset, many=True)

#         if lastAccessedTimeDb is None:
#             print('No last access time')
#         else:
#             # Filter since last access time
#             accessedTimeStr = lastAccessedTimeDb['accessedTime']
#             accessedTime = datetime.strptime(accessedTimeStr, '%Y-%m-%dT%H:%M:%S.%fZ')

#             for ee in eeSerializer.data:
#                 createdDateTime = datetime.strptime(ee['createdDateTime'], '%Y-%m-%dT%H:%M:%S.%fZ')
#                 if createdDateTime > accessedTime:
#                     print(str(ee))
#                     print(accessedTime)
#                     response['hasNewEmergencyEvents'] = True
#                     return Response(response)

#         return Response(response)
    
def lobby(request):
    return render(request, 'emergencyEvent/lobby.html')