# forms.py
from django import forms
from .models import *

class FloorPlanForm(forms.ModelForm):

    class Meta:
        model = FloorPlan
        fields = ['name', 'floorplan_img']
