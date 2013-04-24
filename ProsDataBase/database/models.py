from django.db import models

class Table(models.Model):
    id = models.IntegerField
    name = models.CharField(max_length=100)
#    columns = DataDescr[]
#    datasets = Dataset[]
#    references = Reference[]

class DataDescr(models.Model):
    id = models.IntegerField
    name = models.CharField(max_length=100)
    table = models.ForeignKey(Table)
    type = models.ForeignKey(Datatype)
    required = models.BooleanField

class Dataset(models.Model):
    id = models.IntegerField
#    data = Data[]
    table = models.ForeignKey(Table)
    created = models.DateTimeField
    deleted = models.DateTimeField
    creator = models.ForeignKey(User)
    deleter = models.ForeignKey(User)

class Data(models.Model):
    id = models.IntegerField
    column = models.ForeignKey(DataDescr)
    value = models.ForeignKey(Datatype)
    created = models.DateTimeField
    deleted = models.DateTimeField
    creator = models.ForeignKey(User)
    deleter = models.ForeignKey(User)

class Datatype(models.Model):
    pass

class Text(Datatype):
    content = models.CharField(max_length=200)
    length = models.IntegerField

class Numeric(Datatype):
    content = models.FloatField
    min = models.FloatField
    max = models.FloatField

class Selection(Datatype):
#    values = models.Field ??
    length = models.IntegerField

class Date(Datatype):
    content = models.DateTimeField
    min = models.DateTimeField
    max = models.DateTimeField

class Reference(models.Model):
    table1 = models.ForeignKey(Table)
    table2 = models.ForeignKey(Table)
#    match = models.Map ??

class User(models.Model):
    id = models.IntegerField
    name = models.CharField(max_length=100)
#    groups = Group[]
    rights = models.ForeignKey(RightList)

class Group(models.Model):
    name = models.CharField(max_length=100)
#    admin = User[]
    rights = models.ForeignKey(RightList)
class RightList(models.Model):
    table = models.ForeignKey(Table)
#    read = DataDescr[]
#    insert = DataDescr[]
#    modify = DataDescr[]
#    delete = DataDescr[]
    viewLog = models.BooleanField
    rightsAdmin = models.BooleanField