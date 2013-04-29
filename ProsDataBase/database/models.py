from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, BaseUserManager, UserManager


'''
FYI:
- Usage of ForeignKey(): first param = name of referenced model X as string.
                         Second param is required if X is referenced more than once: related_name=[unique String]

- django does not support overwriting of parent field-attributes by child classes

- an id-field is automatically added to each model without primary-key

- BoolData does not need BoolType, as range is already clear
'''


# -- Table structure


class DataDescr(models.Model):
    name = models.CharField(max_length=100)
    table = models.ForeignKey('Table')
    type = models.ForeignKey('Datatype')
    required = models.BooleanField()

    def __unicode__(self):
        return self.name


class Reference(models.Model):
    column1 = models.ForeignKey('DataDescr', related_name='col1')
    column2 = models.ForeignKey('DataDescr', related_name='col2')


class Dataset(models.Model):
    table = models.ForeignKey('Table')
    created = models.DateTimeField()
    deleted = models.DateTimeField()
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='set-creator')
    deleter = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='set-deleter')

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

    def __unicode__(self):  # TODO: does not check for tables without columns
        txt = self.name + ": "

        if self.dataDescrs(self).isEmpty():
            txt += "<empty>"
            return txt

        for col in self.dataDescrs(self):
            txt += col + ", "

        return txt[:-2]


# -- Data fields


class Data(models.Model):
    column = models.ForeignKey('DataDescr')
    dataset = models.ForeignKey('Dataset')
    created = models.DateTimeField()
    deleted = models.DateTimeField()
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='data-creator')
    deleter = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='data-deleter')

    def content(self):  # workaround for overwriting parent field attribute
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


class BoolData(Data):
    content = models.BooleanField

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


class DBUser(AbstractUser):
    rights = models.ForeignKey('RightList', null=True)
    objects = UserManager()


class DBGroup(Group):
    rights = models.ForeignKey('RightList')
    DBUsers = models.ManyToManyField(settings.AUTH_USER_MODEL, through='RelUserGroup')


class RelUserGroup(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    group = models.ForeignKey('DBGroup')
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