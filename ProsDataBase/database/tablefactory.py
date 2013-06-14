__author__ = 'tieni'

import csv
import json
import sys
from django.http import HttpResponse

from models import *
from serializers import TableSerializer
from forms import *
from response import *
from django.utils.translation import ugettext_lazy as _


def modifyCategories(request):
    """
    {
        "categories": [{"old": "name", "new": "newname"}, {"old": "name", "new": "newname"}, {"old": "name", "new": "newname"}]
    }
    """
    request = json.loads(request.raw_post_data)
    errors = list()

    for cat in request["categories"]:
        if "old" in cat:
            try:
                catForChange = Category.objects.get(name=cat["old"])
            except Category.DoesNotExist:
                errors.append({"code": Error.CATEGORY_NOTFOUND, "message": _("Could not find category ") + cat["old"] + "."})

            try:  # check if category with name already exists. Only save new name, if not existent yet
                Category.objects.get(name=cat["new"])
                errors.append({"code": Error.CATEGORY_CREATE, "message": _("Category with name ") + cat["new"] + _(" already exists.")})
            except Category.DoesNotExist:
                catForChange.name = cat["new"]
                catForChange.save()

        else:
            try:  # check if category with name already exists. Only save new name, if not existent yet
                Category.objects.get(name=cat["new"])
                errors.append({"code": Error.CATEGORY_CREATE, "message": _("Category with name ") + cat["new"] + _(" already exists.")})
            except Category.DoesNotExist:
                newCatF = CategoryForm({"name": cat["new"]})
                if newCatF.is_valid():
                    newCat = newCatF.save()
                    newCat.save()

    if len(errors) > 0:
        return HttpResponse(json.dumps({"errors": errors}), content_type="application/json")

    return HttpResponse(json.dumps({"success": _("Saved changes successfully.")}), content_type="application/json")


def deleteCategory(name):
    try:
        category = Category.objects.get(name=name)
        tables = Table.objects.filter(category=category)
        if len(tables) > 0:
            return HttpResponse(json.dumps({"errors": [{"code": Error.CATEGORY_DELETE, "message": _("Please put the tables of this group into another category first.")}]}), content_type="application/json")
        category.delete()
    except Category.DoesNotExist:
        return HttpResponse(json.dumps({"errors": [{"code": Error.CATEGORY_DELETE, "message": _("Category with name ") + name + _(" does not exist.")}]}), content_type="application/json")

    return HttpResponse(json.dumps({"success": _("Deleted category ") + name + "."}), content_type="application/json")


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

    savedObjs = list()  # holds all objects saved so far, so that in case of errors, they can be deleted
    errors = list()

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
        savedObjs.append(newTable)
    else:
        for obj in savedObjs:
            obj.delete()
        return HttpResponse(json.dumps({"errors": [{"code": Error.TABLE_CREATE, "message": _("Failed to create table. Please contact the developers.")}]}))

    # add to table 'RightlistForTable' for user
    answer = createTableRights(jsonRequest["rights"], newTable)
    if not answer:
        for obj in savedObjs:
            obj.delete()
        errors.append(answer)

    for col in jsonRequest["columns"]:
        # add to table 'Datatype'
        answer = createColumn(col, newTable, request.user)
        if not answer:
            for obj in savedObjs:
                obj.delete()
            errors.append(answer)

    if len(errors) > 0:
        return HttpResponse(json.dumps({"errors": errors}), content_type="application/json")
    return HttpResponse(_("Successfully created table ") + table["name"], status=200)


