__author__ = 'My-Tien Nguyen'

from models import *
from django.forms import ModelForm

# -- Table structure


class ColumnForm(ModelForm):
    class Meta:
        model = Column
        fields = ('name', 'type', 'required', 'created', 'creator')


class DatasetForm(ModelForm):
    class Meta:
        model = Dataset
        fields = ('created', 'creator')


class TableForm(ModelForm):
    class Meta:
        model = Table
        fields = ('name', 'created', 'creator')


class DataForm(ModelForm):  # TODO: Needed?
    class Meta:
        model = Data
        fields = ('created', 'creator')


class DataTextForm(ModelForm):
    class Meta:
        model = DataText
        fields = ('created', 'creator', 'content')


class DataNumericForm(ModelForm):
    class Meta:
        model = DataNumeric
        fields = ('created', 'creator', 'content')


class DataSelectionForm(ModelForm):
    class Meta:
        model = DataSelection
        fields = ('created', 'creator', 'content')


class DataDateForm(ModelForm):
    class Meta:
        model = DataDate
        fields = ('created', 'creator', 'content')


class DataBoolForm(ModelForm):
    class Meta:
        model = DataBool
        fields = ('created', 'creator', 'content')


# -- data types


class TypeForm(ModelForm):
    class Meta:
        model = Type
        fields = ('name',)


class TypeTextForm(ModelForm):
    class Meta:
        model = TypeText
        fields = ('length', )


class TypeNumericForm(ModelForm):
    class Meta:
        model = TypeNumeric
        fields = ('min', 'max')


class SelectionValueForm(ModelForm):
    class Meta:
        model = SelectionValue
        fields = ('index', 'content')


class TypeSelectionForm(ModelForm):
    class Meta:
        model = TypeSelection
        fields = ('count', )


class TypeDateForm(ModelForm):
    class Meta:
        model = TypeDate
        fields = ('min', 'max')

# -- Permission system


class DBGroupForm(ModelForm):
    class Meta:
        model = DBGroup
        fields = ('name', )


class MembershipForm(ModelForm):
    class Meta:
        model = Membership
        fields = ('isAdmin', )


class RightListForTableForm(ModelForm):
    class Meta:
        model = RightListForTable
        fields = ('viewLog', 'rightsAdmin', 'insert')


class RightListForColumnForm(ModelForm):
    class Meta:
        model = RightListForColumn
        fields = ('read', 'modify', 'delete')
