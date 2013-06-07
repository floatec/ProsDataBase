__author__ = 'tieni'

import json
import sys
from django.http import HttpResponse

from models import *
from forms import *


def createTable(request):
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
    jsonRequest = json.loads(request.raw_post_data)
    # add to table 'Table'
    table = dict()
    table["name"] = jsonRequest["name"]
    table["created"] = datetime.now()

    tableF = TableForm(table)
    if tableF.is_valid():
        newTable = tableF.save(commit=False)
        newTable.creator = request.user
        newTable.category = Category.objects.get(name=jsonRequest["category"])
        newTable.save()
    else:
        return HttpResponse("Could not create table.")

    # add to table 'RightlistForTable' for user
    answer = createTableRights(jsonRequest["rights"], newTable)
    if answer != 'OK':
        return HttpResponse(content=answer, status=400)

    for col in jsonRequest["columns"]:
        # add to table 'Datatype'
        answer = createColumn(col, newTable, request.user)
        if answer != 'OK':
            return HttpResponse(content=answer, status=400)

    return HttpResponse(status=200)


def createColumn(col, table, user):
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
                return "Could not create text type"

        elif col["type"] == Type.NUMERIC:
            type["min"] = col["min"] if "min" in col else -sys.maxint
            type["max"] = col["max"] if "max" in col else sys.maxint

            typeNumericF = TypeNumericForm(type)
            if typeNumericF.is_valid():
                newNumeric = typeNumericF.save(commit=False)
                newNumeric.type = newDatatype
                newNumeric.save()
            else:
                return "Could not create numeric type"

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
                    return "Could not create date type"
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
                return "Could not create selection type"

            for option in col["options"]:
                selValF = SelectionValueForm({"index": option["key"], "content": option["value"]})
                if selValF.is_valid():
                    selVal = selValF.save(commit=False)
                    selVal.typeSelection = typeSel
                    selVal.save()
                else:
                    return "Could not create selection values"

        elif col["type"] == Type.BOOL:
            typeBool = TypeBool()
            typeBool.type = newDatatype
            typeBool.save()

        elif col["type"] == Type.TABLE:
            newTypeTable = TypeTable()
            refTable = Table.objects.get(name=col["table"])
            newTypeTable.table = refTable
            newTypeTable.column = Column.objects.get(name=col["column"], table=refTable) if "column" in col else None
            newTypeTable.type = newDatatype
            newTypeTable.save()

        # add to table 'Column'
        column = dict()
        column["name"] = col["name"]
        column["created"] = datetime.now()
        columnF = ColumnForm(column)
        if columnF.is_valid():
            newColumn = columnF.save(commit=False)
            newColumn.creator = user
            newColumn.type = newDatatype
            newColumn.table = table
            newColumn.save()
        else:
            return "Could not create new column " + col["name"]
        # new rights
        if "rights" in col:
            answer = createColumnRights(col["rights"], newColumn)
            if answer != 'OK':
                return answer
        return 'OK'


def createTableRights(rights, table):
    # for users
    for item in rights["users"]:
        rightList = dict()
        rightList["viewLog"] = True if "viewLog" in item["rights"] else False
        rightList["rightsAdmin"] = True if "rightsAdmin" in item["rights"] else False
        rightList["insert"] = True if "insert" in item["rights"] else False
        rightList["delete"] = True if "delete" in item["rights"] else False

        if True in rightList.values():
            rightListF = RightListForTableForm(rightList)
            if rightListF.is_valid():
                newRightList = rightListF.save(commit=False)
                newRightList.table = table

                user = DBUser.objects.get(username=item["name"])
                newRightList.user = user
                newRightList.save()

            else:
                return "Could not create user's rightlist for table."

     # for groups
    for item in rights["groups"]:
        rightList = dict()
        rightList["viewLog"] = True if "viewLog" in item["rights"] else False
        rightList["rightsAdmin"] = True if "rightsAdmin" in item["rights"] else False
        rightList["insert"] = True if "insert" in item["rights"] else False
        rightList["delete"] = True if "delete" in item["rights"] else False

        if True in rightList.values():
            rightListF = RightListForTableForm(rightList)
            if rightListF.is_valid():
                newRightList = rightListF.save(commit=False)
                newRightList.table = table

                group = DBGroup.objects.get(name=item["name"])
                newRightList.group = group
                newRightList.save()
            else:
                return "Could not create group's rightlist for table"
    return 'OK'


def createColumnRights(rights, column):
    # for users
    for item in rights["users"]:
        rightList = dict()
        rightList["read"] = 1 if "read" in item["rights"] else 0
        rightList["modify"] = 1 if "modify" in item["rights"] else 0
        if True in rightList.values():
            rightListF = RightListForColumnForm(rightList)
            if rightListF.is_valid():
                newRightList = rightListF.save(commit=False)
                newRightList.column = column
                newRightList.table = column.table

                user = DBUser.objects.get(username=item["name"])
                newRightList.user = user
                newRightList.save()
            else:
                return "could not create column right list for user"
    # for groups
    for item in rights["groups"]:
        rightList = dict()
        rightList["read"] = 1 if "read" in item["rights"] else 0
        rightList["modify"] = 1 if "modify" in item["rights"] else 0
        if True in rightList.values():
            rightListF = RightListForColumnForm(rightList)
            if rightListF.is_valid():
                newRightList = rightListF.save(commit=False)
                newRightList.column = column
                newRightList.table = column.table

                group = DBGroup.objects.get(name=item["name"])
                newRightList.group = group
                newRightList.save()
            else:
                return "Could not create column right list for group"
    return 'OK'