def createColumn(col, table, user):
    savedObjs = list()  # holds all objects saved so far, so that in case of errors, they can be deleted

    # add to table 'Datatype'
    newDatatype = Type(name=col["name"], type=col["type"])
    newDatatype.save()
    savedObjs.append(newDatatype)

    # add to corresponding datatype table
    type = dict()
    if col["type"] == Type.TEXT:
        type["length"] = col["length"]
        typeTextF = TypeTextForm(type)
        if typeTextF.is_valid():
            newText = typeTextF.save(commit=False)
            newText.type = newDatatype
            newText.save()
            savedObjs.append(newText)
        else:
            for obj in savedObjs:
                obj.delete()
            return {"code": Error.TYPE_CREATE, "message": _("Could not create text type for column ")+col["name"] + _(". Abort.")}

    elif col["type"] == Type.NUMERIC:
        type["min"] = col["min"] if "min" in col else -sys.maxint
        type["max"] = col["max"] if "max" in col else sys.maxint

        typeNumericF = TypeNumericForm(type)
        if typeNumericF.is_valid():
            newNumeric = typeNumericF.save(commit=False)
            newNumeric.type = newDatatype
            newNumeric.save()
            savedObjs.append(newNumeric)
        else:
            for obj in savedObjs:
                obj.delete()
            return {"code": Error.TYPE_CREATE, "message": _("Could not create numeric type for column ")+col["name"] + _(". Abort.")}

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
                savedObjs.append(typeDate)
            else:
                for obj in savedObjs:
                    obj.delete()
                return {"code": Error.TYPE_CREATE, "message": _("Could not create date type for column ") + col["name"] + _(". Abort.")}
        else:
            typeDate = TypeDate()
            typeDate.type = newDatatype
            typeDate.save()
            savedObjs.append(typeDate)

    elif col["type"] == Type.SELECTION:
        typeSelF = TypeSelectionForm({"count": len(col["options"]), })
        if typeSelF.is_valid():
            typeSel = typeSelF.save(commit=False)
            typeSel.type = newDatatype
            typeSel.save()
            savedObjs.append(typeSel)
        else:
            for obj in savedObjs:
                obj.delete()
            return {"code": Error.TYPE_CREATE, "message": _("Could not create selection type for column ") + col["name"] + _(". Abort.")}
            count = 0
        for option in col["options"]:
            selValF = SelectionValueForm({"index": count, "content": option["value"]})
            if selValF.is_valid():
                selVal = selValF.save(commit=False)
                selVal.typeSelection = typeSel
                selVal.save()
                savedObjs.append(selVal)
                count += 1
            else:
                for obj in savedObjs:
                    obj.delete()
                return {"code": Error.TYPE_CREATE, "message": _("Could not create selection value for column ") + col["name"] + _(". Abort.")}

    elif col["type"] == Type.BOOL:
        typeBool = TypeBool()
        typeBool.type = newDatatype
        typeBool.save()
        savedObjs.append(typeBool)

    elif col["type"] == Type.TABLE:
        newTypeTable = TypeTable()
        refTable = Table.objects.get(name=col["table"])
        newTypeTable.table = refTable
        newTypeTable.column = Column.objects.get(name=col["column"], table=refTable) if "column" in col else None
        newTypeTable.type = newDatatype
        newTypeTable.save()
        savedObjs.append(newTypeTable)

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
        savedObjs.append(newColumn)
    else:
        for obj in savedObjs:
            obj.delete()
        return {"code": Error.COLUMN_CREATE, "message": _("Could not create column ") + col["name"] + _(". Abort.")}
    # new rights
    if "rights" in col:
        answer = createColumnRights(col["rights"], newColumn)
        if not answer:
            for obj in savedObjs:
                obj.delete()
            return {"code": Error.TYPE_CREATE, "message": _("Could not create column rights for column ") + col["name"] + _(". Abort.")}

    return True


