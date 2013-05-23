from database.models import *
from database.forms import *

def create_table(**kwargs):
    """
    creates a simple table with two columns with
    two datasets filed with two values
    """

    table = dict()
    table["name"] = "Test"
    table["created"] = datetime.now()
    tabF = TableForm(table)
    if tabF.is_valid():
        newTable = tabF.save()
        table.save()

    columnFirstname= dict()
    columnFirstname["name"] = "Vorname"
    columnFirstname["required"] = True
    columnFirstname["created"] = datetime.now()
    colFirstnameF = ColumnForm(columnFirstname)
    if colFirstnameF.is_valid():
        newColumnFirstname = colFirstnameF.save()
        newColumnFirstname.table = newTable
        newColumnFirstname.save()

    columnSecondname = dict()
    columnSecondname["name"] = "Nachname"
    columnSecondname["required"] = True
    columnSecondname["created"] = datetime.now()
    colSecondnameF = ColumnForm(columnSecondname)
    if colSecondnameF.is_valid():
        newColumnSecondname = colSecondnameF.save()
        newColumnSecondname.table = newTable
        newColumnSecondname.save()

    dataSetFirstname = dict()
    dataSetFirstname["created"] = datetime.now()
    dataSetFirstnameF = DatasetForm(dataSetFirstname)
    if dataSetFirstnameF.is_valid():
        newDataSetFirstname = dataSetFirstnameF.save()
        newDataSetFirstname.column = newColumnFirstname
        newDataSetFirstname.save()

    dataSetSecondname = dict()
    dataSetSecondname["created"] = datetime.now()
    dataSetSecondnameF = DatasetForm(dataSetSecondname)
    if dataSetSecondnameF.is_valid():
        newDataSetSecondname = dataSetSecondnameF.save()
        newDataSetSecondname.column = newColumnSecondname
        newDataSetSecondname.save()

    dataTextFirstname = dict()
    dataTextFirstname["created"] = datetime.now()
    dataTextFirstname["content"] = "Hasret"
    dataTextFirstnameF = DataTextForm(dataTextFirstname)
    if dataTextFirstnameF.is_valid():
        newDataTextFirstname = dataTextFirstnameF.save()
        newDataTextFirstname.dataSet = newDataSetFirstname
        newDataTextFirstname.save()

    dataTextSecondname = dict()
    dataTextSecondname["created"] = datetime.now()
    dataTextSecondname["content"] = "Demirci"
    dataTextSecondnameF = DataTextForm(dataTextSecondname)
    if dataTextSecondnameF.is_valid():
        newDataTextSecondname = dataTextSecondnameF.save()
        newDataTextSecondname.dataSet = newDataSetSecondname
        newDataTextSecondname.save()

    return table

def create_Group(**kwargs):
    """
    creates a group with two members
    """
    hans = DBUser.objects.create_user(username="hans")
    hans.save()
    mark = DBUser.objects.create_user(username="mark")
    mark.save()

    groupA = dict()
    groupA["name"] = "Student"
    groupF = DBGroupForm(groupA)
    if groupF.is_valid():
        newDBGroup = groupF.save()
        newDBGroup.save()

    m1 = dict()
    m1["isAdmin"] = True
    m1F = MembershipForm(m1)
    if m1F.is_valid():
        m1new = m1F.save(commit=False)
        m1new.user = hans
        m1new.group = newDBGroup
        m1new.save()

    m2 = dict()
    m2["isAdmin"] = False
    m2F = MembershipForm(m2)
    if m2F.is_valid():
        m2new = m2F.save(commit=False)
        m2new.user = mark
        m2new.group = newDBGroup
        m2F.save()

    return newDBGroup