"""
FYI:
about Django:
- Usage of ForeignKey(): first param = name of referenced model X as string (avoids problem of forward declaration)
                         Second param is required if X is referenced more than once: related_name=[unique String]

- django does not support overwriting of parent field-attributes by child classes

- an id-field is automatically added to each model without primary-key

about our implementation:
- BoolData does not need BoolType, as range is already clear
"""

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager


# -- Table structure


class DataDescr(models.Model):
    name = models.CharField(max_length=100)
    table = models.ForeignKey('Table', related_name="dataDescrs")
    type = models.ForeignKey('Datatype')
    required = models.BooleanField()

    created = models.DateTimeField()
    deleted = models.DateTimeField(blank=True, null=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s-creator')
    deleter = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s-deleter', blank=True, null=True)

    def __unicode__(self):
        return self.name


class Dataset(models.Model):
    table = models.ForeignKey('Table', related_name="datasets")
    created = models.DateTimeField()
    deleted = models.DateTimeField(blank=True, null=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='set-creator')
    deleter = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='set-deleter', blank=True, null=True)

    def getData(self):
        return self.data.all()

    def getField(self, name):
        pass

    def __unicode__(self):
        return unicode(self.table) + " id " + unicode(self.id)


class Table(models.Model):
    name = models.CharField(max_length=100)
    created = models.DateTimeField()
    deleted = models.DateTimeField(blank=True, null=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s-creator')
    deleter = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s-deleter', blank=True, null=True)

    def getDataDescrs(self):
        return self.dataDescrs.all()

    def getDatasets(self):
        return self.datasets.all()

    def __unicode__(self):  # TODO: does not check for tables without columns
        return self.name


# -- Data fields

# related-names in base classes must contain '%(class)s' to avoid clashes in inheriting classes
class Data(models.Model):
    column = models.ForeignKey('DataDescr', related_name="%(class)s-data")
    dataset = models.ForeignKey('Dataset', related_name="%(class)s-data")
    created = models.DateTimeField()
    deleted = models.DateTimeField(blank=True, null=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s-creator')
    deleter = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s-deleter', blank=True, null=True)

    def getContent(self):  # workaround for overwriting parent field attribute
        pass

    class Meta:
        abstract = True


class TableData(Data):
    pass


class RelTableDataDataset(models.Model):
    tableData = models.ForeignKey('TableData')
    dataset = models.ForeignKey('Dataset')


class TextData(Data):
    content = models.CharField(max_length=200)

    def getContent(self):
        return self.content

    def __unicode__(self):
        return self.content


class NumericData(Data):
    content = models.FloatField()

    def getContent(self):
        return self.content

    def __unicode__(self):
        return unicode(self.content)


class SelectionData(Data):
    content = models.ForeignKey('SelectionValue')

    def getContent(self):
        return self.content

    def __unicode__(self):
        return unicode(self.content)


class DateData(Data):
    content = models.DateTimeField()

    def getContent(self):
        return self.content

    def __unicode__(self):
        return unicode(self.content)


class BoolData(Data):
    content = models.BooleanField()

    def getContent(self):
        return self.content

    def __unicode__(self):
        return unicode(self.content)


# -- data types

class Datatype(models.Model):
    TEXT = 0
    NUMERIC = 1
    DATE = 2
    SELECTION = 3
    TABLE = 4

    name = models.CharField(max_length=30)

    def __unicode__(self):
        return self.name


class TextType(models.Model):
    datatype = models.ForeignKey('Datatype')
    length = models.IntegerField()

    def __unicode__(self):
        return self.datatype.name


class NumericType(models.Model):
    datatype = models.ForeignKey('Datatype')
    min = models.FloatField()
    max = models.FloatField()

    def __unicode__(self):
        return Datatype.objects.filter(datatype=id).name


class SelectionValue(models.Model):
    selectionType = models.ForeignKey('SelectionType', to_field='datatype', related_name='selVals')
    content = models.CharField(max_length=100)
    index = models.IntegerField()

    def __unicode__(self):
        return self.content


class SelectionType(models.Model):
    datatype = models.ForeignKey('Datatype', unique=True)
    count = models.IntegerField()

    def value(self, pos):
        return self.selVals.get(index=pos)

    def values(self):
        return self.selVals.all()

    def __unicode__(self):
        return Datatype.objects.filter(datatype=id).name


class DateType(models.Model):
    datatype = models.ForeignKey('Datatype')
    min = models.DateTimeField()
    max = models.DateTimeField()

    def __unicode__(self):
        return Datatype.objects.filter(datatype=id).name


class TableType(models.Model):
    datatype = models.ForeignKey('Datatype')
    table = models.ForeignKey('Table')

    def __unicode__(self):
        return Datatype.objects.filter(datatype=id).name

# -- Permission system


class DBUser(AbstractUser):
    tableCreator = models.BooleanField()
    objects = UserManager()


class DBGroup(models.Model):
    name = models.CharField(max_length=30)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='RelUserGroup')


class RelUserGroup(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    group = models.ForeignKey('DBGroup')
    isAdmin = models.BooleanField()

    def __unicode__(self):
        return unicode(self.user) + " - " + unicode(self.group)


class RightList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="rights", blank=True, null=True)
    group = models.ForeignKey('DBGroup', related_name="rights", blank=True, null=True)
    table = models.ForeignKey('Table', related_name="rightlists")
    viewLog = models.BooleanField()
    rightsAdmin = models.BooleanField()
    insert = models.BooleanField()

    def __unicode__(self):
        return "list " + unicode(self.id) + " for " + unicode(self.table)


class RelRightsDataDescr(models.Model):
    column = models.ForeignKey('DataDescr')
    rightList = models.ForeignKey('RightList')
    read = models.BooleanField()
    modify = models.BooleanField()
    delete = models.BooleanField()

    def __unicode__(self):
        return unicode(self.rightList) + ":" + unicode(self.column)