def deleteTable(name, user):
    """
    Set the delete flag for this table and all its columns and datasets.
    Renames the table to: tablename_DELETED_currentdatetime, so that a new table with this name can be created.
    """
    try:
        table = Table.objects.get(name=name)
    except Table.DoesNotExist:
        HttpResponse(json.dumps({"errors": [{"code": Error.TABLE_NOTFOUND, "message": _("Could not find table with name " + name + ".")}]}))

    if table.deleted:
        HttpResponse(json.dumps({"errors": [{"code": Error.TABLE_NOTFOUND, "message": _("Could not find table with name " + name + ".")}]}))

    errors = list()
    # Only delete this table if it is not referenced by any other table.
    typeTables = TypeTable.objects.filter(table=table)
    if len(typeTables) > 0:  # there are references.
        # Get names of tables referencing this table for error display
        tableNames = set()
        for typeTable in typeTables:
            column = Column.objects.get(type=typeTable.type)
            tableNames.add(column.table.name)

        errors.append({"error": _("Please delete references to this table in tables ") + str(tableNames) + _(" first.")})

    else:  # no reference exists, so delete the table
        datasets = list()
        for dataset in table.datasets.all():
            datasets.append(dataset)
            answer = deleteDataset(dataset.datasetID, user)
            if not answer:
                errors.append(answer)

        columns = list()
        for column in table.columns.all():
            answer = deleteColumn(table.name, column.name, user)
            if not answer:
                errors.append(answer)

        table.deleted = True
        table.modified = datetime.now()
        table.modifier = user
        table.name = table.name + "_DELETED_" + str(datetime.now())
        table.save()

        # the foreign keys to this table must be updated, since the table was renamed
        for col in columns:
            col.table = table
            col.save()

        for dataset in datasets:
            dataset.table = table
            dataset.save()

        if len(errors) > 0:
            return HttpResponse({"errors": errors}, content_type="application/json")
        return HttpResponse(json.dumps({"success": _("Successfully deleted table ") + table.name + "."}), status=200)


def deleteColumn(tableName, columnName, user):
    """
    Set the delete flag for this column and all its data fields.
    Renames the column to: columnname_DELETED_currentdatetime, so that a new column with this name can be created.
    """
    try:
        table = Table.objects.get(name=tableName)
    except Table.DoesNotExist:
        return {"code": Error.TABLE_NOTFOUND, "message": _("Could not find table with name " + tableName + ".")}
    try:
        column = table.getColumns().get(name=columnName)
    except Column.DoesNotExist:
        return {"code": Error.COLUMN_NOTFOUND, "message": _("Could not find column with name ") + columnName + _(" in table " )+ tableName + "."}

    #  find all data fields related to this column to set their delete flag
    if column.type.type == Type.TEXT:
        data = DataText.objects.filter(column=column)
    elif column.type.type == Type.NUMERIC:
        data = DataNumeric.objects.filter(column=column)
    elif column.type.type == Type.DATE:
        data = DataDate.objects.filter(column=column)
    elif column.type.type == Type.SELECTION:
        data = DataSelection.objects.filter(column=column)
    elif column.type.type == Type.BOOL:
        data = DataBool.objects.filter(column=column)
    elif column.type.type == Type.TABLE:
        data = DataTable.objects.filter(column=column)

    items = list()
    for item in data:
        items.append(item)
        item.deleted = True
        item.modified = datetime.now()
        item.modifier = user
        item.save()

    column.name = column.name + "_DELETED_" + str(datetime.now())
    column.deleted = True
    column.modified = datetime.now()
    column.modifier = user
    column.save()

    # the foreign keys must be updated, since the column was renamed
    for item in items:
        item.column = column
        item.save()

    return True


