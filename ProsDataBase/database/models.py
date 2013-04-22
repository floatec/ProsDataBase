from django.db import models

class Table (models):
    name = models.CharField(max_length=100)

