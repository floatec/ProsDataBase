# Create your views here.
# -*- coding: UTF-8 -*-

from django.http import HttpResponse
import sys, json
from ..serializers import *
from ..forms import *

from datetime import datetime


def showAllUsers(request):
    if request.method == 'GET':
        user = UserSerializer.serializeAll()
        return HttpResponse(json.dumps(user), content_type="application/json")


def groups(request):
    if request.method == 'GET':
        return showAllGroups()
    elif request.method == 'POST':
        return addGroup(request)


def group(request, name):
    if request.method == 'PUT':
        return modifyGroup(request, name)
    if request.method == 'GET':
        return showOneGroup(name)


def tables(request):
    if request.method == 'GET':
        return showAllTables()
    if request.method == 'POST':
        return addTable(request)


def table(request, name):
    if request.method == 'GET':
        return showTable(request, name)
    if request.method == 'POST':
        return insertData(request, name)
    if request.method == "DELETE":
        return deleteTable(name)


def datasets(request, tableName):
    if request.method == 'POST':
        return showDatasets(request, tableName)
    if request.method == 'DELETE':
        return deleteDatasets(request, tableName)


def dataset(request, tableName, datasetID):
    if request.method == 'GET':
        return showDataset(tableName, datasetID)
    elif request.method == 'PUT':
        return modifyData(request, tableName, datasetID)
    elif request.method == 'DELETE':
        return deleteDataset(tableName, datasetID)


def showAllGroups():
    groups = GroupSerializer.serializeAll()
    return HttpResponse(json.dumps(groups), content_type="application/json")


def showOneGroup(name):
    group = GroupSerializer.serializeOne(name)
    return HttpResponse(json.dumps(group), content_type="application/json")


def addGroup(request):
    request = json.loads(request.raw_post_data)

    groupNames = list()
    for name in DBGroup.objects.all():
        groupNames.append(name)

    if request["name"] in groupNames:
        HttpResponse(content="Group with name " + request["name"] + " already exists.", status=400)

    groupF = DBGroupForm({"name": request["name"]})
    if groupF.is_valid():
        newGroup = groupF.save(commit=False)
        newGroup.tableCreator = request["tableCreator"]
        newGroup.groupCreator = request["groupCreator"]
        newGroup.save()

        failed = list() # list of users whose names could not be found in the database
        for adminName in set(request["admins"]):
            try:
                admin = DBUser.objects.get(username=adminName)
            except DBUser.DoesNotExist:
                if len(adminName) > 0:
                    failed.append(adminName)
                continue
            membership = Membership(group=newGroup, user=admin)
            membership.isAdmin = True
            membership.save()

        for userName in set(request["users"]) - set(request["admins"]):
            try:
                user = DBUser.objects.get(username=userName)
            except DBUser.DoesNotExist:
                if len(userName) > 0:
                    failed.append(userName)
                continue
            membership = Membership(group=newGroup, user=user)
            membership.save()

    if len(failed) > 0:
        return HttpResponse({"error": "following users could not be added to the group: " + str(failed) + ". Have you misspelled them?"}, content_type="application/json")
    return HttpResponse("Successfully saved group " + request["name"] + ".", status=200)


def modifyGroup(request, name):
    pass


def showTable(request, name):
    if request.method == 'GET':
        table = TableSerializer.serializeOne(name)
        return HttpResponse(json.dumps(table), content_type="application/json")


def tableStructure(request, name):
    if request.method == 'GET':
        structure = TableSerializer.serializeStructure(name)
        return HttpResponse(json.dumps(structure), content_type="application/json")


def showDatasets(request, tableName):
    try:
        Table.objects.get(name=tableName)
    except Table.DoesNotExist:
        return HttpResponse(content="Could not find table with name " + tableName + ".", status=400)

    request = json.loads(request.raw_post_data)
    result = dict()
    result["datasets"] = list()
    for id in request["datasets"]:
        result["datasets"].append(DatasetSerializer.serializeOne(id))

    return HttpResponse(json.dumps(result), content_type="application/json")


