from django.db import models

class Citizen(models.Model):
    firstName = models.CharField(max_length=100)
    lastName = models.CharField(max_length=200)
    phoneNumber= models.CharField(max_length=20)

    def __str__(self):
        return self.firstName + ' ' + self.lastName

class Location(models.Model):
    lat = models.FloatField()
    lng = models.FloatField()

    def __str__(self):
        return self.lat + ", " + self.lng

class EmergencyEvent(models.Model):
    createdDateTime = models.DateTimeField(auto_now_add=True)
    checked = models.BooleanField(default=False)
    poss = models.ManyToManyField(Location)
    citizen = models.ForeignKey(Citizen, on_delete=models.CASCADE)

    def __str__(self):
        return self.citizen.lastName + ', ' + str(self.poss) + ', ' + str(self.checked)
