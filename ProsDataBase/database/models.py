# -*- coding: UTF-8 -*-

"""
FYI:
about Django:
- Usage of ForeignKey(): first param = name of referenced model X as string (avoids problem of forward declaration)
                         Second param is required if X is referenced more than once: related_name=[unique String]

- django does not support overwriting of parent field-attributes by child classes

- an id-field is automatically added to each model without primary-key

about our implementation:
- DataBool does not need TypeBool, as range is already clear
"""

import sys

from django.db import models
from django.conf import settings
from datetime import datetime
from django.contrib.auth.models import AbstractUser, UserManager


# -- Table structure


class Column(models.Model):
    name = models.CharField(max_length=100)
    table = models.ForeignKey('Table', related_name="columns")
    type = models.ForeignKey('Type')
    required = models.BooleanField(default=False)
    comment = models.TextField(blank=True, null=True)

    created = models.DateTimeField(default=datetime.now)
    modified = models.DateTimeField(blank=True, null=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='columncreator')
    modifier = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='columnmodifier', blank=True, null=True)

    def __unicode__(self):
        return self.name


class Dataset(models.Model):
    datasetID = models.CharField(max_length=200)
    table = models.ForeignKey('Table', related_name="datasets")
    created = models.DateTimeField(default=datetime.now)
    modified = models.DateTimeField(blank=True, null=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='setcreator')
    modifier = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='setmodifier', blank=True, null=True)

    def getData(self):
        """
        returns an array of querysets of different types of datas.

        Order is text, numeric, date, selection, table, bool
        """
        data = list()
        data.append(self.datatext.all())
        data.append(self.datanumeric.all())
        data.append(self.datadate.all())
        data.append(self.dataselection.all())
        data.append(self.databool.all())
        data.append(self.datatable.all())
        return data

    def getCount(self):
        if len(self.datasetID) > 0:
            delim1 = self.datasetID.index('_')
            delim2 = self.datasetID[delim1 + 1:].index('_') + delim1 + 1

            return int(self.datasetID[delim1 + 1:delim2])
        else:
            return 0

    def checksum(self):
        """
        returns an upper-case letter as checksum based on the primary key and the creation date.
        """
        result = self.pk * 7 + self.created.year * 7 + self.created.month * 7 + self.created.day * 7
        chars = list()
        for i in range(65, 91):
            chars.append(chr(i))
        return chars[result % len(chars)]

    def getField(self, name):
        for field in self.getData(self):
            if field.name == name:
                return field

    def __unicode__(self):
        return unicode(self.table) + " id " + unicode(self.id)


class Table(models.Model):
    name = models.CharField(max_length=100)
    created = models.DateTimeField(default=datetime.now)
    modified = models.DateTimeField(blank=True, null=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='tablecreator')
    modifier = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='tablemodifier', blank=True, null=True)

    def getColumns(self):
        return self.columns.all()

    def getDatasets(self):
        return self.datasets.all()

    def generateDatasetID(self, dataset):
        """
        returns a semantical id of the form tableID.YYYY_No_Checksum.

        tableID is the unique id from the table's AutoField,
        YYYY is the year the dataset was created in,
        No is a counter for datasets in a specific year,
        Checksum is a letter in range ['A', 'Z'].
        E.g. 3_2013_23_C means: this is the 23rd dataset which was created  in 2013 for the table with id 3.
        """
        datasets = self.datasets.filter(created__year=dataset.created.year)

        counts = list()
        counts.append(0)
        for dataset in datasets:
            counts.append(dataset.getCount())

        return str(self.pk) + "." + str(dataset.created.year) + "_" + str(max(counts) + 1) + "_" + dataset.checksum()

    def __unicode__(self):  # TODO: does not check for tables without columns
        return self.name


# -- Data fields