def showDataset(tableName, datasetID):
    try:
        table = Table.objects.get(name=tableName)
    except Table.DoesNotExist:
        return HttpResponse(content="Table with name " + tableName + " could not be found.", status=400)
    try:
        dataset = Dataset.objects.get(datasetID=datasetID, table=table)
    except Dataset.DoesNotExist:
        return HttpResponse(content="dataset with id " + datasetID + " could not be found in table " + tableName + ".", status=400)

    if dataset.deleted:
        return HttpResponse("The requested dataset does not exist.", status=400)
    else:
        dataset = DatasetSerializer.serializeOne(datasetID)
        return HttpResponse(json.dumps(dataset), content_type="application/json")


def deleteDatasets(request, tableName):
    try:
        Table.objects.get(name=tableName)
    except Table.DoesNotExist:
        return HttpResponse(content="Could not find table " + tableName + " to delete from.", status=400)

    request = json.loads(request.raw_post_data)
    deleted = list()
    for id in request:
        try:
            dataset = Dataset.objects.get(datasetID=id)
        except Dataset.DoesNotExist:
            continue
        if dataset.deleted:
            continue
        dataset.deleted = True
        dataset.modifed = datetime.now()
        dataset.modifier = DBUser.objects.get(username="test")
        dataset.save()
        deleted.append(id)

    return HttpResponse(json.dumps({"deleted": deleted}), content_type="application/json")


def deleteDataset(tableName, datasetID):
    try:
        table = Table.objects.get(name=tableName)
    except Table.DoesNotExist:
        return HttpResponse(content="Could not find table " + tableName + " to delete from.", status=400)
    try:
        dataset = Dataset.objects.get(datasetID=datasetID, table=table)
    except Dataset.DoesNotExist:
        return HttpResponse(content="Could not find dataset with id " + datasetID + " in table " + tableName + ".", status=400)

    if dataset.deleted:
        return HttpResponse(content="Dataset with id " + datasetID + " does not exist.", status=400)
    dataset.deleted = True
    dataset.modified = datetime.now()
    dataset.modifier = DBUser.objects.get(username="test")
    dataset.save()
    return HttpResponse("Successfully deleted dataset with id " + datasetID + " from table " + tableName + ".", status=200)


