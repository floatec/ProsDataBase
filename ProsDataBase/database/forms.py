__author__ = 'My-Tien Nguyen'

from models import *
from django.forms import ModelForm

# -- Table structure


class DataDescrForm(ModelForm):
    class Meta:
        model = DataDescr
        fields = ('name', 'table', 'type', 'required', 'created', 'creator', 'deleted', 'deleter')


class DatasetForm(ModelForm):
    class Meta:
        model = Dataset
        fields = ('table', 'created', 'creator', 'deleted', 'deleter')


class TableForm(ModelForm):
    class Meta:
        model = Table
        fields = ('name', 'created', 'creator', 'deleted', 'deleter')


class DataForm(ModelForm):  # TODO: Needed?
    class Meta:
        model = Data
        fields = ('column', 'dataset', 'created', 'creator', 'deleted', 'deleter')


class TextDataForm(ModelForm):
    class Meta:
        model = TextData
        fields = ('column', 'dataset', 'created', 'creator', 'deleted', 'deleter', 'content')


class NumericDataForm(ModelForm):
    class Meta:
        model = NumericData
        fields = ('column', 'dataset', 'created', 'creator', 'deleted', 'deleter', 'content')


class SelectionDataForm(ModelForm):
    class Meta:
        model = SelectionData
        fields = ('column', 'dataset', 'created', 'creator', 'deleted', 'deleter', 'content')


class DateDataForm(ModelForm):
    class Meta:
        model = DateData
        fields = ('column', 'dataset', 'created', 'creator', 'deleted', 'deleter', 'content')


class BoolDataForm(ModelForm):
    class Meta:
        model = BoolData
        fields = ('column', 'dataset', 'created', 'creator', 'deleted', 'deleter', 'content')


# -- data types


class DatatypeForm(ModelForm):
    class Meta:
        model = Datatype


class TextTypeForm(ModelForm):
    class Meta:
        model = TextType
        fields = ('name', 'length')


class NumericTypeForm(ModelForm):
    class Meta:
        model = NumericType
        fields = ('name', 'min', 'max')


class SelectionValueForm(ModelForm):
    class Meta:
        model = SelectionValue
        fields = ('selectionType', 'content')


class SelectionTypeForm(ModelForm):
    class Meta:
        model = SelectionType
        fields = ('name', 'count')


class DateTypeForm(ModelForm):
    class Meta:
        model = DateType
        fields = ('name', 'min', 'max')


# -- Permission system


class DBUserForm(ModelForm):
    class Meta:
        model = DBUser
        fields = ('rights', 'objects')


class DBGroupForm(ModelForm):
    class Meta:
        model = DBGroup
        fields = ('name', 'rights', 'DBUsers')


class RelUserGroupForm(ModelForm):
    class Meta:
        model = RelUserGroup
        fields = ('user', 'group', 'isAdmin')


class RightListForm(ModelForm):
    class Meta:
        model = RightListForm
        fields = ('table', 'viewLog', 'rightsAdmin')


class RelRightsDataDescrForm(ModelForm):
    column = models.ForeignKey('DataDescr')
    rightList = models.ForeignKey('RightList')
    read = models.BooleanField()
    insert = models.BooleanField()
    modify = models.BooleanField()
    delete = models.BooleanField()

    def __unicode__(self):
        return unicode(self.rightList) + ":" + unicode(self.column)

    class Meta:
        model = RelRightsDataDescr
        fields = ('column', 'rightList', 'read', 'insert', 'modify', 'delete')