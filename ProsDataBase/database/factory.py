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
        newTable = tabF.save(commit=False)


    columnFirstname= dict()
    columnFirstname["name"] = "Vorname"
    columnFirstname["required"] = True
    columnFirstname["created"] = datetime.now()
    colFirstnameF = ColumnForm(columnFirstname)
    if colFirstnameF.is_valid():
        newColumnFirstname = colFirstnameF.save(commit=False)
        newColumnFirstname.table = newTable


    columnSecondname = dict()
    columnSecondname["name"] = "Nachname"
    columnSecondname["required"] = True
    columnSecondname["created"] = datetime.now()
    colSecondnameF = ColumnForm(columnSecondname)
    if colSecondnameF.is_valid():
        newColumnSecondname = colSecondnameF.save(commit=False)
        newColumnSecondname.table = newTable
        newColumnSecondname.save()

    dataSetFirstname = dict()
    dataSetFirstname["created"] = datetime.now()
    dataSetFirstnameF = DatasetForm(dataSetFirstname)
    if dataSetFirstnameF.is_valid():
        newDataSetFirstname = dataSetFirstnameF.save(commit=False)
        newDataSetFirstname.column = newColumnFirstname
        newDataSetFirstname.save()

    dataSetSecondname = dict()
    dataSetSecondname["created"] = datetime.now()
    dataSetSecondnameF = DatasetForm(dataSetSecondname)
    if dataSetSecondnameF.is_valid():
        newDataSetSecondname = dataSetSecondnameF.save(commit=False)
        newDataSetSecondname.column = newColumnSecondname
        newDataSetSecondname.save()

    dataTextFirstname = dict()
    dataTextFirstname["created"] = datetime.now()
    dataTextFirstname["content"] = "Hasret"
    dataTextFirstnameF = DataTextForm(dataTextFirstname)
    if dataTextFirstnameF.is_valid():
        newDataTextFirstname = dataTextFirstnameF.save(commit=False)
        newDataTextFirstname.dataSet = newDataSetFirstname
        newDataTextFirstname.save()

    dataTextSecondname = dict()
    dataTextSecondname["created"] = datetime.now()
    dataTextSecondname["content"] = "Demirci"
    dataTextSecondnameF = DataTextForm(dataTextSecondname)
    if dataTextSecondnameF.is_valid():
        newDataTextSecondname = dataTextSecondnameF.save(commit=False)
        newDataTextSecondname.dataSet = newDataSetSecondname
        newDataTextSecondname.save()

    newTable.save()
    return table


def create_Group(**kwargs):
    """
    creates a group with two members
    """
    groupA = dict()
    groupA["name"] = "Student"
    groupF = DBGroupForm(groupA)
    if groupF.is_valid():
        newDBGroup = groupF.save()
        newDBGroup.save()

    for i in range(1,1001):
        user = DBUser.objects.create_user(username=i)
        user.save()
        m = dict()
        m["isAdmin"] = False
        mF = MembershipForm(m)
        if mF.is_valid():
            newm = mF.save(commit=False)
            newm.user = user
            newm.group = newDBGroup
            newm.save()

    return newDBGroup