def insertData(request, tableName):
    """
    Insert a dataset into a table.

    Receives data in json format:
    {
        "columns": [
            {"name": "colname1", "value": "val1"},
            {"name": "colname2", "value": ["3.2013_44_T", "3.2013_43_Q", "3.2013_45_L"], "table": "referencedTableName"} // for TypeTable columns
        ]
    }
    """
    request = json.loads(request.raw_post_data)
    try:
        theTable = Table.objects.get(name=tableName)
    except Table.DoesNotExist:
        return HttpResponse(content="table with name " + tableName + " not found.", status=400)

    datasetF = DatasetForm({"created": datetime.now()})
    if not datasetF.is_valid():
        return HttpResponse(content="Error creating a new dataset.", status=500)

    newDataset = datasetF.save(commit=False)
    newDataset.table = theTable
    newDataset.creator = DBUser.objects.get(username="test")
    newDataset.save()
    newDataset.datasetID = theTable.generateDatasetID(newDataset)
    newDataset.save()

    for col in request["columns"]:
        try:
            column = Column.objects.get(name=col["name"], table=theTable)
        except Column.DoesNotExist:
            HttpResponse(content="Could not find a column with name " + col["name"] + "in table " + tableName + ".", status=400)
            continue
        print "col " + col["name"]
        if not column.type.getType().isValid(col["value"]):
            return HttpResponse(content="input " + unicode(col["value"]) + " for column " + column.name + " is not valid.", status=400)

        if column.type.type == Type.TEXT:
            textF = DataTextForm({"created": datetime.now(), "content": col["value"]})
            if textF.is_valid():
                newData = textF.save(commit=False)

        elif column.type.type == Type.NUMERIC:
            numF = DataNumericForm({"created": datetime.now(), "content": col["value"]})
            if numF.is_valid():
                newData = numF.save(commit=False)

        elif column.type.type == Type.DATE:
            dateF = DataDateForm({"created": datetime.now(), "content": col["value"]})
            if dateF.is_valid():
                newData = dateF.save(commit=False)

        elif column.type.type == Type.SELECTION:
            selF = DataSelectionForm({"created": datetime.now(), "content": col["value"]})
            if selF.is_valid():
                newData = selF.save(commit=False)

        elif column.type.type == Type.BOOL:
            boolF = DataBoolForm({"created": datetime.now(), "content": col["value"]})
            if boolF.is_valid():
                newData = boolF.save(commit=False)

        elif column.type.type == Type.TABLE:
            dataTblF = DataTableForm({"created": datetime.now()})
            if dataTblF.is_valid():
                newData = dataTblF.save(commit=False)

        if newData is None:
            return HttpResponse(content="Could not add data for column + " + col["name"] + ". The content type was not valid.", status=400)

        else:
            newData.creator = DBUser.objects.get(username="test")
            newData.column = column
            newData.dataset = newDataset
            newData.save()

        if column.type.type == Type.TABLE and newData is not None:
            for index in col["value"]:  # find all datasets for this
                try:
                    dataset = Dataset.objects.get(datasetID=index)
                except Dataset.DoesNotExist:
                    return HttpResponse(content="dataset with id " + index + " could not be found in table " + column.type.getType().table.name + ".", status=400)
                else:
                    link = DataTableToDataset()
                    link.DataTable = newData
                    link.dataset = dataset
                    link.save()

    return HttpResponse(json.dumps({"id": newDataset.datasetID}), content_type="application/json", status=200)