def modifyTable(request, name):
    """
    {
        "name": "tablename",
        "category: "category",
        "columns": [
            {"id": 1, "name": "columname1", "length": 30,
                "rights": {
                    "users" : [{"name": "user1", "rights": ["read"]}, {"name": "user2", "rights": ["modify", "read"]}],
                    "groups": [{"name": "group1", "rights": ["modify", "read"]}]
                }
            },
            {"id": 2, "name": "column2", "min": 0, "max": 150,
                "rights": {
                    "users" : [{"name": "user1", "rights": ["read"]}, {"name": "user2", "rights": ["modify", "read"]}],
                    "groups": [{"name": "group2", "rights": ["modify", "read"]}]
                }
            }
        ],
        "rights": {
            "users": [{"name": "user1", "rights": ["rightsAdmin", "viewLog", "delete"]}, {"name": "user2", "rights": ["insert"]}],
            "groups": [{"name": "group2", "rights": ["rightsAdmin", "insert"]}]
        }
    }
    """
    try:
        table = Table.objects.get(name=name)
    except Table.DoesNotExist:
        return HttpResponse(content="Could not find table with name " + name + ".", status=400)

    jsonRequest = json.loads(request.raw_post_data)
    if jsonRequest["name"] != name:
        try:
            Table.objects.get(name=jsonRequest["name"])
        except Table.DoesNotExist:
            table.name = jsonRequest["name"]

    if jsonRequest["category"] != table.category.name:
        try:
            category = Category.objects.get(name=jsonRequest["category"])
        except Category.DoesNotExist:
            return HttpResponse("Could not find category " + jsonRequest["category"] + ".", status=400)

        table.category = category
        table.save()
        if "rights" in jsonRequest:
            RightListForTable.objects.filter(table=table).delete()
            answer = createTableRights(jsonRequest["rights"], table)
            if answer != 'OK':
                return HttpResponse(content=answer, status=400)

    for col in jsonRequest["columns"]:
        if "id" not in col:  # this should be a newly added column
            answer = createColumn(col, table, request.user)
            if answer != 'OK':
                return HttpResponse(content=answer, status=400)
            continue

        # this column should be modified
        try:
            column = Column.objects.get(pk=col["id"])
        except Column.DoesNotExist:
            HttpResponse(content="Could not find column with id " + col["id"] + ".", status=400)
        if column.name != col["name"]:
            try:
                Column.objects.get(name=col["name"], table=table)
                return HttpResponse(content="Column with name " + col["name"] + " already exists.", status=400)
            except Column.DoesNotExist:
                column.name = col["name"]

        colType = column.type
        if colType.type == Type.TEXT:
            typeText = colType.getType()
            if col["length"] >= typeText.length:
                typeText.length = col["length"]
                typeText.save()
        elif colType.type == Type.NUMERIC:
            typeNum = colType.getType()
            if col["min"] <= typeNum.min:
                typeNum.min = col["min"]
            if typeNum.max <= col["max"]:
                typeNum.max = col["max"]

        elif colType.type == Type.DATE:
            typeDate = colType.getType()
            if "min" in col and col["min"] <= typeDate.min:
                typeDate.min = col["min"]
            if "max" in col and col["max"] >= typeDate.max:
                typeDate.max = col["max"]

        elif colType.type == Type.SELECTION:
            typeSel = colType.getType()
            if len([option["name"] for option in col["options"]]) > len(set([option["name"] for option in col["options"]])):
                return HttpResponse(content="found duplicate selection values.", status=400)
            for option in col["options"]:
                try:
                    value = SelectionValue.objects.get(index=option["key"])
                    value.content = option["value"]
                    value.save()
                except SelectionValue.DoesNotExist:  # this is a new selection value
                    typeSel.count += 1
                    typeSel.save()
                    selValF = SelectionValueForm({"index": option["key"], "content": option["value"]})
                    if selValF.is_valid():
                        selVal = selValF.save()
                        selVal.typeselection = typeSel
                        selVal.save()

        elif colType.type == Type.TABLE:
            typeTable = colType.getType()
            refTable = typeTable.table
            refColumns = refTable.getColumns()
            refColNames = list()
            for refColumn in refColumns:
                refColNames.append(refColumn.name)
            if col["column"] not in refColNames:
                return HttpResponse(content="Column " + col["column"] + " does not exist in referenced table " + col["table"] + ".", status=400)
            try:
                refColumn = Column.objects.get(name=col["column"])
            except Column.DoesNotExist:
                return HttpResponse(content="Column " + col["column"] + " does not exist.", status=400)
            typeTable.column = refColumn
        if "rights" in col:
            RightListForColumn.objects.filter(column=column).delete()
            answer = createColumnRights(col["rights"], column)
            if answer != 'OK':
                return HttpResponse(content=answer, status=400)

    return HttpResponse(content="Successfully modified table", status=200)