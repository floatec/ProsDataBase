# Create your views here.

from django.http import HttpResponse, HttpRequest

from serializers import *
from forms import *
from datetime import datetime


def table(request):
    if request.method == 'GET':
        showAllTables(request)
    if request.method == 'POST':
        addTable(request)

def showAllTables(request):
    if request.method == 'GET':
        tables = TableSerializer.serializeAll()
        return HttpResponse(tables, content_type="application/json")


def showAllUsers(request):
    if request.method == 'GET':
        user = UserSerializer.serializeAll()
        return HttpResponse(user, content_type="application/json")


def showAllGroups(request):
    if request.method == 'GET':
        user = GroupSerializer.serializeAll()
        return HttpResponse(user, content_type="application/json")


def addTable(request):
    """
    add table to database.

    This function adds datasets to the tables 'Table', 'RightListForTable', 'RightListForColumn', 'Column', 'Type'
    and corresponding datatype tables (e.g. 'TypeNumeric').
    If the datatype is 'TypeSelection', the selection options are also added to the table 'SelectionValue'

{
  "name": "example",
  "admin": [4, 23, 10003],  //group ids have an offset of say 10000, to distinguish from user ids
  "column": [
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
      "users": {"1": ["rightAdmin", "viewLog"], "2": ["insert"]},
      "groups": {"1001": ["rightsAdmin", "insert"]}
  }
}
    """
    if request.method == "POST":
        # add to table 'Table'
        dataTable = dict()
        dataTable["name"] = HttpRequest.POST["name"]
        dataTable["creator"] = request.user
        dataTable["created"] = datetime.now()

        tableF = TableForm(dataTable)
        if tableF.is_valid():
            newTable = tableF.save()
            newTable.save()

        # add to table 'RightlistForTable' for user
        for userID, rights in request["rights"]["users"]:
            rightList = dict()
            rightList["viewLog"] = True if "viewLog" in rights else False
            rightList["rightsAdmin"] = True if "rightsAdmin" in rights else False
            rightList["insert"] = True if "insert" in rights else False
            rightListF = RightListForTableForm(rightList)

            if rightListF.is_valid():
                newRightList = rightListF.save()
                newRightList.table = newTable

                user = DBUser.objects.get(id=userID)
                newRightList.user = user
                newRightList.save()

         # add to table 'RightlistForTable' for group
        for groupID, rights in request["rights"]["groups"]:
            rightList = dict()
            rightList["viewLog"] = True if "viewLog" in rights else False
            rightList["rightsAdmin"] = True if "rightsAdmin" in rights else False
            rightList["insert"] = True if "insert" in rights else False
            rightListF = RightListForTableForm(rightList)
            if rightListF.is_valid():
                newRightList = rightListF.save()
                newRightList.table = newTable

                group = DBGroup.objects.get(id=groupID)
                newRightList.group = group
                newRightList.save()

        for col in request["columns"]:
            # add to table 'Column'
            column = dict()
            column["name"] = col["name"]
            column["type"] = col["type"]
            column["required"] = col["required"]
            columnF = ColumnForm(column)
            if columnF.is_valid():
                newColumn = columnF.save()
                newColumn.creator = request.user
                newColumn.created = datetime.now()
                newColumn.table = Table.objects.get(request["name"])
                newColumn.save()

            # add to table 'RightListForColumn' for users
            for userID, rights in request["columns"]["rights"]["users"]:
                rightList = dict()
                rightList["viewLog"] = 1 if "viewLog" in rights else 0
                rightList["rightsAdmin"] = 1 if "rightsAdmin" in rights else 0
                rightList["insert"] = 1 if "insert" in rights else 0
                rightListF = RightListForTableForm(rightList)
                if rightListF.is_valid():
                    newRightList = rightListF.save()
                    newRightList.table = newTable

                    user = DBUser.objects.get(id=userID)
                    newRightList.user = user
                    newRightList.save()

            # add to table 'RightListForColumns' for groups
            for groupID, rights in request["columns"]["rights"]["users"]:
                rightList = dict()
                rightList["viewLog"] = 1 if "viewLog" in rights else 0
                rightList["rightsAdmin"] = 1 if "rightsAdmin" in rights else 0
                rightList["insert"] = 1 if "insert" in rights else 0
                rightListF = RightListForTableForm(rightList)
                if rightListF.is_valid():
                    newRightList = rightListF.save()
                    newRightList.table = newTable

                    group = DBGroup.objects.get(id=groupID)
                    newRightList.group = group
                    newRightList.save()

            # add to table 'Datatype'
            newDatatype = TypeForm({col["name"], })
            if newDatatype.is_valid():
                newDatatype.save()

            # add to corresponding datatype table
            type = dict()
            if col["type"] == Type.TEXT:
                type["length"] = col["length"]
                typeTextF = TypeTextForm(type)
                if typeTextF.is_valid():
                    newText = typeTextF.save()
                    newText.type = newDatatype
                    newText.save()

            elif col["type"] == Type.NUMERIC or col["type"] == Type.DATE:
                type["min"] = col["min"]
                type["max"] = col["max"]
                typeNumericF = TypeNumericForm(type)
                if typeNumericF.is_valid():
                    newNumeric = typeNumericF.save()
                    newNumeric.type = newDatatype
                    newNumeric.save()

            elif col["type"] == Type.TABLE:
                newTypeTable = TypeTable()
                newTypeTable.table = newTable
                newTypeTable.type = newDatatype
                newTypeTable.save()

            elif col["type"] == Type.SELECTION:
                typeSelF = TypeSelectionForm({"count": len(col["options"]), })
                if typeSelF.is_valid():
                    typeSel = typeSelF.save()
                    typeSel.type = newDatatype
                    typeSel.save()

                for key, val in col["options"]:
                    selValF = SelectionValueForm({key, val})
                    if selValF.is_valid():
                        selVal = selValF.save()
                        selVal.typeSelection = typeSel

        return HttpResponse(status=200)