def modifyData(request, tableName, datasetID):
    """
    Modify a table's dataset.

    Receives data in json format:
    {
        "columns": [
            {"column": "column1", "value": 0},
            {"column": "column2", "value": "2013-12-07 22:07:00"},
            {"column": "column3", "value": ["3.2013_44_T", "3.2013_43_Q", "3.2013_45_L"]}
        ]
    }
    """
    request = json.loads(request.raw_post_data)
    try:
        theTable = Table.objects.get(name=tableName)
    except Table.DoesNotExist:
        return HttpResponse(content="table with name" + tableName + " not found.", status=400)
    try:
        dataset = Dataset.objects.get(datasetID=datasetID)
    except Dataset.DoesNotExist:
        return HttpResponse(content="Could not find dataset with id " + datasetID + " in table " + tableName + ".", status=400)

    dataCreatedNewly = False  # is set to True if a data element was not modified but created newly
    newData = None
    for col in request["columns"]:
        try:
            column = Column.objects.get(name=col["name"], table=theTable)
        except Column.DoesNotExist:
            return HttpResponse("Could not find column with name " + col["name"] + ".", status=400)
            continue

        if not column.type.getType().isValid(col["value"]):
            return HttpResponse(content="input " + unicode(col["value"]) + " for column " + column.name + " is not valid.", status=400)

        if column.type.type == Type.TEXT:
            try:
                text = dataset.datatext.get(column=column)
                text.modified = datetime.now()
                text.modifier = DBUser.objects.get(username="test")
                text.content = col["value"]
                text.save()
            except DataText.DoesNotExist:
                dataCreatedNewly = True
                textF = DataTextForm({"created": datetime.now(), "content": col["value"]})
                if textF.is_valid():
                    newData = textF.save(commit=False)

        elif column.type.type == Type.NUMERIC:
            try:
                num = dataset.datanumeric.get(column=column)
                num.modified = datetime.now()
                num.modifier = DBUser.objects.get(username="test")
                num.content = col["value"]
                num.save()
            except DataNumeric.DoesNotExist:
                dataCreatedNewly = True
                numF = DataNumericForm({"created": datetime.now(), "content": col["value"]})
                if numF.is_valid():
                    newData = numF.save(commit=False)

        elif column.type.type == Type.DATE:
            try:
                date = dataset.datadate.get(column=column)
                date.modified = datetime.now()
                date.modifier = DBUser.objects.get(username="test")
                date.content = col["value"]
                date.save()
            except DataDate.DoesNotExist:
                dataCreatedNewly = True
                dateF = DataDateForm({"created": datetime.now(), "content": col["value"]})
                if dateF.is_valid():
                    newData = dateF.save(commit=False)

        elif column.type.type == Type.SELECTION:
            try:
                sel = dataset.dataselection.get(column=column)
                sel.modified = datetime.now()
                sel.modifier = DBUser.objects.get(username="test")
                sel.content = col["value"]
                sel.save()
            except DataSelection.DoesNotExist:
                dataCreatedNewly = True
                selF = DataSelectionForm({"created": datetime.now(), "content": col["value"]})
                if selF.is_valid():
                    newData = selF.save(commit=False)

        elif column.type.type == Type.BOOL:
            try:
                bool = dataset.databool.get(column=column)
                bool.modified = datetime.now()
                bool.modifier = DBUser.objects.get(username="test")
                bool.content = col["value"]
                bool.save()
            except DataBool.DoesNotExist:
                dataCreatedNewly = True
                boolF = DataBoolForm({"created": datetime.now(), "content": col["value"]})
                if boolF.is_valid():
                    newData = boolF.save(commit=False)

        elif column.type.type == Type.TABLE:
            try:
                dataTbl = dataset.datatable.get(column=column)
                links = DataTableToDataset.objects.filter(DataTable=dataTbl)
                setIDs = list()
                #  remove all links between dataTable and datasets which are not listed in col["value"]
                for link in links:
                    setIDs.append(link.dataset_id)
                    if link.dataset_id not in col["value"]:
                        link.delete()

                #  now add any link that does not exist yet
                for id in [index for index in col["value"] if index not in setIDs]:  # this list comprehension returns the difference col["value"] - setIDs
                    try:
                        newDataset = Dataset.objects.get(datasetID=id)
                        newLink = DataTableToDataset()
                        newLink.DataTable = dataTbl
                        newLink.dataset = newDataset
                        newLink.save()
                    except Dataset.DoesNotExist:
                        return HttpResponse(content="Could not find dataset with id " + id + ".", status=400)

            except DataTable.DoesNotExist:
                dataCreatedNewly = True
                dataTblF = DataTableForm({"created": datetime.now()})
                if dataTblF.is_valid():
                    newData = dataTblF.save(commit=False)

        if dataCreatedNewly:
            if newData is None:
                return HttpResponse(content="Could not add data to column " + col["name"] + ". The content type was invalid.", status=400)

            else:
                newData.creator = DBUser.objects.get(username="test")
                newData.column = column
                newData.dataset = Dataset.objects.get(datasetID=datasetID)
                newData.save()

            # this must be performed at the end, because DatatableToDataset receives newData, which has to be saved first
            if column.type.type == Type.TABLE and newData is not None:
                for index in col["value"]:  # find all datasets for this
                    try:
                        dataset = Dataset.objects.get(pk=index)
                        link = DataTableToDataset()
                        link.DataTable = newData
                        link.dataset = dataset
                        link.save()
                    except Dataset.DoesNotExist:
                        return HttpResponse(content="Could not find dataset with id " + index + ".", status=400)

    return HttpResponse(json.dumps({"id": dataset.datasetID}), status=200)


def showAllTables():
    tables = TableSerializer.serializeAll()
    return HttpResponse(json.dumps(tables), content_type="application/json") if tables is not None \
        else HttpResponse(status=500)