# related-names in base classes must contain '%(class)s' to avoid clashes in inheriting classes
class Data(models.Model):
    column = models.ForeignKey('Column', related_name="%(class)s")
    dataset = models.ForeignKey('Dataset', related_name="%(class)s")
    created = models.DateTimeField(default=datetime.now())
    modified = models.DateTimeField(blank=True, null=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_creator')
    modifier = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_modifier', blank=True, null=True)

    class Meta:
        abstract = True


class DataText(Data):
    content = models.CharField(max_length=200)

    def __unicode__(self):
        return self.content


class DataNumeric(Data):
    content = models.FloatField()

    def __unicode__(self):
        return unicode(self.content)


class DataSelection(Data):
    content = models.CharField(max_length=100)

    def __unicode__(self):
        return unicode(self.content)


class DataDate(Data):
    content = models.DateTimeField()

    def __unicode__(self):
        return unicode(self.content)


class DataBool(Data):
    content = models.BooleanField()

    def __unicode__(self):
        return unicode(self.content)


class DataTable(Data):
    def content(self):
        return self.linkToDatasets.all()


class DataTableToDataset(models.Model):
    DataTable = models.ForeignKey('DataTable', related_name="linkToDatasets")
    dataset = models.ForeignKey('Dataset')

# -- data types


class Type(models.Model):
    TEXT = 0
    NUMERIC = 1
    DATE = 2
    SELECTION = 3
    BOOL = 4
    TABLE = 5

    type = models.IntegerField()
    name = models.CharField(max_length=30)

    def getType(self):
        if hasattr(self, 'typetext') and self.typetext is not None:
            return self.typetext
        if hasattr(self, 'typenumeric') and self.typenumeric is not None:
            return self.typenumeric
        if hasattr(self, 'typedate') and self.typedate is not None:
            return self.typedate
        if hasattr(self, 'typeselection') and self.typeselection is not None:
            return self.typeselection
        if hasattr(self, 'typebool') and self.typebool is not None:
            return self.typebool
        if hasattr(self, 'typetable') and self.typetable is not None:
            return self.typetable

    def __unicode__(self):
        return self.name


class TypeText(models.Model):
    type = models.OneToOneField('Type')
    length = models.IntegerField(default=200)

    def isValid(self, input):
        return len(input) <= self.length

    def __unicode__(self):
        return self.type.name


class TypeNumeric(models.Model):
    type = models.OneToOneField('Type')
    min = models.FloatField(default=-sys.maxint)
    max = models.FloatField(default=sys.maxint)

    def isValid(self, input):
        return self.min <= input <= self.max

    def __unicode__(self):
        return self.type.name


class TypeDate(models.Model):
    type = models.OneToOneField('Type')
    min = models.DateTimeField(blank=True, null=True)
    max = models.DateTimeField(blank=True, null=True)

    def isValid(self, input):
        return True

    def __unicode__(self):
        return self.type.name


class SelectionValue(models.Model):
    typeSelection = models.ForeignKey('TypeSelection', to_field='type', related_name='selVals')
    index = models.IntegerField()
    content = models.CharField(max_length=100)

    def __unicode__(self):
        return self.content


class TypeSelection(models.Model):
    type = models.OneToOneField('Type')
    count = models.IntegerField()

    def value(self, pos):
        return self.selVals.get(index=pos)

    def values(self):
        return self.selVals.all()

    def isValid(self, input):
        selValContents = []
        for val in self.selVals.all():
            selValContents.append(val.content)

        return input in selValContents

    def __unicode__(self):
        return self.type.name


class TypeBool(models.Model):
    type = models.OneToOneField('Type')

    def isValid(self, input):
        return input in [True, False]

    def __unicode__(self):
        return self.type.name


class TypeTable(models.Model):
    type = models.OneToOneField('Type')
    table = models.ForeignKey('Table')

    def isValid(self, input):
        datasets = self.table.datasets.all()
        datasetIDs = []
        for dataset in datasets:
            datasetIDs.append(dataset.id)

        return set(input).issubset(set(datasetIDs))

    def __unicode__(self):
        return self.type.name

# -- Permission system


class DBUser(AbstractUser):
    tableCreator = models.BooleanField(default=False)
    groupCreator = models.BooleanField(default=False)
    objects = UserManager()


class DBGroup(models.Model):
    name = models.CharField(max_length=30)
    tableCreator = models.BooleanField(default=False)
    groupCreator = models.BooleanField(default=False)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Membership')

    def __unicode__(self):
        return self.name


class Membership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    group = models.ForeignKey('DBGroup')
    isAdmin = models.BooleanField(default=False)

    def __unicode__(self):
        return unicode(self.user) + " - " + unicode(self.group)


class RightListForTable(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name="table-rights")
    group = models.ForeignKey('DBGroup', blank=True, null=True, related_name="table-rights")

    table = models.ForeignKey('Table', related_name="rightlists")
    viewLog = models.BooleanField(default=False)
    rightsAdmin = models.BooleanField(default=False)
    insert = models.BooleanField(default=False)
    delete = models.BooleanField(default=False)

    def __unicode__(self):
        return "list " + unicode(self.id) + " for " + unicode(self.table)


class RightListForColumn(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name="column-rights")
    group = models.ForeignKey('DBGroup', blank=True, null=True, related_name="column-rights")

    column = models.ForeignKey('Column')
    read = models.BooleanField(default=False)
    modify = models.BooleanField(default=False)

    def __unicode__(self):
        return "list" + unicode(self.id) + ":" + unicode(self.column)