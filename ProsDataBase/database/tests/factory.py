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

def create_table(user):
    # ============================================================
    # creates a simple table with two columns and
    # two datasets filed with 3 values
    # ============================================================
    category = dict()
    category["name"] = "Allgemein"
    categoryF = CategoryForm(category)
    if categoryF.is_valid():
        newCategory = categoryF.save(commit=False)
        newCategory.save()

    table = dict()
    table["name"] = generate_random_username()
    table["created"] = datetime.now()

    tabF = TableForm(table)
    if tabF.is_valid():
        newTable = tabF.save(commit=False)
        newTable.creator = user
        newTable.category = newCategory
        newTable.save()

    return newTable

def create_columns(table, user):
    # ============================================================
    # - create a texttype
    # ============================================================
    texttype = Type(name="Text", type=0)
    texttype.save()

    # ============================================================
    # - creates a numerictype
    # ============================================================
    numerictype = Type(name="Numeric", type=1)
    numerictype.save()
    numericCond = TypeNumeric(type=numerictype, min=2, max=10)
    numericCond.save()

    # ============================================================
    # - creates a datetype
    # ============================================================
    datetype = Type(name="Type", type=2)
    datetype.save()

    # ============================================================
    # - creates a selectiontype
    # ============================================================
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

    # ============================================================
    # - creates a booleantype
    # ============================================================
    booleantype = Type(name="Boolean", type=4)
    booleantype.save()

    tabletype = Type(name="Table", type=5)
    tabletype.save()

    for i in range(0,4):
        columns = dict()
        columnsArray = ["TEXT" + table.name, "NUMERIC" + table.name, "DATE" + table.name,
                        "SELECTION" + table.name, "BOOLEAN" + table.name, "TABLE" + table.name ]
        columns["name"] = columnsArray[i]
        columns["created"] = datetime.now()
        columnsF = ColumnForm(columns)
        if columnsF.is_valid():
            newColumns = columnsF.save(commit=False)
            newColumns.table = table
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
            #if i == 5:
             #   newColumns.type = tabletype
            newColumns.creator = user
            newColumns.save()

            dataSets = dict()
            dataSets["created"] = datetime.now()
            dataSetsF = DatasetForm(dataSets)
            if dataSetsF.is_valid():
                newDataSets = dataSetsF.save(commit=False)
                newDataSets.column = newColumns
                newDataSets.creator = user
                newDataSets.table = table
                newDataSets.save()
                newDataSets.datasetID = table.generateDatasetID(newDataSets)
                newDataSets.save()
                # ============================================================
                # - the 1st column have a text data type
                # ============================================================
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
                            newDataText.creator = user
                            newDataText.save()
                # ============================================================
                # - the 2nd column have a numeric data type
                # ============================================================
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
                            newDataNummeric.creator = user
                            newDataNummeric.save()
                # ============================================================
                # -- the 3rd column have a date data type
                # ============================================================
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
                            newDataDate.creator = user
                            newDataDate.save()
                # ============================================================
                # -- the 4th column have a Selection data type
                # ============================================================
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
                            newDataSelection.creator = user
                            newDataSelection.save()
                # ============================================================
                # -- the 5th column have a boolean data type
                # ============================================================
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
                            newDataBoolean.creator = user
                            newDataBoolean.save()
                # ============================================================
                # -- the 6th column have a table datatype
                # ============================================================
                #if i == 5:
                #    op = dict()
                #    op["name"] = generate_random_username()
                #    op["created"] = datetime.now()
                #    opF = TableForm(op)
                #    if opF.is_valid():
                #        newOP = opF.save(commit=False)
                #        newOP.creator = testUser
                #        newOP.save()

                #        texttype2 = Type(name="Text", type=0)
                #        texttype2.save()

                #       texttype3 = Type(name="Text", type=0)
                #        texttype3.save()
