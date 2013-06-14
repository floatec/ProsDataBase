# -*- coding: UTF-8 -*-

__author__ = 'My-Tien Nguyen'

from models import *
from django.forms import ModelForm

# ===============================
# ----- TABLE FORMS ---------
# ===============================


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ('name', )


class ColumnForm(ModelForm):
    class Meta:
        model = Column
        fields = ('name', 'created', 'comment')


class DatasetForm(ModelForm):
    class Meta:
        model = Dataset
        fields = ('created', )


class TableForm(ModelForm):
    class Meta:
        model = Table
        fields = ('name', 'created')


# ===============================
# ----- DATA FORMS --------------
# ===============================


class DataForm(ModelForm):  # TODO: Needed?
    class Meta:
        model = Data
        fields = ('created',)


class DataTextForm(ModelForm):
    class Meta:
        model = DataText
        fields = ('created', 'content')


class DataNumericForm(ModelForm):
    class Meta:
        model = DataNumeric
        fields = ('created', 'content')


class DataDateForm(ModelForm):
    class Meta:
        model = DataDate
        fields = ('created', 'content')


class DataSelectionForm(ModelForm):
    class Meta:
        model = DataSelection
        fields = ('created', 'content')


class DataBoolForm(ModelForm):
    class Meta:
        model = DataBool
        fields = ('created', 'content')


class DataTableForm(ModelForm):
    class Meta:
        model = DataTable
        fields = ('created',)

# ===============================
# ----- TYPE FORMS --------------
# ===============================


class TypeForm(ModelForm):
    class Meta:
        model = Type
        fields = ('name', 'type')


class TypeTextForm(ModelForm):
    class Meta:
        model = TypeText
        fields = ('length', )


class TypeNumericForm(ModelForm):
    class Meta:
        model = TypeNumeric
        fields = ('min', 'max')


class TypeDateForm(ModelForm):
    class Meta:
        model = TypeDate
        fields = ('min', 'max')


class SelectionValueForm(ModelForm):
    class Meta:
        model = SelectionValue
        fields = ('index', 'content')


class TypeSelectionForm(ModelForm):
    class Meta:
        model = TypeSelection
        fields = ('count', )


# ===============================
# ------- HISTORY TABLE ---------
# ===============================


class HistoryForm(ModelForm):
    class Meta:
        model = History
        fields = ('date', 'type')


# ===============================
# ----- PERMISSION FORMS --------
# ===============================


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
        fields = ('viewLog', 'rightsAdmin', 'insert', 'delete')


class RightListForColumnForm(ModelForm):
    class Meta:
        model = RightListForColumn
        fields = ('read', 'modify')
