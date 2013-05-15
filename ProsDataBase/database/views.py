# Create your views here.

from django.http import HttpResponse, HttpRequest

from serializers import *
from forms import *
from datetime import datetime


def showAllTables(request):
    if request.method == 'GET':
        tables = TableSerializer.serializeAll()
        return HttpResponse(tables, content_type="application/json")

def showAllUser(request):
    if request.method == 'GET':
        user = UserSerializer.serializeAll()
        return HttpResponse(user, content_type="application/json")


def AddTable(request):
    """
    add table to database.

    This function adds datasets to the tables 'Table', 'RightList', 'RelRightListDataDescr', 'DataDescr', 'Datatype'
    and corresponding datatype tables (e.g. 'NumericType').
    If the datatype is 'SelectionType', the selection options are also added to the table 'SelectionValue'

    {
        "name": "example",
        "admin": [4, 23, 10003],  //group ids have an offset of say 10000, to distinguish from user ids
        "dataDescr": [
            {"name": "columname", "required": 1, "type": 1,
                "options": {"0": "yes", "1": "no", "2": "maybe"},
                "rights": { "8": ["read"], "17": ["modify", "read"], "1001": ["modify", "delete", "read"]}
            },
            {"name": "anothercolum", "required": 0, "type": 1,
                "options": {"0": "yes", "1": "no", "2": "maybe"},
                "rights": { "8": ["read"], "17": ["modify", "read"], "1001": ["modify", "delete", "read"]}
            }
        ],
        "rights": {"1": ["rightAdmin", "viewLog"], "1001": ["rightsAdmin", "insert"], "2": ["insert"]}
    }
    """
    if request.method == "POST":
        # add to table 'Table'
        tableData = dict()
        tableData["name"] = HttpRequest.POST["name"]
        tableData["creator"] = request.user
        tableData["created"] = datetime.now()

        tableF = TableForm(tableData)
        if tableF.is_valid():
            newTable = tableF.save()
            newTable.save()

        # add to table 'Datadescr'
        for col in request["dataDescrs"]:
            dataDescr = dict()
            dataDescr["name"] = col["name"]
            dataDescr["type"] = col["type"]
            dataDescr["required"] = col["required"]
            dataDescrF = DataDescrForm(dataDescr)
            if dataDescrF.is_valid():
                newDataDescr = dataDescrF.save()
                newDataDescr.creator = request.user
                newDataDescr.created = datetime.now()
                newDataDescr.table = Table.objects.get(request["name"])
                newDataDescr.save()
            # add to table datatype
            newDatatype = DatatypeForm({col["name"], })
            if newDatatype.is_valid():
                newDatatype.save()
            # add to corresponding datatype table
            type = dict()
            if col["type"] == Datatype.TEXT:
                type["length"] = col["length"]
                textTypeF = TextTypeForm(type)
                if textTypeF.is_valid():
                    newText = textTypeF.save()
                    newText.datatype = newDatatype
                    newText.save()

            elif col["type"] == Datatype.NUMERIC or col["type"] == Datatype.DATE:
                type["min"] = col["min"]
                type["max"] = col["max"]
                numericTypeF = NumericTypeForm(type)
                if numericTypeF.is_valid():
                    newNumeric = numericTypeF.save()
                    newNumeric.datatype = newDatatype
                    newNumeric.save()

            elif col["type"] == Datatype.TABLE:
                newTableType = TableType()
                newTableType.table = newTable
                newTableType.datatype = newDatatype
                newTableType.save()

            elif col["type"] == Datatype.SELECTION:
                selTypeF = SelectionTypeForm({"count": len(col["options"]), })
                if selTypeF.is_valid():
                    selType = selTypeF.save()
                    selType.datatype = newDatatype
                    selType.save()

                for key, val in col["options"]:
                    selValF = SelectionValueForm({key, val})
                    if selValF.is_valid():
                        selVal = selValF.save()
                        selVal.selectionType = selType

        # add to Rightlist and RelRightListDataDescr
        for newID, rights in request["rights"]:
            user = DBUser.objects.get(id=newID)
            if user.rightList_id is None:  # User does not have a list of rights yet
                rightList = dict()
                rightList["viewLog"] = 1 if "viewLog" in rights else 0
                rightList["rightsAdmin"] = 1 if "rightsAdmin" in rights else 0
                rightList["insert"] = 1 if "insert" in rights else 0
                rightListF = RightListForm(rightList)
                if rightListF.is_valid():
                    newRightList = rightListF.save()
                    newRightList.table = newTable
                    newRightList.user = user
                    user.rightList = newRightList

        return HttpResponse(status=200)