#
#                        columnsOP = dict()
#                        columnsOP["name"] = i
#                        columnsOP["created"] = datetime.now()
#                        columnsOPF = ColumnForm(columnsOP)
#                        if columnsOPF.is_valid():
#                            newColumnsOP = columnsOPF.save(commit=False)
#                            newColumnsOP.table = newOP
#                            newColumnsOP.type = texttype2
#                            newColumnsOP.creator = testUser
#                            newColumnsOP.save()
#                            dataSetsOP = dict()
#                            dataSetsOP["created"] = datetime.now()
#                            dataSetsOPF = DatasetForm(dataSetsOP)
#                            if dataSetsOPF.is_valid():
#                                newDataSetsOP = dataSetsOPF.save(commit=False)
#                                newDataSetsOP.column = newColumnsOP
#                                newDataSetsOP.creator = testUser
#                                newDataSetsOP.table = newOP
#                                newDataSetsOP.save()
#                                newDataSetsOP.datasetID = newOP.generateDatasetID(newDataSetsOP)
#                                newDataSetsOP.save()
#                                dataText2 = dict()
#                                dataText2["created"] = datetime.now()
#                                dataText2["content"] = "HalloWelt!!!"
#                                dataText2F = DataTextForm(dataText2)
#                                if dataText2F.is_valid():
#                                    newDataText2 = dataText2F.save(commit=False)
#                                    newDataText2.column = newColumnsOP
#                                    newDataText2.dataset = newDataSetsOP
#                                    newDataText2.creator = testUser
#                                    newDataText2.save()

#                        columnsOP2 = dict()
#                        columnsOP2["name"] = i
#                        columnsOP2["created"] = datetime.now()
#                        columnsOP2F = ColumnForm(columnsOP2)
#                        if columnsOP2F.is_valid():
#                            newColumnsOP2 = columnsOP2F.save(commit=False)
#                            newColumnsOP2.table = newOP
#                            newColumnsOP2.type = texttype3
#                            newColumnsOP2.creator = testUser
#                            newColumnsOP2.save()
#                            dataSetsOP2 = dict()
#                            dataSetsOP2["created"] = datetime.now()
#                            dataSetsOP2F = DatasetForm(dataSetsOP2)
#                            if dataSetsOP2F.is_valid():
#                                newDataSetsOP2 = dataSetsOP2F.save(commit=False)
#                                newDataSetsOP2.column = newColumnsOP2
#                                newDataSetsOP2.creator = testUser
#                                newDataSetsOP2.table = newOP
#                                newDataSetsOP2.save()
#                                newDataSetsOP2.datasetID = newOP.generateDatasetID(newDataSetsOP2)
#                                newDataSetsOP2.save()
#                                dataText3 = dict()
#                                dataText3["created"] = datetime.now()
#                                dataText3["content"] = "HalloWelt!!!"
#                                dataText3F = DataTextForm(dataText3)
#                                if dataText3F.is_valid():
#                                    newDataText3 = dataText3F.save(commit=False)
#                                    newDataText3.column = newColumnsOP2
#                                    newDataText3.dataset = newDataSetsOP2
#                                    newDataText3.creator = testUser
#                                    newDataText3.save()

#                    dataTable = dict()
#                    dataTable["created"] = datetime.now()
#                    dataTableF = DataTableForm(dataTable)
#                    if dataTableF.is_valid():
#                        newDataTable = dataTableF.save(commit=False)
#                        newDataTable.column = newColumns
#                        newDataTable.dataset = newDataSets
#                        newDataTable.creator = testUser
#                        newDataTable.save()

#                    dataTableToDataSets = DataTableToDataset(DataTable=newDataTable, dataset=newDataSetsOP)
#                    dataTableToDataSets.save()

#                    dataTableToDataSets2 = DataTableToDataset(DataTable=newDataTable, dataset=newDataSetsOP2)
#                    dataTableToDataSets2.save()

    return newColumns

def create_Group(**kwargs):
    # ============================================================
    # creates a group with 1000 members
    # ============================================================
    groupA = dict()
    groupA["name"] = (generate_random_username())
    groupF = DBGroupForm(groupA)
    if groupF.is_valid():
        newDBGroup = groupF.save()
        newDBGroup.save()
    for i in range(1,1001):
        user = DBUser.objects.create_user(username=generate_random_username())
        user.save()
        m = dict()
        m["isAdmin"] = False
        mF = MembershipForm(m)
        if mF.is_valid():
            newm = mF.save(commit=False)
            newm.user = user
            newm.group = newDBGroup
            newm.save()

    GroupSerializer.serializeOne(groupA["name"])
    return newDBGroup

def create_UserWithName(name, password):
    user = DBUser.objects.create_user(username=name, password=password)
    user.save()
    return user

def create_RandomUser():
    user = DBUser.objects.create_user(username=generate_random_username(), tableCreator=True)
    user.save()
    return user

def connect_User_With_Rights(user, table):
    # ============================================================
    # creates a User with rights
    # ============================================================
    rights = dict()
    rightsF = RightListForTableForm(rights)
    if rightsF.is_valid():
        newRights = rightsF.save(commit=False)
        newRights.user = user
        newRights.table = table
        newRights.save()
        return newRights