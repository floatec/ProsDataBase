# Create your views here.
# -*- coding: UTF-8 -*-

from django.http import HttpResponse, HttpRequest
import sys

from ..serializers import *
from ..forms import *

from datetime import datetime


def table(request):
    if request.method == 'POST':
        return addTable(request)
    if request.method == 'GET':
        return showAllTables(request)


def showTable(request, name):
    if request.method == 'GET':
        return HttpResponse(TableSerializer.serializeOne(name), content_type="application/json")


def tableStructure(request, name):
    if request.method == 'GET':
        structure = TableSerializer.serializeStructure(name)
        return HttpResponse(structure, content_type="application/json") if structure is not None \
            else HttpResponse(status=500)


def insertData(request):
    """
    Insert a dataset into a table.

    Receives data in json format:
    {
        "table": "tablename",
        "columns": [
            {"name": "colname1", "value": val1},
            {"name": "colname2", "value": [0, 1, 2], "table": "referencedTableName"} // for TypeTable columns
        ]
    }

    Tries to add as much data as possible as long as the table exists. Invalid columns, that is nonexistent columns
    or columns with invalid type, are skipped, but a note will be returned.
    Also, invalid datasets for global object columns are skipped, but a note will be returned.
    """
    if request.method == 'POST':
        request = json.loads(request.raw_post_data)
        try:
            theTable = Table.objects.get(name=request["table"])
        except Table.DoesNotExist:
            return HttpResponse(content="table with name" + request["table"] + " not found.", status=400)

        datasetF = DatasetForm({"created": datetime.now()})
        if not datasetF.is_valid():
            return HttpResponse(content="Error creating a new dataset.", status=500)

        newDataset = datasetF.save(commit=False)
        newDataset.table = theTable
        newDataset.creator = DBUser.objects.get(username="test")
        newDataset.save()

        dataFails = []  # collects all columns by name for wich data could not be saved
        missingDatasets = []  # collects all datasets which could not be found in the global object
        for col in request["columns"]:
            try:
                column = Column.objects.get(name=col["name"], table=theTable)
            except Column.DoesNotExist:
                dataFails.append(col["name"])
                continue

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
                table = Table.objects.get(name=col["table"])
                if table is None:
                    return HttpResponse(content="Global object " + col["table"] + " could not be found", status=400)

                dataTblF = DataTableForm({"created": datetime.now()})
                if dataTblF.is_valid():
                    newData = dataTblF.save(commit=False)

            if newData is None:
                dataFails.append(col["name"])

            else:
                newData.creator = DBUser.objects.get(username="test")
                newData.column = column
                newData.dataset = newDataset
                newData.save()

            if column.type.type == Type.TABLE and newData is not None:
                for index in col["value"]:  # find all datasets for this
                    try:
                        dataset = Dataset.objects.get(pk=index)
                    except Dataset.DoesNotExist:
                        missingDatasets.append(index)
                    else:
                        link = DataTableToDataset()
                        link.DataTable = newData
                        link.dataset = dataset
                        link.save()

        if len(dataFails) > 0:
            if len(missingDatasets) > 0:
                return HttpResponse(content="Note: Failed to add data to following columns: " + unicode(dataFails) +
                                            ". For the global object datasets with following indices could not be found: " + unicode(missingDatasets) + ".", status=200)
            return HttpResponse(content="Note: Failed to add data to following columns: " + unicode(dataFails) + ".", status=200)

        if len(missingDatasets) > 0:
            return HttpResponse(content="Note: For the global object datasets with following indices could not be found: " + unicode(missingDatasets) + ".", status=200)

        return HttpResponse(content="Saved dataset successfully.", status=200)


def modifyData(request, datasetID):
    """
    Modify a table's dataset.

    Receives data in json format:
    {
        "table": "tablename",
        "dataset": [ {"column": "name", "value": 0}, {"column": "columnname", "value": val1}, {"column": "anothercolumn", "value": val2} ]
    }

    Tries to write as much data as possible as long as the table and specified dataset exist. Invalid columns, that is nonexistent columns
    or columns with invalid type, are skipped, but a note will be returned.
    Also, invalid datasets for global object columns are skipped, but a note will be returned.
    """
    if request.method == 'POST':
        request = json.loads(request.raw_post_data)
        try:
            theTable = Table.objects.get(name=request["table"])
        except Table.DoesNotExist:
            return HttpResponse(content="table with name" + request["table"] + " not found.", status=400)
        try:
            dataset = Dataset.objects.get(pk=datasetID)
        except Dataset.DoesNotExist:
            return HttpResponse(content="Could not find dataset with id " + datasetID + " in table " + request["table"] + ".", status=400)

        dataFails = []  # collects all columns by name for wich data could not be saved
        missingDatasets = []  # collects all datasets which could not be found in the global object
        dataCreatedNewly = False  # is set to True if a data element was not modified but created newly
        newData = None
        for col in request["dataset"]:
            try:
                column = Column.objects.get(name=col["column"], table=theTable)
            except Column.DoesNotExist:
                dataFails.append(col["column"])
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
                            newDataset = Dataset.objects.get(pk=id)
                            newLink = DataTableToDataset()
                            newLink.DataTable = dataTbl
                            newLink.dataset = newDataset
                            newLink.save()
                        except Dataset.DoesNotExist:
                            missingDatasets.append(id)

                except DataTable.DoesNotExist:
                    dataCreatedNewly = True
                    dataTblF = DataTableForm({"created": datetime.now()})
                    if dataTblF.is_valid():
                        newData = dataTblF.save(commit=False)

            if dataCreatedNewly:
                if newData is None:
                    dataFails.append(col["name"])

                else:
                    newData.creator = DBUser.objects.get(username="test")
                    newData.column = column
                    newData.dataset = newDataset
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
                            missingDatasets.append(index)

        if len(dataFails) > 0:
            if len(missingDatasets) > 0:
                return HttpResponse(content="Note: Failed to add data to following columns: " + unicode(dataFails) +
                                            ". For the global object datasets with following indices could not be found: " + unicode(missingDatasets) + ".", status=200)
            return HttpResponse(content="Note: Failed to add data to following columns: " + unicode(dataFails) + ".", status=200)

        if len(missingDatasets) > 0:
            return HttpResponse(content="Note: For the global object datasets with following indices could not be found: " + unicode(missingDatasets) + ".", status=200)

        return HttpResponse(content="Saved dataset successfully.", status=200)


def showAllUsers(request):
    if request.method == 'GET':
        user = UserSerializer.serializeAll()
        return HttpResponse(user, content_type="application/json")


def showAllGroups(request):
    if request.method == 'GET':
        user = GroupSerializer.serializeAll()
        return HttpResponse(user, content_type="application/json")


def showAllTables(request):
    if request.method == 'GET':
        tables = TableSerializer.serializeAll()
        return HttpResponse(tables, content_type="application/json") if tables is not None \
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
    if request.method == "POST":
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
                    selValF = SelectionValueForm({"index": option["id"], "content": option["value"]})
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
            column["required"] = col["required"]
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