def deleteDatasets(request, tableName):
    try:
        Table.objects.get(name=tableName)
    except Table.DoesNotExist:
        return HttpResponse(json.dumps({"errors": [{"code": Error.TABLE_NOTFOUND, "message": _("Could not find table ") + tableName + _(" to delete from.")}]}), content_type="application/json")

    jsonRequest = json.loads(request.raw_post_data)

    errors = list()
    for id in jsonRequest:
        answer = deleteDataset(id, request.user)
        print answer
        if not answer:
            errors.append(answer)

    if len(errors) > 0:
        return HttpResponse(json.dumps({"errors": errors}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({"success": _("Successfully deleted all datasets.")}), content_type="application/json")


def deleteDataset(datasetID, user):
    """
    Set the delete flag for this dataset. Returns an error if it is referenced by other tables.

    It is not necessary to set the delete flag of containing data fields, as the whole dataset is not serialized
    anyway if its delete flag is set.
    """
    try:
        dataset = Dataset.objects.get(datasetID=datasetID)
        if dataset.deleted:
            return {"code": Error.DATASET_NOTFOUND, "message": _("Could not find dataset with id ") + dataset.datasetID + "."}
    except Dataset.DoesNotExist:
            return {"code": Error.DATASET_NOTFOUND, "message": _("Could not find dataset with id ")+ dataset.datasetID + "."}

    # only delete if dataset is not referenced by another table
    links = TableLink.objects.filter(dataset=dataset)
    if len(links) > 0:  # this dataset is used by another table.
        # get names of tables which reference this dataset for error display
        dataTableIDs = list()
        for link in links:
            dataTableIDs.append(link.dataTable_id)
        dataTables = DataTable.objects.filter(pk__in=dataTableIDs)
        datasetIDs = list()
        for dataTable in dataTables:
            datasetIDs.append(dataTable.dataset.datasetID)
        datasets = Dataset.objects.filter(datasetID__in=datasetIDs)
        tables = set()
        for dataset in datasets:
            tables.add(dataset.table.name)

            return {"code": Error.DATASET_REF, "message": _("Could not delete dataset with id ") + dataset.datasetID + _(". Please delete references to it in following tables first: ") + str(tables) + "."}

    # no references in other tables, so delete this dataset
    dataset.deleted = True
    dataset.modified = datetime.now()
    dataset.modifier = user
    dataset.save()
    return True


def createTableRights(rights, table):
    # for users
    savedObjects = list()
    for item in rights["users"]:
        rightList = dict()
        rightList["viewLog"] = True if "viewLog" in item["rights"] else False
        rightList["rightsAdmin"] = True if "rightsAdmin" in item["rights"] else False
        rightList["insert"] = True if "insert" in item["rights"] else False
        rightList["delete"] = True if "delete" in item["rights"] else False

        if True in rightList.values():
            rightListF = RightListForTableForm(rightList)
            if rightListF.is_valid():
                newUserRights = rightListF.save(commit=False)
                newUserRights.table = table
                newUserRights.user = DBUser.objects.get(username=item["name"])
                newUserRights.save()
                savedObjects.append(newUserRights)
            else:
                for obj in savedObjects:
                    obj.delete()
                return {"code": Error.RIGHTS_TABLE_CREATE, "message": _("Failed to create table rights.")}

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
                newGroupRights = rightListF.save(commit=False)
                newGroupRights.table = table
                newGroupRights.group = DBGroup.objects.get(name=item["name"])
                newGroupRights.save()
                savedObjects.append(newGroupRights)
            else:
                for obj in savedObjects:
                    obj.delete()
                return {"code": Error.RIGHTS_TABLE_CREATE, "message": _("Could not create table rights.")}
    return True


def createColumnRights(rights, column):
    savedObjs = list()

    # for users
    for item in rights["users"]:
        rightList = dict()
        rightList["read"] = True if "read" in item["rights"] else False
        rightList["modify"] = True if "modify" in item["rights"] else False
        if True in rightList.values():
            rightListF = RightListForColumnForm(rightList)
            if rightListF.is_valid():
                newRightList = rightListF.save(commit=False)
                newRightList.column = column
                newRightList.table = column.table

                user = DBUser.objects.get(username=item["name"])
                newRightList.user = user
                newRightList.save()
                savedObjs.append(newRightList)
            else:
                for obj in savedObjs:
                    obj.delete()
                return {"code": Error.RIGHTS_COLUMN_CREATE, "message": _("Failed to create column rights.")}
    # for groups
    for item in rights["groups"]:
        rightList = dict()
        rightList["read"] = True if "read" in item["rights"] else False
        rightList["modify"] = True if "modify" in item["rights"] else False
        if True in rightList.values():
            rightListF = RightListForColumnForm(rightList)
            if rightListF.is_valid():
                newRightList = rightListF.save(commit=False)
                newRightList.column = column
                newRightList.table = column.table

                group = DBGroup.objects.get(name=item["name"])
                newRightList.group = group
                newRightList.save()
                savedObjs.append(newRightList)
            else:
                for obj in savedObjs:
                    obj.delete()
                return {"code": Error.RIGHTS_COLUMN_CREATE, "message": _("Failed to create column rights.")}
    return True


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
        return HttpResponse(json.dumps({"errors": [{"code": Error.TABLE_NOTFOUND, "message": _("Could not find table ")+ name + _(" to delete from.")}]}), content_type="application/json")

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
            return HttpResponse(json.dumps({"errors": [{"code": Error.CATEGORY_NOTFOUND, "message": _("Could not find category ") + jsonRequest["category"] + "."}]}), content_type="application/json")

        table.category = category
        table.save()

    if "rights" in jsonRequest:
        RightListForTable.objects.filter(table=table).delete()
        answer = createTableRights(jsonRequest["rights"], table)
        if not answer:
            return HttpResponse(json.dumps({"errors": [answer]}), content_type="application/json")

    for col in jsonRequest["columns"]:
        if "id" not in col:  # this should be a newly added column
            answer = createColumn(col, table, request.user)
            if not answer:
                return HttpResponse(json.dumps({"errors": [answer]}), content_type="application/json")
            continue

        # this column should be modified
        try:
            column = Column.objects.get(pk=col["id"])
        except Column.DoesNotExist:
            HttpResponse(json.dumps({"errors": [{"code": Error.COLUMN_NOTFOUND, "message": _("Could not find column.")}]}), content_type="application/json")
        if column.name != col["name"]:
            try:
                Column.objects.get(name=col["name"], table=table)
                return HttpResponse(json.dumps({"errors": [{"code": Error.COLUMN_CREATE, "message": _("Column with name ")+ col["name"] + _(" already exists.")}]}), content_type="application/json")
            except Column.DoesNotExist:
                column.name = col["name"]
                column.save()

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
            typeNum.save()

        elif colType.type == Type.DATE:
            typeDate = colType.getType()
            if "min" in col and col["min"] <= typeDate.min:
                typeDate.min = col["min"]
            if "max" in col and col["max"] >= typeDate.max:
                typeDate.max = col["max"]
            typeDate.save()

        elif colType.type == Type.SELECTION:
            typeSel = colType.getType()
            if len([option["value"] for option in col["options"]]) > len(set([option["value"] for option in col["options"]])):
                return HttpResponse(json.dumps({"errors": [{"code": Error.TYPE_CREATE, "message": _("found duplicate selection values.")}]}), content_type="application/json")
            for option in col["options"]:
                if "key" in option:
                    value = SelectionValue.objects.get(index=option["key"], typeSelection=typeSel)
                    value.content = option["value"]
                    value.save()
                    # change this selection value for all existing datasets.
                    for datasel in DataSelection.objects.filter(dataset__in=table.getDatasets(), column=column):
                        if datasel.key == option["key"]:
                            datasel.content = option["value"]
                else:  # this is a new selection value
                    typeSel.count += 1
                    typeSel.save()
                    selValF = SelectionValueForm({"index": typeSel.count, "content": option["value"]})
                    if selValF.is_valid():
                        selVal = selValF.save(commit=False)
                        selVal.typeSelection = typeSel
                        selVal.save()

        elif colType.type == Type.TABLE:
            typeTable = colType.getType()
            refTable = typeTable.table
            if "column" in col:
                refColumns = refTable.getColumns()
                refColNames = list()
                for refColumn in refColumns:
                    refColNames.append(refColumn.name)
                if col["column"] not in refColNames:
                    return HttpResponse(json.dumps({"errors": [{"code": Error.COLUMN_REF, "message": _("Column ")+ col["column"] + _(" does not exist in referenced table ") + col["table"] + "."}]}), content_type="application/json")
                try:
                    refColumn = Column.objects.get(name=col["column"])
                except Column.DoesNotExist:
                    return HttpResponse(json.dumps({"errors": [{"code": Error.COLUMN_NOTFOUND, "message": _("Column ")+ col["column"] + _(" does not exist.")}]}), content_type="application/json")
                typeTable.column = refColumn
            else:
                typeTable.column = None
                typeTable.save()
        if "rights" in col:
            RightListForColumn.objects.filter(column=column).delete()
            answer = createColumnRights(col["rights"], column)
            if not answer:
                return HttpResponse(json.dumps({"errors": [answer]}), content_type="application/json")

    result = TableSerializer.serializeStructure(name, request.user)
    return HttpResponse(json.dumps(result), content_type="application/json")


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
    jsonRequest = json.loads(request.raw_post_data)
    try:
        theTable = Table.objects.get(name=tableName)
    except Table.DoesNotExist:
        return HttpResponse(json.dumps({"errors": [{"code": Error.TABLE_CREATE, "message": _("Failed to create table. Please contact the developers.")}]}))

    savedObjs = list()

    datasetF = DatasetForm({"created": datetime.now()})
    if not datasetF.is_valid():
        return HttpResponse(json.dumps({"errors": [{"code": Error.DATASET_CREATE, "message": _("Error creating a new dataset.")}]}), content_type="application/json")

    newDataset = datasetF.save(commit=False)
    newDataset.table = theTable
    newDataset.creator = request.user
    newDataset.save()
    newDataset.datasetID = theTable.generateDatasetID(newDataset)
    newDataset.save()
    savedObjs.append(newDataset)

    for col in jsonRequest["columns"]:
        if "value" not in col:
            continue
        try:
            column = Column.objects.get(name=col["name"], table=theTable)
        except Column.DoesNotExist:
            for obj in savedObjs:
                obj.delete()
            HttpResponse(json.dumps({"errors": [{"code": Error.COLUMN_NOTFOUND, "message": _("Could not find a column with name ") + col["name"] + _("in table ") + tableName + _(". Abort.")}]}), content_type="application/json")
            continue
        if not column.type.getType().isValid(col["value"]):
            for obj in savedObjs:
                obj.delete()
            return HttpResponse(json.dumps({"errors": [{"code": Error.TYPE_INVALID, "message": _("input ") + unicode(col["value"]) + _(" for column ") + column.name + _(" is not valid. Abort.")}]}), content_type="application/json")

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
            selVal = SelectionValue.objects.get(type=column.type.getType(), content=col["value"])
            selF = DataSelectionForm({"created": datetime.now(), "content": col["value"], "key": selVal.index})
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
            for obj in savedObjs:
                obj.delete()
            return HttpResponse(json.dumps({"errors": [{"code": Error.DATAFIELD_CREATE, "message": _("Could not add data for column") + col["name"] + _(". The content type was not valid. Abort.")}]}), content_type="application/json")

        else:
            newData.creator = request.user
            newData.column = column
            newData.dataset = newDataset
            newData.save()
            savedObjs.append(newData)

        if column.type.type == Type.TABLE and newData is not None:
            for index in col["value"]:  # find all datasets for this
                try:
                    dataset = Dataset.objects.get(datasetID=index)
                except Dataset.DoesNotExist:
                    return HttpResponse(json.dumps({"errors": [{"code": Error.DATASET_NOTFOUND, "message": _("dataset with id ") + index + _(" could not be found in table ") + column.type.getType().table.name + _(". Abort.")}]}), content_type="application/json")
                else:
                    link = TableLink()
                    link.dataTable = newData
                    link.dataset = dataset
                    link.save()
                    savedObjs.append(link)

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
    jsonRequest = json.loads(request.raw_post_data)
    try:
        theTable = Table.objects.get(name=tableName)
    except Table.DoesNotExist:
        return HttpResponse(json.dumps({"errors": [{"code": Error.TABLE_CREATE, "message": _("Failed to create table. Please contact the developers.")}]}))
    try:
        dataset = Dataset.objects.get(datasetID=datasetID)
    except Dataset.DoesNotExist:
        return HttpResponse(json.dumps({"errors": [{"code": Error.DATASET_NOTFOUND, "message": _("Could not find dataset with id ") + datasetID + _(" in table ") + tableName + "."}]}), content_type="application/json")

    dataCreatedNewly = False  # is set to True if a data element was not modified but created newly
    newData = None
    for col in jsonRequest["columns"]:
        try:
            column = Column.objects.get(name=col["name"], table=theTable)
        except Column.DoesNotExist:
            HttpResponse(json.dumps({"errors": [{"code": Error.COLUMN_NOTFOUND, "message": _("Could not find column with name ") + col["name"] + "."}]}), content_type="application/json")
            continue

        if not column.type.getType().isValid(col["value"]):
            return HttpResponse(json.dumps({"errors": [{"code": Error.TYPE_INVALID, "message": _("input ") + unicode(col["value"]) + _(" for column ") + column.name + _(" is not valid.")}]}), content_type="application/json")

        if column.type.type == Type.TEXT:
            try:
                text = dataset.datatext.get(column=column)
                text.modified = datetime.now()
                text.modifier = request.user
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
                num.modifier = request.user
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
                date.modifier = request.user
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
                sel.modifier = request.user
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
                bool.modifier = request.user
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
                links = TableLink.objects.filter(dataTable=dataTbl)
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
                        newLink = TableLink()
                        newLink.dataTable = dataTbl
                        newLink.dataset = newDataset
                        newLink.save()
                    except Dataset.DoesNotExist:
                        return HttpResponse(json.dumps({"errors": [{"code": Error.DATASET_NOTFOUND, "message": _("Could not find dataset with id ") + id + "."}]}), content_type="application/json")

            except DataTable.DoesNotExist:
                dataCreatedNewly = True
                dataTblF = DataTableForm({"created": datetime.now()})
                if dataTblF.is_valid():
                    newData = dataTblF.save(commit=False)

        if dataCreatedNewly:
            if newData is None:
                return HttpResponse(json.dumps({"errors": [{"code": Error.TYPE_NOTYPE, "message": _("Could not add data to column ") + col["name"] + _(". The content type was invalid.")}]}), content_type="application/json")

            else:
                newData.creator = request.user
                newData.column = column
                newData.dataset = Dataset.objects.get(datasetID=datasetID)
                newData.save()

            # this must be performed at the end, because TableLink receives newData, which has to be saved first
            if column.type.type == Type.TABLE and newData is not None:
                for index in col["value"]:  # find all datasets for this
                    try:
                        dataset = Dataset.objects.get(pk=index)
                        link = TableLink()
                        link.dataTable = newData
                        link.dataset = dataset
                        link.save()
                    except Dataset.DoesNotExist:
                        return HttpResponse(json.dumps({"errors": [{"code": Error.DATASET_NOTFOUND, "message": _("Could not find dataset with id ") + index + "."}]}), content_type="application/json")

    return HttpResponse(json.dumps({"id": dataset.datasetID}), status=200)


def exportTable(request, tableName):
    try:
        table = Table.objects.get(name=tableName)
    except Table.DoesNotExist:
        return HttpResponse(content=_("Could not find table with name ") + tableName + ".", status=400)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename='" + table.name + "_" + str(datetime.now()) + ".csv'"

    writer = csv.writer(response)
    writer.writerow([table.name + " from " + str(datetime.now())])
    writer.writerow(["system ID"] + request["columns"])

    for datasetID in request["datasets"]:
        try:
            dataset = Dataset.objects.get(datasetID=datasetID)
        except Dataset.DoesNotExist:
            return HttpResponse(content="Could not find dataset with ID " + datasetID + ".", status=400)
        row = list()
        row.append(datasetID)
        for colName in request["columns"]:
            try:
                column = Column.objects.get(name=colName, table=table)
            except Column.DoesNotExist:
                return HttpResponse(content=_("Could not find column with name ")+ colName + _(" in table ") + tableName + ".", status=400)
            if column.type.type == Type.TEXT:
                text = dataset.datatext.all().get(column=column)
                row.append(text.content)
            elif column.type.type == Type.NUMERIC:
                num = dataset.datanumeric.all().get(column=column)
                row.append(num.content)
            elif column.type.type == Type.DATE:
                date = dataset.datadate.all().get(column=column)
                row.append(date.content)
            elif column.type.type == Type.SELECTION:
                selection = dataset.dataselection.all().get(column=column)
                row.append(selection.content)
            elif column.type.type == Type.BOOL:
                bool = dataset.databool.all().get(column=column)
                row.append(bool.content)
            #elif column.type.type == Type.TABLE:
            #    dataTable = dataset.datatext.all().get(column=column)
            #    row.append(data)
        writer.writerow(row)

    return response
