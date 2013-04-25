from django.db import models
from django.contrib.auth.models import User, Group


# -- Table structure


class DataDescr(models.Model):
    name = models.CharField(max_length=100)
    table = models.ForeignKey('Table')
    type = models.ForeignKey('Datatype')
    required = models.BooleanField()


class Reference(models.Model):
    column1 = models.ForeignKey('DataDescr', related_name='col1')
    column2 = models.ForeignKey('DataDescr', related_name='col2')


class Dataset(models.Model):
    table = models.ForeignKey('Table')
    created = models.DateTimeField()
    deleted = models.DateTimeField()
    creator = models.ForeignKey('dbUser', related_name='set-creator')
    deleter = models.ForeignKey('dbUser', related_name='set-deleter')

    def data(self):
        Data.objects.filter(dataset=self.id)


class Table(models.Model):
    name = models.CharField(max_length=100)

    def dataDescrs(self):
        DataDescr.objects.filter(table=self.id)

    def datasets(self):
        Dataset.objects.filter(table=self.id)

    def references(self):
        Reference.objects.filter(table1=self.id)


# -- Data fields

# to receive
class Data(models.Model):
    column = models.ForeignKey('DataDescr')
    dataset = models.ForeignKey('Dataset')
    created = models.DateTimeField()
    deleted = models.DateTimeField()
    creator = models.ForeignKey('dbUser', related_name='data-creator')
    deleter = models.ForeignKey('dbUser', related_name='data-deleter')

    def content(self):
        pass


class TextData(Data):
    content = models.CharField(max_length=200)

    def content(self):
        return self.content


class NumericData(Data):
    content = models.FloatField()

    def content(self):
        return self.content


class SelectionData(Data):
    content = models.ForeignKey('SelectionValue')

    def content(self):
        return self.content


class DateData(Data):
    content = models.DateTimeField()

    def content(self):
        return self.content


# -- data types


class Datatype(models.Model):
    pass


class TextType(Datatype):
    length = models.IntegerField()


class NumericType(Datatype):
    min = models.FloatField()
    max = models.FloatField()


class SelectionValue(models.Model):
    selectionType = models.ForeignKey('SelectionType')
    content = models.CharField(max_length=100)


class SelectionType(Datatype):
    count = models.IntegerField()

    def values(self):
        SelectionValue.objects.filter(selectionType=self.id)


class DateType(Datatype):
    min = models.DateTimeField()
    max = models.DateTimeField()

# -- Permission system


class dbUser(User):
    rights = models.ForeignKey('RightList')


class dbGroup(Group):
    rights = models.ForeignKey('RightList')


class RelUserGroup(models.Model):
    user = models.ForeignKey('dbUser')
    group = models.ForeignKey('dbGroup')
    isAdmin = models.BooleanField()


class RightList(models.Model):
    table = models.ForeignKey('Table')
    viewLog = models.BooleanField()
    rightsAdmin = models.BooleanField()


class RelRightsDataDescr(models.Model):
    column = models.ForeignKey('DataDescr')
    rightList = models.ForeignKey('RightList')
    read = models.BooleanField()
    insert = models.BooleanField()
    modify = models.BooleanField()
    delete = models.BooleanField()
