from django.db import models

class Citizen(models.Model):
    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=200)
    #registered = models.DateTimeField(auto_now_add=True)
    phoneNumber= models.CharField(max_length=20)

    def __str__(self):
        return self.firstName + ' ' + self.lastName


class EmergencyEvent(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    createdDateTime = models.DateTimeField(auto_now_add=True)
    citizen = models.ForeignKey(Citizen, on_delete=models.CASCADE)

    def __str__(self):
        return self.citizen.lastName + ', ' + str(self.latitude) + ', ' + str(self.longitude)
