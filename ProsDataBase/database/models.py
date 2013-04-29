from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, UserManager


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

    def __unicode__(self):
        return unicode(self.column1) + "-" + unicode(self.column2)


class Dataset(models.Model):
    table = models.ForeignKey('Table')
    created = models.DateTimeField()
    deleted = models.DateTimeField(blank=True, null=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='set-creator')
    deleter = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='set-deleter', blank=True, null=True)

    def data(self):
        Data.objects.filter(dataset=self.id)

    def __unicode__(self):
        return unicode(self.table)


class Table(models.Model):
    name = models.CharField(max_length=100)

    def dataDescrs(self):
        DataDescr.objects.filter(table=self.id)

    def datasets(self):
        Dataset.objects.filter(table=self.id)

    def references(self):
        Reference.objects.filter(table1=self.id)

    def __unicode__(self):  # TODO: does not check for tables without columns
        return self.name


# -- Data fields


class Data(models.Model):
    column = models.ForeignKey('DataDescr')
    dataset = models.ForeignKey('Dataset')
    created = models.DateTimeField()
    deleted = models.DateTimeField(blank=True, null=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s-creator')
    deleter = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s-deleter', blank=True, null=True)

    def getContent(self):  # workaround for overwriting parent field attribute
        pass

    class Meta:
        abstract = True


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
        return self.content


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
        return self.content


class BoolData(Data):
    content = models.BooleanField()

    def getContent(self):
        return self.content

    def __unicode__(self):
        return self.content


# -- data types


class Datatype(models.Model):
    name = models.CharField(max_length=30)

    def __unicode__(self):
        return self.name


class TextType(models.Model):
    name = models.ForeignKey('Datatype')
    length = models.IntegerField()

    def __unicode__(self):
        return unicode(self.name)


class NumericType(models.Model):
    name = models.ForeignKey('Datatype')
    min = models.FloatField()
    max = models.FloatField()

    def __unicode__(self):
        return unicode(self.name)


class SelectionValue(models.Model):
    selectionType = models.ForeignKey('SelectionType')
    content = models.CharField(max_length=100)

    def __unicode__(self):
        return self.content


class SelectionType(models.Model):
    name = models.ForeignKey('Datatype')
    count = models.IntegerField()

    def values(self):
        SelectionValue.objects.filter(selectionType=self)

    def __unicode__(self):
        return unicode(self.name)


class DateType(models.Model):
    name = models.ForeignKey('Datatype')
    min = models.DateTimeField()
    max = models.DateTimeField()

    def __unicode__(self):
        return unicode(self.name)

# -- Permission system


class DBUser(AbstractUser):
    rights = models.ForeignKey('RightList', null=True, blank=True)
    objects = UserManager()


class DBGroup(models.Model):
    name = models.CharField(max_length=30)
    rights = models.ForeignKey('RightList')
    DBUsers = models.ManyToManyField(settings.AUTH_USER_MODEL, through='RelUserGroup')


class RelUserGroup(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    group = models.ForeignKey('DBGroup')
    isAdmin = models.BooleanField()

    def __unicode__(self):
        return unicode(self.user) + " - " + unicode(self.group)


class RightList(models.Model):
    table = models.ForeignKey('Table')
    viewLog = models.BooleanField()
    rightsAdmin = models.BooleanField()

    def __unicode__(self):
        return "list " + str(self.id) + " for " + unicode(self.table)


class RelRightsDataDescr(models.Model):
    column = models.ForeignKey('DataDescr')
    rightList = models.ForeignKey('RightList')
    read = models.BooleanField()
    insert = models.BooleanField()
    modify = models.BooleanField()
    delete = models.BooleanField()

    def __unicode__(self):
        return unicode(self.rightList) + ":" + unicode(self.column)