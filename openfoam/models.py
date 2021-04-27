from django.db import models
from django.conf import settings

# Create your models here.


class SimulationModel(models.Model):
    name = models.CharField(max_length=100, null=False, unique=True)
    type = models.CharField(max_length=100, null=False)
    file_name = models.CharField(max_length=100, null=False)
    status = models.CharField(max_length=10, null=False)
    rn = models.IntegerField(null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,null=False)


class ResultsModel(models.Model):
    simulation_id = models.IntegerField(null=False)
    name = models.CharField(max_length=100, null=False, unique=True)
    ca1 = models.DecimalField(max_digits=10, decimal_places=6, null=True)
    ca2 = models.DecimalField(max_digits=10, decimal_places=6, null=True)
    ce1 = models.DecimalField(max_digits=10, decimal_places=6, null=True)
    ce2 = models.DecimalField(max_digits=10, decimal_places=6, null=True)
    predicted_lift = models.DecimalField(max_digits=10, decimal_places=6, null=True)
    predicted_drag = models.DecimalField(max_digits=10, decimal_places=6, null=True)
    actual_lift = models.DecimalField(max_digits=10, decimal_places=6, null=True)
    actual_drag = models.DecimalField(max_digits=10, decimal_places=6, null=True)
    aoa = models.IntegerField(null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
