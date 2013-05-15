# Create your views here.

from django.http import HttpResponse, HttpRequest

from serializers import *
from forms import *
from datetime import datetime


def showAllTables(request):
    if request.method == 'GET':
        tables = TableSerializer.serializeAll()
        return HttpResponse(tables, content_type="application/json")


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
            {"name": "columname", "type": 1, "options": ["0": "yes", "1": "no", "2": "maybe"]},
            {"name": "anothercolum", "type": 1, "options": ["0": "yes", "1": "no", "2": "maybe"]}
        ],
        "rights": [
            {"name":"columname", "read": [17, 8, 10001], "write": [22], "modify": [], "delete": []}
        ]
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
            table = tableF.save()
            table.save()

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

            newDatatype = DatatypeForm({col["name"], })
            if newDatatype.is_valid():
                newDatatype.save()

            type = dict()
            type["name"] = col["name"]
            if col["type"] == Datatype.TEXT:
                type["length"] = col["length"]

            elif col["type"] == Datatype.NUMERIC or col["type"] == Datatype.DATE:
                type["min"] = col["min"]
                type["max"] = col["max"]

            elif col["type"] == Datatype.SELECTION:
                selTypeF = SelectionTypeForm({"count": len(col["options"]), })
                if selTypeF.is_valid():
                    selVal = selValF.save()
                    selVal.datatype = Datatype.objects.get(name=col["name"])
                    selVal.save()

                for val in col["options"]:
                    selValF = SelectionValueForm({val, })
                    if selValF.is_valid():
                        selVal = selValF.save()
                        selVal.selectionType

            elif col["type"] == Datatype.TABLE:
                type.table = Table.objects.get(name=col["name"])

        # TODO: rights

        return HttpResponse(status=200)

