from django.db import models

class FloorPlan(models.Model):
    name = models.CharField(max_length = 50)
    floorplan_img = models.ImageField(upload_to='images/background')
