from django.db import models

class Citizen(models.Model):
    firstName = models.CharField(max_length=255)
    lastName = models.CharField(max_length=255)
    phoneNumber= models.CharField(max_length=20)

    def __str__(self):
        return self.firstName + ' ' + self.lastName

class Location(models.Model):
    lat = models.FloatField()
    lng = models.FloatField()

    def __str__(self):
        return self.lat + ", " + self.lng

class EmergencyEvent(models.Model):
    citizen = models.ForeignKey(Citizen, on_delete=models.CASCADE)
    poss = models.ManyToManyField(Location)
    createdDateTime = models.DateTimeField(auto_now_add=True)
    checked = models.BooleanField(default=False)

    def __str__(self):
        return self.citizen.lastName + ', ' + str(self.poss) + ', ' + str(self.checked)
