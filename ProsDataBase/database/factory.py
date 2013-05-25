from database.models import *
from database.forms import *
from database.serializers import *
from string import ascii_lowercase, digits
from random import choice

def generate_random_username(length=6, chars=ascii_lowercase+digits):
    username = ''.join([choice(chars) for i in xrange(length)])
    return username

def create_table(**kwargs):
    """
    creates a simple table with two columns with
    two datasets filed with two values
    """
    testUser = DBUser.objects.create_user(username="hallo")
    testUser.save()

    table = dict()
    table["name"] = "Test"
    table["created"] = datetime.now()
    tabF = TableForm(table)
    if tabF.is_valid():
        newTable = tabF.save(commit=False)
        newTable.creator = testUser
        newTable.save()

    newDatatype = Type(name="Text", type=0)
    newDatatype.save()

    for i in range(0,3):
        columns = dict()
        columns["name"] = i
        columns["required"] = True
        columns["created"] = datetime.now()
        columnsF = ColumnForm(columns)
        if columnsF.is_valid():
            newColumns = columnsF.save(commit=False)
            newColumns.table = newTable
            newColumns.type = newDatatype
            newColumns.creator = testUser
            newColumns.save()

            dataSets = dict()
            dataSets["created"] = datetime.now()
            dataSetsF = DatasetForm(dataSets)
            if dataSetsF.is_valid():
                newDataSets = dataSetsF.save(commit=False)
                newDataSets.column = newColumns
                newDataSets.creator = testUser
                newDataSets.table = newTable
                newDataSets.save()

                for k in range(0,5):
                    dataText = dict()
                    dataText["created"] = datetime.now()
                    dataText["content"] =  generate_random_username()
                    dataTextF = DataTextForm(dataText)
                    if dataTextF.is_valid():
                        newDataTextF = dataTextF.save(commit=False)
                        newDataTextF.column = newColumns
                        newDataTextF.dataset = newDataSets
                        newDataTextF.creator = testUser
                        newDataTextF.save()

    print TableSerializer.serializeOne("Test")

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