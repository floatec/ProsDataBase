from database.models import *
from database.forms import *
from database.serializers import *
from string import ascii_lowercase, digits
from random import choice

def generate_random_username(length=5, chars=ascii_lowercase):
    """
    generate a simple string with the length of 5 characters only lowercase
    alphabets
    """
    username = ''.join([choice(chars) for i in xrange(length)])
    return username

def generate_random_number(length=2, chars=digits):
    number = ''.join([choice(chars) for k in xrange(length)])
    return number

def create_table(**kwargs):
    """
    creates a simple table with two columns and
    two datasets filed with 3 values
    """
    testUser = DBUser.objects.create_user(username="test")
    testUser.save()

    table = dict()
    table["name"] = "BungaBunga"
    table["created"] = datetime.now()
    tabF = TableForm(table)
    if tabF.is_valid():
        newTable = tabF.save(commit=False)
        newTable.creator = testUser
        newTable.save()


    texttype = Type(name="Text", type=0)
    texttype.save()

    numerictype = Type(name="Numeric", type=1)
    numerictype.save()
    numericCond = TypeNumeric(type=numerictype, min=2, max=10)
    numericCond.save()

    datetype = Type(name="Type", type=2)
    datetype.save()

    selectiontype = Type(name="Selection", type=3)
    selectiontype.save()

    typeSelection = dict()
    typeSelection["count"] = 2
    typeSelectionF = TypeSelectionForm(typeSelection)
    if typeSelectionF.is_valid():
        newTypeSelection = typeSelectionF.save(commit=False)
        newTypeSelection.type = selectiontype
        newTypeSelection.save()

    selection1 = dict()
    selection1["index"] = 0
    selection1["content"] = "ja"
    selection1F = SelectionValueForm(selection1)
    if selection1F.is_valid():
        newSelection1 = selection1F.save(commit=False)
        newSelection1.typeSelection = newTypeSelection
        newSelection1.save()

    selection2 = dict()
    selection2["index"] = 1
    selection2["content"] = "nein"
    selection2F = SelectionValueForm(selection2)
    if selection2F.is_valid():
        newSelection2 = selection2F.save(commit=False)
        newSelection2.typeSelection = newTypeSelection
        newSelection2.save()

    booleantype = Type(name="Boolean", type=4)
    booleantype.save()

    tabletype = Type(name="Table", type=5)
    tabletype.save()

    for i in range(0,6):
        columns = dict()
        columns["name"] = i
        columns["required"] = True
        columns["created"] = datetime.now()
        columnsF = ColumnForm(columns)
        if columnsF.is_valid():
            newColumns = columnsF.save(commit=False)
            newColumns.table = newTable
            if i == 0:
                newColumns.type = texttype
            if i == 1:
                newColumns.type = numerictype
            if i == 2:
                newColumns.type = datetype
            if i == 3:
                newColumns.type = selectiontype
            if i == 4:
                newColumns.type = booleantype
            if i == 5:
                newColumns.type = tabletype
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
                if i == 0:
                    for j in range(0,2):
                        dataText = dict()
                        dataText["created"] = datetime.now()
                        dataText["content"] =  generate_random_username()
                        dataTextF = DataTextForm(dataText)
                        if dataTextF.is_valid():
                            newDataText = dataTextF.save(commit=False)
                            newDataText.column = newColumns
                            newDataText.dataset = newDataSets
                            newDataText.creator = testUser
                            newDataText.save()
                if i == 1:
                    for k in range(0,2):
                        dataNumeric = dict()
                        dataNumeric["created"] = datetime.now()
                        dataNumeric["content"] = generate_random_number()
                        dataNumericF = DataNumericForm(dataNumeric)
                        if dataNumericF.is_valid():
                            newDataNummeric = dataNumericF.save(commit=False)
                            newDataNummeric.column = newColumns
                            newDataNummeric.dataset = newDataSets
                            newDataNummeric.creator = testUser
                            newDataNummeric.save()
                if i == 2:
                    for l in range(0,2):
                        dataDate = dict()
                        dataDate["created"] = datetime.now()
                        dataDate["content"] = datetime.now()
                        dataDateF = DataDateForm(dataDate)
                        if dataDateF.is_valid():
                            newDataDate = dataDateF.save(commit=False)
                            newDataDate.column = newColumns
                            newDataDate.dataset = newDataSets
                            newDataDate.creator = testUser
                            newDataDate.save()
                if i == 3:
                    for m in range(0,2):
                        dataSelection = dict()
                        dataSelection["created"] = datetime.now()
                        if l == 0:
                            dataSelection["content"] = "ja"
                        if l == 1:
                            dataSelection["content"] = "nein"
                        dataSelectionF = DataSelectionForm(dataSelection)
                        if dataSelectionF.is_valid():
                            newDataSelection = dataSelectionF.save(commit=False)
                            newDataSelection.column = newColumns
                            newDataSelection.dataset = newDataSets
                            newDataSelection.creator = testUser
                            newDataSelection.save()
                if i == 4:
                    for n in range(0,2):
                        dataBoolean = dict()
                        dataBoolean["created"] = datetime.now()
                        if k == 0:
                            dataBoolean["content"] = "True"
                        if k == 1:
                            dataBoolean["content"] = "False"
                        dataBooleanF = DataBoolForm(dataBoolean)
                        if dataBooleanF.is_valid():
                            newDataBoolean = dataBooleanF.save(commit=False)
                            newDataBoolean.column = newColumns
                            newDataBoolean.dataset = newDataSets
                            newDataBoolean.creator = testUser
                            newDataBoolean.save()

                if i == 5:
                    op = dict()
                    op["name"] = "BungaBunga"
                    op["created"] = datetime.now()
                    opF = TableForm(op)
                    if opF.is_valid():
                        newOP = opF.save(commit=False)
                        newOP.creator = testUser
                        newOP.save()
                        columnsOP = dict()
                        columnsOP["name"] = i
                        columnsOP["required"] = True
                        columnsOP["created"] = datetime.now()
                        columnsOPF = ColumnForm(columnsOP)
                        if columnsOPF.is_valid():
                            newColumnsOP = columnsOPF.save(commit=False)
                            newColumnsOP.type = texttype
                            newColumnsOP.save()
                            dataSetsOP = dict()
                            dataSetsOP["created"] = datetime.now()
                            dataSetsOPF = DatasetForm(dataSetsOP)
                            if dataSetsOPF.is_valid():
                                newDataSetsOP = dataSetsOPF.save(commit=False)
                                newDataSetsOP.column = newColumnsOP
                                newDataSetsOP.creator = testUser
                                newDataSetsOP.table = newOP
                                newDataSetsOP.save()





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