from django.db import models
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType

# -- Table structure


class DataDescr(models.Model):
    id = models.IntegerField()
    name = models.CharField(max_length=100)
    table = models.ForeignKey('Table.id')
    type = models.ForeignKey('Datatype.id')
    required = models.BooleanField()

    def data(self):
        Data.objects.filter(dataset=self.id)


class Reference(models.Model):
    column1 = models.ForeignKey('DataDescr.id')
    column2 = models.ForeignKey('DataDescr.id')


class Dataset(models.Model):
    id = models.IntegerField()
    table = models.ForeignKey('Table.id')
    created = models.DateTimeField()
    deleted = models.DateTimeField()
    creator = models.ForeignKey('User.id')
    deleter = models.ForeignKey('User.id')


class Table(models.Model):
    id = models.IntegerField()
    name = models.CharField(max_length=100)

    def dataDescrs(self):
        DataDescr.objects.filter(table=self.id)

    def datasets(self):
        Dataset.objects.filter(table=self.id)

    def references(self):
        Reference.objects.filter(table1=self.id)


# -- Data fields


class Data(models.Model):
    id = models.IntegerField
    column = models.ForeignKey(DataDescr.id)
    dataset = models.ForeignKey(Dataset.id)
    content = models.Field  # TODO
    created = models.DateTimeField()
    deleted = models.DateTimeField()
    creator = models.ForeignKey(User.id)
    deleter = models.ForeignKey(User.id)


class TextData(Data):
    content = models.TextField()


class NumericData(Data):
    content = models.FloatField()


class SelectionData(Data):
    content = models.ForeignKey(SelectionValue.id)


class DateData(Data):
    content = models.DateTimeField()


# -- data types


class Datatype(models.Model):
    id = models.IntegerField()


class TextType(Datatype):
    length = models.IntegerField()


class NumericType(Datatype):
    min = models.FloatField()
    max = models.FloatField()


class SelectionValue(models.Model):
    selectionType = models.ForeignKey(SelectionType.id)
    content = models.CharField(200)


class SelectionType(Datatype):
    count = models.IntegerField()

    def values(self):
        SelectionValue.objects.filter(selectionType=self.id)


class DateType(Datatype):
    min = models.DateTimeField()
    max = models.DateTimeField()

# -- Permission system


class dbUser(models.User):
    id = models.IntegerField()
    rights = models.ForeignKey(RightList.id)


class dbGroup(models.Group):
    rights = models.ForeignKey(RightList.id)


class RelUserGroup(models.Model):
    user = models.ForeignKey(dbUser.id)
    group = models.ForeignKey(dbGroup.name)
    isAdmin = models.BooleanField()


class RightList(models.Model):
    id = models.IntegerField()
    table = models.ForeignKey(Table.id)
    viewLog = models.BooleanField()
    rightsAdmin = models.BooleanField()


class RelRightsDataDescr(models.Model):
    column = models.ForeignKey(DataDescr.id)
    rightList = models.ForeignKey(RightList.id)
    read = models.BooleanField()
    insert = models.BooleanField()
    modify = models.BooleanField()
    delete = models.BooleanField()