def addTable(request):
    """
    add table to database.

    This function adds datasets to the tables 'Table', 'RightListForTable', 'RightListForColumn', 'Column', 'Type'
    and corresponding datatype tables (e.g. 'TypeNumeric').
    If the datatype is 'TypeSelection', the selection options are also added to the table 'SelectionValue'

    {
      "name": "example",
      "columns": [
            {"name": "columname", "required": 1, "type": 1,
                "options": {"0": "yes", "1": "no", "2": "maybe"},
                "rights": {
                    "users" : { "8": ["read"], "17": ["modify", "read"]},
                    "groups": {"1001": ["modify", "delete", "read"]}
                }
            },
            {"name": "anothercolum", "required": 0, "type": 1,
                "options": {"0": "yes", "1": "no", "2": "maybe"},
                "rights": {
                    "users" : { "8": ["read"], "17": ["modify", "read"]},
                    "groups": {"1001": ["modify", "delete", "read"]}
                }
            }
        ],
      "rights": {
          "users": {"1": ["rightsAdmin", "viewLog"], "2": ["insert"]},
          "groups": {"1001": ["rightsAdmin", "insert"]}
      }
    }
    """
    request = json.loads(request.raw_post_data)
    # add to table 'Table'
    table = dict()
    table["name"] = request["name"]
    table["created"] = datetime.now()

    tableF = TableForm(table)
    if tableF.is_valid():
        newTable = tableF.save(commit=False)
        newTable.creator = DBUser.objects.get(username="test")
        newTable.save()
    else:
        return HttpResponse("Could not create table.")

    # add to table 'RightlistForTable' for user
    if "rights" in request:
        for item in request["rights"]["users"]:
            rightList = dict()
            rightList["viewLog"] = True if "viewLog" in item["rights"] else False
            rightList["rightsAdmin"] = True if "rightsAdmin" in item["rights"] else False
            rightList["insert"] = True if "insert" in item["rights"] else False
            rightList["delete"] = True if "delete" in item["rights"] else False
            rightListF = RightListForTableForm(rightList)

            if rightListF.is_valid():
                newRightList = rightListF.save(commit=False)
                newRightList.table = newTable

                user = DBUser.objects.get(username=item["name"])
                newRightList.user = user
                newRightList.save()

            else:
                return HttpResponse("Could not create user's rightlist for table.")

         # add to table 'RightlistForTable' for group
        for item in request["rights"]["groups"]:
            rightList = dict()
            rightList["viewLog"] = True if "viewLog" in item["rights"] else False
            rightList["rightsAdmin"] = True if "rightsAdmin" in item["rights"] else False
            rightList["insert"] = True if "insert" in item["rights"] else False
            rightList["delete"] = True if "delete" in item["rights"] else False
            rightListF = RightListForTableForm(rightList)
            if rightListF.is_valid():
                newRightList = rightListF.save(commit=False)
                newRightList.table = newTable

                group = DBGroup.objects.get(name=item["name"])
                newRightList.group = group
                newRightList.save()
            else:
                return HttpResponse("Could not create group's rightlist for table")

    for col in request["columns"]:
        # add to table 'Datatype'
        newDatatype = Type(name=col["name"], type=col["type"])
        newDatatype.save()

        # add to corresponding datatype table
        type = dict()
        if col["type"] == Type.TEXT:
            type["length"] = col["length"]
            typeTextF = TypeTextForm(type)
            if typeTextF.is_valid():
                newText = typeTextF.save(commit=False)
                newText.type = newDatatype
                newText.save()
            else:
                return HttpResponse("Could not create text type")

        elif col["type"] == Type.NUMERIC:
            type["min"] = col["min"] if "min" in col else -sys.maxint
            type["max"] = col["max"] if "max" in col else sys.maxint

            typeNumericF = TypeNumericForm(type)
            if typeNumericF.is_valid():
                newNumeric = typeNumericF.save(commit=False)
                newNumeric.type = newDatatype
                newNumeric.save()
            else:
                return HttpResponse("Could not create numeric type")

        elif col["type"] == Type.DATE:
            if "min" in col:
                type["min"] = col["min"]
            if "max" in col:
                type["max"] = col["max"]

            if "min" in type and "max" in type:
                typeDateF = TypeDateForm(type)
                if typeDateF.is_valid():
                    typeDate = typeDateF.save()
                    typeDate.type = newDatatype
                    typeDate.save()
                else:
                    return HttpResponse("Could not create date type")
            else:
                typeDate = TypeDate()
                typeDate.type = newDatatype
                typeDate.save()

        elif col["type"] == Type.SELECTION:
            typeSelF = TypeSelectionForm({"count": len(col["options"]), })
            if typeSelF.is_valid():
                typeSel = typeSelF.save(commit=False)
                typeSel.type = newDatatype
                typeSel.save()
            else:
                return HttpResponse("Could not create Selection")

            for option in col["options"]:
                selValF = SelectionValueForm({"index": option["key"], "content": option["value"]})
                if selValF.is_valid():
                    selVal = selValF.save(commit=False)
                    selVal.typeSelection = typeSel
                    selVal.save()
                else:
                    return HttpResponse("Could not create Selection value")

        elif col["type"] == Type.BOOL:
            typeBool = TypeBool()
            typeBool.type = newDatatype
            typeBool.save()

        elif col["type"] == Type.TABLE:
            newTypeTable = TypeTable()
            newTypeTable.table = Table.objects.get(name=col["table"])
            newTypeTable.type = newDatatype
            newTypeTable.save()

        # add to table 'Column'
        column = dict()
        column["name"] = col["name"]
        column["created"] = datetime.now()
        columnF = ColumnForm(column)
        if columnF.is_valid():
            newColumn = columnF.save(commit=False)
            newColumn.creator = DBUser.objects.get(username="test")
            newColumn.type = newDatatype
            newColumn.table = newTable
            newColumn.save()
        else:
            return HttpResponse("Could not create new column " + col["name"])
        if "rights" in col:
            # add to table "RightListForColumn" for users
            for item in col["rights"]["users"]:
                rightList = dict()
                rightList["read"] = 1 if "read" in item["rights"] else 0
                rightList["modify"] = 1 if "modify" in item["rights"] else 0
                rightListF = RightListForColumnForm(rightList)
                if rightListF.is_valid():
                    newRightList = rightListF.save(commit=False)
                    newRightList.column = newColumn

                    user = DBUser.objects.get(username=item["name"])
                    newRightList.user = user
                    newRightList.save()
                else:
                    return HttpResponse("could not create column right list for user")
            # add to table 'RightListForColumn' for groups
            for item in col["rights"]["groups"]:
                rightList = dict()
                rightList["read"] = 1 if "read" in item["rights"] else 0
                rightList["modify"] = 1 if "modify" in item["rights"] else 0
                rightListF = RightListForColumnForm(rightList)
                if rightListF.is_valid():
                    newRightList = rightListF.save(commit=False)
                    newRightList.column = newColumn

                    group = DBGroup.objects.get(name=item["name"])
                    newRightList.group = group
                    newRightList.save()
                else:
                    return HttpResponse("Could not create column right list for group")

    return HttpResponse(status=200)


def deleteTable(name):
    try:
        table = Table.objects.get(name=name)
    except Table.DoesNotExist:
        HttpResponse(content="Could not find table with name " + name + ".", status=400)

    if table.deleted:
        HttpResponse(content="Table with name " + name + " does not exist.", status=400)

    datasets = list()
    for dataset in table.datasets.all():
        datasets.append(dataset)
        dataset.deleted = True
        dataset.modified = datetime.now()
        dataset.modifier = DBUser.objects.get(username="test")
        dataset.save()

    columns = list()
    for column in table.columns.all():
        columns.append(column)
        column.deleted = True
        column.modified = datetime.now()
        column.modifier = DBUser.objects.get(username="test")
        column.save()

    table.deleted = True
    table.modified = datetime.now()
    table.modifier = DBUser.objects.get(username="test")
    table.name = table.name + "_DELETED_" + str(datetime.now())
    table.save()

    for col in columns:
        col.table = table
        col.save()

    for dataset in datasets:
        dataset.table = table
        dataset.save()

    return HttpResponse(json.dumps({"deleted": table.name}), status=200)