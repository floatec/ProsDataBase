__author__ = 'tieni'

import csv
import json
import sys
from django.http import HttpResponse

from models import *
from forms import *
import historyfactory
from response import *
from django.utils.translation import ugettext_lazy as _


def modifyCategories(request):
    """
    {
        "categories": [{"old": "name", "new": "newname"}, {"old": "name", "new": "newname"}, {"old": "name", "new": "newname"}]
    }
    """
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

    return HttpResponse(json.dumps({"success": _("Saved changes successfully.").__unicode__()}), content_type="application/json")


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


def createTable(request, user):
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

    savedObjs = list()  # holds all objects saved so far, so that in case of errors, they can be deleted
    errors = list()

    # check if table already exists:
    existingTables = Table.objects.filter(name=request["name"])
    for existingTable in existingTables.all():
        if not existingTable.deleted:
            return HttpResponse(json.dumps({"errors": [{"code": Error.TABLE_CREATE, "message": _("A table with name ").__unicode__() + request["name"] + _(" already exists.").__unicode__()}]}))
    # create new table
    table = dict()
    table["name"] = request["name"]
    table["created"] = datetime.now()
    tableF = TableForm(table)
    if tableF.is_valid():
        newTable = tableF.save(commit=False)
        newTable.creator = user
        newTable.category = Category.objects.get(name=request["category"])
        newTable.save()
        savedObjs.append(newTable)
    else:
        for obj in savedObjs:
            obj.delete()
        return HttpResponse(json.dumps({"errors": [{"code": Error.TABLE_CREATE, "message": _("Failed to create table. Please contact the developers.").__unicode__()}]}))

    # add table access rights for users and groups
    answer = createTableRights(request["rights"], newTable, user)
    if not answer:
        for obj in savedObjs:
            obj.delete()
        errors.append(answer)

    columnNames = list()
    for col in request["columns"]:
        # add to table 'Datatype'
        answer = createColumn(col, newTable, user)
        if not answer:
            for obj in savedObjs:
                obj.delete()
            errors.append(answer)
        columnNames.append(col["name"])

    #  finally give the creator of this table all rights on it
    tableRightsF = RightListForTableForm({'viewLog': True, 'rightsAdmin': True, 'insert': True, 'delete': True})
    if tableRightsF.is_valid():
        tableRights = tableRightsF.save(commit=False)
        tableRights.user = user
        tableRights.table = newTable
        tableRights.save()
        savedObjs.append(tableRights)
    else:
        for obj in savedObjs:
            obj.delete()
        errors.append({"code": Error.RIGHTS_TABLE_CREATE, "message": _("Failed to give access rights to the table creator. Please contact the developers.").__unicode__()})
    for col in newTable.getColumns():
        colRightsF = RightListForColumnForm({'read': True, 'modify': True})
        if colRightsF.is_valid():
            colRights = colRightsF.save(commit=False)
            colRights.user = user
            colRights.column = col
            colRights.table = newTable
            colRights.save()
            savedObjs.append(colRights)
        else:
            for obj in savedObjs:
                obj.delete()
            errors.append({"code": Error.RIGHTS_TABLE_CREATE, "message": _("Failed to give access rights to column ").__unicode__() + col.name + _(" for the table creator. Please contact the developers.").__unicode__()})

    if len(errors) > 0:
        return HttpResponse(json.dumps({"errors": errors}), content_type="application/json")

    # Write column creation to history
    columnString = ""
    for name in columnNames:
        columnString += name + ", "
    columnString = columnString[:-2]  # cut off trailing comma

    history = historyfactory.writeTableHistory(None, newTable, user, HistoryTable.TABLE_CREATED, _("Added columns: ").__unicode__() + columnString)
    # Write table rights to history
    rights = historyfactory.printRightsFor(newTable.name)
    if rights is not None:
        for right in rights:
            historyfactory.writeTableHistory(history, newTable, user, HistoryTable.TABLE_CREATED, _("Added permissions:\n").__unicode__() + right)
    # write table creation to history
    historyfactory.writeTableHistory(history, newTable, user, HistoryTable.TABLE_CREATED, _("Created table ").__unicode__() + newTable.name + ".")
    return HttpResponse(json.dumps({"success":_("Successfully created table ").__unicode__() + table["name"]}), content_type="application/json")


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
            return {"code": Error.TYPE_CREATE, "message": _("Could not create text type for column ").__unicode__() + col["name"] + _(". Abort.")}

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
            return {"code": Error.TYPE_CREATE, "message": _("Could not create numeric type for column ").__unicode__() + col["name"] + _(". Abort.").__unicode__()}

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
                return {"code": Error.TYPE_CREATE, "message": _("Could not create date type for column ").__unicode__() + col["name"] + _(". Abort.").__unicode__()}
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
            return {"code": Error.TYPE_CREATE, "message": _("Could not create selection type for column ").__unicode__() + col["name"] + _(". Abort.").__unicode__()}
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
                return {"code": Error.TYPE_CREATE, "message": _("Could not create selection value for column ").__unicode__() + col["name"] + _(". Abort.").__unicode__()}

    elif col["type"] == Type.BOOL:
        typeBool = TypeBool()
        typeBool.type = newDatatype
        typeBool.save()
        savedObjs.append(typeBool)

    elif col["type"] == Type.TABLE:
        newTypeTable = TypeTable()
        refTable = Table.objects.get(name=col["table"], deleted=False)
        newTypeTable.table = refTable
        newTypeTable.column = Column.objects.get(name=col["column"], table=refTable, deleted=False) if "column" in col else None
        newTypeTable.type = newDatatype
        newTypeTable.save()
        savedObjs.append(newTypeTable)

    # add to table 'Column'
    column = dict()
    column["name"] = col["name"]
    column["created"] = datetime.utcnow().replace(tzinfo=utc)
    column["comment"] = col["comment"]
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
        return {"code": Error.COLUMN_CREATE, "message": _("Could not create column ").__unicode__() + col["name"] + _(". Abort.").__unicode__()}
    # new rights
    if "rights" in col:
        answer = createColumnRights(col["rights"], newColumn, user)
        if not answer:
            for obj in savedObjs:
                obj.delete()
            return {"code": Error.TYPE_CREATE, "message": _("Could not create column rights for column ").__unicode__() + col["name"] + _(". Abort.").__unicode__()}
    return True


def deleteTable(name, user):
    """
    Set the delete flag for this table and all its columns and datasets.
    Renames the table to: tablename_DELETED_currentdatetime, so that a new table with this name can be created.
    """
    try:
        table = Table.objects.get(name=name, deleted=False)
    except Table.DoesNotExist:
        HttpResponse(json.dumps({"errors": [{"code": Error.TABLE_NOTFOUND, "message": _("Could not find table with name ").__unicode__() + name + "."}]}))

    if table.deleted:
        HttpResponse(json.dumps({"errors": [{"code": Error.TABLE_NOTFOUND, "message": _("Could not find table with name ").__unicode__() + name + "."}]}))

    errors = list()
    # Only delete this table if it is not referenced by any other table.
    typeTables = TypeTable.objects.filter(table=table)
    if len(typeTables) > 0:  # there are references.
        # Get names of tables referencing this table for error display
        tableNames = set()
        for typeTable in typeTables:
            column = Column.objects.get(type=typeTable.type)
            tableNames.add(column.table.name)

        errors.append({"error": _("Please delete references to this table in tables ").__unicode__() + str(tableNames) + _(" first.").__unicode__()})

    else:  # no reference exists, so delete the table
        for dataset in table.datasets.all():
            answer = deleteDataset(dataset.datasetID, user)
            if not answer:
                errors.append(answer)

        for column in table.columns.all():
            answer = deleteColumn(table.name, column.name, user)
            if not answer:
                errors.append(answer)

        table.deleted = True
        table.modified = datetime.utcnow().replace(tzinfo=utc)
        table.modifier = user
        table.save()

    if len(errors) > 0:
        return HttpResponse(json.dumps({"errors": errors}), content_type="application/json")
    historyfactory.writeTableHistory(None, table, user, HistoryTable.TABLE_DELETED)
    return HttpResponse(json.dumps({"success": _("Successfully deleted table ").__unicode__() + table.name + "."}), status=200)


def deleteColumn(tableName, columnName, user):
    """
    Set the delete flag for this column and all its data fields.
    Renames the column to: columnname_DELETED_currentdatetime, so that a new column with this name can be created.
    """
    try:
        table = Table.objects.get(name=tableName, deleted=False)
    except Table.DoesNotExist:
        return {"code": Error.TABLE_NOTFOUND, "message": _("Could not find table with name ").__unicode__() + tableName + "."}
    try:
        column = table.getColumns().get(name=columnName, deleted=False)
    except Column.DoesNotExist:
        return {"code": Error.COLUMN_NOTFOUND, "message": _("Could not find column with name ").__unicode__() + columnName + _(" in table ").__unicode__() + tableName + "."}

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

    for item in data:
        item.deleted = True
        item.modified = datetime.utcnow().replace(tzinfo=utc)
        item.modifier = user
        item.save()

    column.deleted = True
    column.modified = datetime.utcnow().replace(tzinfo=utc)
    column.modifier = user
    column.save()

    return True


def deleteDatasets(request, tableName):
    try:
        table = Table.objects.get(name=tableName, deleted=False)
    except Table.DoesNotExist:
        return HttpResponse(json.dumps({"errors": [{"code": Error.TABLE_NOTFOUND, "message": _("Could not find table ").__unicode__() + tableName + _(" to delete from.").__unicode__()}]}), content_type="application/json")

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
        # write to history
        historyfactory.writeTableHistory(None, table, request.user, HistoryTable.DATASET_DELETED)
        return HttpResponse(json.dumps({"success": _("Successfully deleted all datasets.").__unicode__()}), content_type="application/json")


def deleteDataset(datasetID, user):
    """
    Set the delete flag for this dataset. Returns an error if it is referenced by other tables.

    It is not necessary to set the delete flag of containing data fields, as the whole dataset is not serialized
    anyway if its delete flag is set.
    """
    try:
        dataset = Dataset.objects.get(datasetID=datasetID)
        if dataset.deleted:
            return {"code": Error.DATASET_NOTFOUND, "message": _("Could not find dataset with id ").__unicode__() + dataset.datasetID + "."}
    except Dataset.DoesNotExist:
            return {"code": Error.DATASET_NOTFOUND, "message": _("Could not find dataset with id ").__unicode__() + dataset.datasetID + "."}

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

            return {"code": Error.DATASET_REF, "message": _("Could not delete dataset with id ").__unicode__() + dataset.datasetID + _(". Please delete references to it in following tables first: ").__unicode__() + str(tables) + "."}

    # no references in other tables, so delete this dataset
    dataset.deleted = True
    dataset.modified = datetime.utcnow().replace(tzinfo=utc)
    dataset.modifier = user
    dataset.save()
    return True


def createTableRights(rights, table, user):
    # for users
    savedObjects = list()
    for item in rights["users"]:
        if user.username == item["name"]:  # user should not be able to change his own permissions
            continue
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
                return {"code": Error.RIGHTS_TABLE_CREATE, "message": _("Failed to create table rights.").__unicode__()}

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
                return {"code": Error.RIGHTS_TABLE_CREATE, "message": _("Could not create table rights.").__unicode__()}
    return True


def createColumnRights(rights, column, user):
    savedObjs = list()

    # for users
    for item in rights["users"]:
        if user.username == item["name"]:  # user should not be able to change his own rights
            continue
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
                return {"code": Error.RIGHTS_COLUMN_CREATE, "message": _("Failed to create column rights.").__unicode__()}
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
                return {"code": Error.RIGHTS_COLUMN_CREATE, "message": _("Failed to create column rights.").__unicode__()}
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
        table = Table.objects.get(name=name, deleted=False)
    except Table.DoesNotExist:
        return HttpResponse(json.dumps({"errors": [{"code": Error.TABLE_NOTFOUND, "message": _("Could not find table ").__unicode__() + name + _(" to delete from.").__unicode__()}]}), content_type="application/json")

    history = None
    jsonRequest = json.loads(request.raw_post_data)
    if jsonRequest["name"] != name:
        try:
            Table.objects.get(name=jsonRequest["name"], deleted=False)
        except Table.DoesNotExist:
            message = _("Changed name from '").__unicode__() + table.name + _("' to: '").__unicode__() + jsonRequest["name"] + "'."
            history = historyfactory.writeTableHistory(history, table, request.user, HistoryTable.TABLE_MODIFIED, message)
            table.name = jsonRequest["name"]

    if jsonRequest["category"] != table.category.name:
        try:
            category = Category.objects.get(name=jsonRequest["category"])
        except Category.DoesNotExist:
            return HttpResponse(json.dumps({"errors": [{"code": Error.CATEGORY_NOTFOUND, "message": _("Could not find category ").__unicode__() + jsonRequest["category"] + "."}]}), content_type="application/json")
        message = _("Changed category from '").__unicode__() + table.category.name + _("' to '").__unicode__() + category.name + "'."
        history = historyfactory.writeTableHistory(history, table, request.user, HistoryTable.TABLE_MODIFIED, message)
        table.category = category
    table.save()

    for col in jsonRequest["columns"]:
        if "id" not in col:  # this should be a newly added column
            answer = createColumn(col, table, request.user)
            if not answer:
                return HttpResponse(json.dumps({"errors": [answer]}), content_type="application/json")

            # give the creator of this column rights on it:
            colRightsF = RightListForColumnForm({"read": True, "modify": True})
            if colRightsF.is_valid():
                colRights = colRightsF.save(commit=False)
                colRights.user = request.user
                colRights.column = table.getColumns().get(name=col["name"], deleted=False)
                colRights.table = table
                colRights.save()
            message = _("New column: '").__unicode__() + col["name"] + "'"
            history = historyfactory.writeTableHistory(history, table, request.user, HistoryTable.TABLE_MODIFIED, message)
            continue

        # this column should be modified
        try:
            column = Column.objects.get(pk=col["id"])
        except Column.DoesNotExist:
            HttpResponse(json.dumps({"errors": [{"code": Error.COLUMN_NOTFOUND, "message": _("Could not find column.").__unicode__()}]}), content_type="application/json")
        if column.name != col["name"]:
            try:
                Column.objects.get(name=col["name"], table=table, deleted=False)
                return HttpResponse(json.dumps({"errors": [{"code": Error.COLUMN_CREATE, "message": _("Column with name ").__unicode__() + col["name"] + _(" already exists.").__unicode__()}]}), content_type="application/json")
            except Column.DoesNotExist:
                message = _("Changed column '").__unicode__() + column.name + _("' to '").__unicode__() + col["name"] + "'"
                history = historyfactory.writeTableHistory(history, table, request.user, HistoryTable.TABLE_MODIFIED, message)
                column.name = col["name"]

        if column.comment != col["comment"]:
            message = column.name + _(": old comment : '").__unicode__() + column.comment + _("', new comment: '").__unicode__() + col["comment"] + "."
            history = historyfactory.writeTableHistory(history, table, request.user, HistoryTable.TABLE_MODIFIED, message)
            column.comment = col["comment"]
        column.save()

        colType = column.type
        if colType.type == Type.TEXT:
            typeText = colType.getType()
            if col["length"] >= typeText.length:
                if col["length"] > typeText.length:
                    message = _("Column '").__unicode__() + column.name + _("': old length: ").__unicode__() + unicode(typeText.length) + _(", new length: ").__unicode__() + unicode(col["length"]) + "."
                    history = historyfactory.writeTableHistory(history, table, request.user, HistoryTable.TABLE_MODIFIED, message)
                typeText.length = col["length"]
                typeText.save()

        elif colType.type == Type.NUMERIC:
            typeNum = colType.getType()
            if col["min"] <= typeNum.min:
                if col["min"] < typeNum.min:
                    message = _("Column '").__unicode__() + column.name + _("': old min: ").__unicode__() + unicode(typeNum.min) + _(", new min: ").__unicode__() + col["min"] + "."
                    history = historyfactory.writeTableHistory(history, table, request.user, HistoryTable.TABLE_MODIFIED, message)
                typeNum.min = col["min"]
            if typeNum.max <= col["max"]:
                if typeNum.max < col["max"]:
                    message = _("Column '").__unicode__() + column.name + _("': old max: ").__unicode__() + unicode(typeNum.max) + _(", new max: ").__unicode__() + col["max"] + "."
                    history = historyfactory.writeTableHistory(history, table, request.user, HistoryTable.TABLE_MODIFIED, message)
                typeNum.max = col["max"]
            typeNum.save()

        elif colType.type == Type.DATE:
            typeDate = colType.getType()
            if "min" in col and col["min"] <= typeDate.min:
                if col["min"] < typeDate.min:
                    message = _("Column '").__unicode__() + column.name + _("': old min: ").__unicode__() + unicode(typeDate.min) + _(", new min: ").__unicode__() + col["min"] + "."
                    history = historyfactory.writeTableHistory(history, table, request.user, HistoryTable.TABLE_MODIFIED, message)
                typeDate.min = col["min"]
            if "max" in col and col["max"] >= typeDate.max:
                if typeDate.max < col["max"]:
                    message = _("Column '").__unicode__() + column.name + _("': old max: ").__unicode__() + unicode(typeDate.max) + _(", new max: ").__unicode__() + col["max"] + "."
                    history = historyfactory.writeTableHistory(history, table, request.user, HistoryTable.TABLE_MODIFIED, message)
                typeDate.max = col["max"]
            typeDate.save()

        elif colType.type == Type.SELECTION:
            typeSel = colType.getType()
            if len([option["value"] for option in col["options"]]) > len(set([option["value"] for option in col["options"]])):
                return HttpResponse(json.dumps({"errors": [{"code": Error.TYPE_CREATE, "message": _("found duplicate selection values.").__unicode__()}]}), content_type="application/json")
            for option in col["options"]:
                if "key" in option:
                    value = SelectionValue.objects.get(index=option["key"], typeSelection=typeSel)
                    if value.content != option["value"]:
                        message = _("Column '").__unicode__() + column.name + _("': changed selection value from '").__unicode__() + value.content + _("' to '").__unicode__() + option["value"] + "."
                        history = historyfactory.writeTableHistory(history, table, request.user, HistoryTable.TABLE_MODIFIED, message)
                    value.content = option["value"]
                    value.save()
                    # change this selection value for all existing datasets.
                    for datasel in DataSelection.objects.filter(dataset__in=table.getDatasets(), column=column):
                        if str(datasel.key) == option["key"]:
                            datasel.content = option["value"]
                            datasel.save()
                else:  # this is a new selection value
                    typeSel.count += 1
                    typeSel.save()
                    selValF = SelectionValueForm({"index": typeSel.count, "content": option["value"]})
                    if selValF.is_valid():
                        selVal = selValF.save(commit=False)
                        selVal.typeSelection = typeSel
                        selVal.save()
                    message = _("Column '").__unicode__() + column.name + _("': added selection value '").__unicode__() + option["value"] + "'."
                    history = historyfactory.writeTableHistory(history, table, request.user, HistoryTable.TABLE_MODIFIED, message)

        elif colType.type == Type.TABLE:
            typeTable = colType.getType()
            refTable = typeTable.table
            if "column" in col:
                refColumns = refTable.getColumns()
                refColNames = list()
                for refColumn in refColumns:
                    if not refColumn.deleted:
                        refColNames.append(refColumn.name)
                if col["column"] not in refColNames:
                    return HttpResponse(json.dumps({"errors": [{"code": Error.COLUMN_REF, "message": _("Column ") + col["column"] + _(" does not exist in referenced table ").__unicode__() + col["table"] + "."}]}), content_type="application/json")
                try:
                    refColumn = refColumns.get(name=col["column"], deleted=False)
                except Column.DoesNotExist:
                    return HttpResponse(json.dumps({"errors": [{"code": Error.COLUMN_NOTFOUND, "message": _("Column ") + col["column"] + _(" does not exist.").__unicode__()}]}), content_type="application/json")
                typeTable.column = refColumn
            else:
                if typeTable.column:
                    message = _("Column '").__unicode__() + column.name + _("': Removed link to column '").__unicode__() + typeTable.column.name + "'."
                    history = historyfactory.writeTableHistory(history, table, request.user, HistoryTable.TABLE_MODIFIED, message)
                typeTable.column = None
                typeTable.save()

    return HttpResponse(json.dumps({"success": _("Successfully modified table structure.").__unicode__()}), content_type="application/json")


def modifyTableRights(rights, tableName, user):
    try:
        table = Table.objects.get(name=tableName, deleted=False)
    except Table.DoesNotExist:
        return HttpResponse({"errors": [{"code": Error.TABLE_NOTFOUND, "message": _("Could not find table with name " + tableName + ".").__unicode__()}]})
    if "rights" in rights:
        RightListForTable.objects.filter(table=table).exclude(user=user).delete()
        answer = createTableRights(rights["rights"], table, user)
        if not answer:
            return HttpResponse(json.dumps({"errors": [answer]}), content_type="application/json")

    for col in rights["columns"]:
        try:
            column = table.getColumns().get(name=col["name"], deleted=False)
        except Column.DoesNotExist:
            continue
        RightListForColumn.objects.filter(column=column).exclude(user=user).delete()
        answer = createColumnRights(col["rights"], column, user)
        if not answer:
            return HttpResponse(json.dumps({"errors": [answer]}), content_type="application/json")

    rights = historyfactory.printRightsFor(tableName)
    if rights is not None:
        message = "Current rights: "
        history = historyfactory.writeTableHistory(None, table, user, HistoryTable.TABLE_MODIFIED, message)
        for right in rights:
            historyfactory.writeTableHistory(history, table, user, HistoryTable.TABLE_MODIFIED, right)

    return HttpResponse(json.dumps({"success": _("Successfully modified rights.").__unicode__()}), content_type="application/json")


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
        theTable = Table.objects.get(name=tableName, deleted=False)
    except Table.DoesNotExist:
        return HttpResponse(json.dumps({"errors": [{"code": Error.TABLE_NOTFOUND, "message": _("Could not find table with name ").__unicode__() + tableName}]}))

    savedObjs = list()

    datasetF = DatasetForm({"created": datetime.utcnow().replace(tzinfo=utc)})
    if not datasetF.is_valid():
        return HttpResponse(json.dumps({"errors": [{"code": Error.DATASET_CREATE, "message": _("Error creating a new dataset.").__unicode__()}]}), content_type="application/json")

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
        if col["value"] is None:
            continue
        try:
            column = Column.objects.get(name=col["name"], table=theTable, deleted=False)
        except Column.DoesNotExist:
            for obj in savedObjs:
                obj.delete()
            HttpResponse(json.dumps({"errors": [{"code": Error.COLUMN_NOTFOUND, "message": _("Could not find a column with name ").__unicode__() + col["name"] + _("in table ").__unicode__() + tableName + _(". Abort.").__unicode__()}]}), content_type="application/json")
            continue
        if not column.type.getType().isValid(col["value"]):
            for obj in savedObjs:
                obj.delete()
            print col["value"]
            return HttpResponse(json.dumps({"errors": [{"code": Error.TYPE_INVALID, "message": _("input ").__unicode__() + unicode(col["value"]) + _(" for column ").__unicode__() + column.name + _(" is not valid. Abort.").__unicode__()}]}), content_type="application/json")

        if column.type.type == Type.TEXT:
            textF = DataTextForm({"created": datetime.utcnow().replace(tzinfo=utc), "content": col["value"]})
            if textF.is_valid():
                newData = textF.save(commit=False)

        elif column.type.type == Type.NUMERIC:
            numF = DataNumericForm({"created": datetime.utcnow().replace(tzinfo=utc), "content": col["value"]})
            if numF.is_valid():
                newData = numF.save(commit=False)

        elif column.type.type == Type.DATE:
            dateF = DataDateForm({"created": datetime.utcnow().replace(tzinfo=utc), "content": col["value"]})
            if dateF.is_valid():
                newData = dateF.save(commit=False)

        elif column.type.type == Type.SELECTION:
            selVal = SelectionValue.objects.get(typeSelection=column.type.getType(), content=col["value"])
            selF = DataSelectionForm({"created": datetime.utcnow().replace(tzinfo=utc), "content": col["value"], "key": selVal.index})
            if selF.is_valid():
                newData = selF.save(commit=False)

        elif column.type.type == Type.BOOL:
            boolF = DataBoolForm({"created": datetime.utcnow().replace(tzinfo=utc), "content": col["value"]})
            if boolF.is_valid():
                newData = boolF.save(commit=False)

        elif column.type.type == Type.TABLE:
            dataTblF = DataTableForm({"created": datetime.utcnow().replace(tzinfo=utc)})
            if dataTblF.is_valid():
                newData = dataTblF.save(commit=False)

        if newData is None:
            for obj in savedObjs:
                obj.delete()
            return HttpResponse(json.dumps({"errors": [{"code": Error.DATAFIELD_CREATE, "message": _("Could not add data for column ").__unicode__() + col["name"] + _(". The content type was not valid. Abort.").__unicode__()}]}), content_type="application/json")

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
                    return HttpResponse(json.dumps({"errors": [{"code": Error.DATASET_NOTFOUND, "message": _("dataset with id ").__unicode__() + index + _(" could not be found in table ").__unicode__() + column.type.getType().table.name + _(". Abort.").__unicode__()}]}), content_type="application/json")
                else:
                    link = TableLink()
                    link.dataTable = newData
                    link.dataset = dataset
                    link.save()
                    savedObjs.append(link)

    historyfactory.writeTableHistory(None, theTable, request.user, HistoryTable.DATASET_INSERTED, historyfactory.printDataset(newDataset.datasetID, request.user))
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
        theTable = Table.objects.get(name=tableName, deleted=False)
    except Table.DoesNotExist:
        return HttpResponse(json.dumps({"errors": [{"code": Error.TABLE_CREATE, "message": _("Failed to create table. Please contact the developers.").__unicode__()}]}))
    try:
        dataset = Dataset.objects.get(datasetID=datasetID)
    except Dataset.DoesNotExist:
        return HttpResponse(json.dumps({"errors": [{"code": Error.DATASET_NOTFOUND, "message": _("Could not find dataset with id ").__unicode__() + datasetID + _(" in table ").__unicode__() + tableName + "."}]}), content_type="application/json")

    dataCreatedNewly = False  # is set to True if a data element was not modified but created newly
    newData = None
    message = "ID: " + unicode(dataset.datasetID) + ". \n"  # message for the history
    history = historyfactory.writeTableHistory(None, theTable, request.user, HistoryTable.DATASET_MODIFIED, message)
    for col in jsonRequest["columns"]:
        if "value" not in col:
            continue
        if col["value"] is None:
            continue
        try:
            column = Column.objects.get(name=col["name"], table=theTable, deleted=False)
        except Column.DoesNotExist:
            HttpResponse(json.dumps({"errors": [{"code": Error.COLUMN_NOTFOUND, "message": _("Could not find column with name ").__unicode__() + col["name"] + "."}]}), content_type="application/json")
            continue

        if not column.type.getType().isValid(col["value"]):
            return HttpResponse(json.dumps({"errors": [{"code": Error.TYPE_INVALID, "message": _("input ").__unicode__() + unicode(col["value"]) + _(" for column ").__unicode__() + column.name + _(" is not valid.").__unicode__()}]}), content_type="application/json")

        if column.type.type == Type.TEXT:
            try:
                text = dataset.datatext.get(column=column)
                text.modified = datetime.utcnow().replace(tzinfo=utc)
                text.modifier = request.user
                if text.content != col["value"]:
                    message = column.name + _(": old: '").__unicode__() + text.content + _("', new: '").__unicode__() + col["value"] + "'"
                    history = historyfactory.writeTableHistory(history, theTable, request.user, HistoryTable.DATASET_MODIFIED, message)
                text.content = col["value"]
                text.save()
            except DataText.DoesNotExist:
                dataCreatedNewly = True
                textF = DataTextForm({"created": datetime.utcnow().replace(tzinfo=utc), "content": col["value"]})
                if textF.is_valid():
                    newData = textF.save(commit=False)
                    message = column.name + _(": new entry: '").__unicode__() + col["value"] + "'"
                    history = historyfactory.writeTableHistory(history, theTable, request.user, HistoryTable.DATASET_MODIFIED, message)

        elif column.type.type == Type.NUMERIC:
            try:
                num = dataset.datanumeric.get(column=column)
                num.modified = datetime.utcnow().replace(tzinfo=utc)
                num.modifier = request.user
                if num.content != col["value"]:
                    message = column.name + _(": old: '").__unicode__() + unicode(num.content) + _("', new: '").__unicode__() + unicode(col["value"]) + "'"
                    history = historyfactory.writeTableHistory(history, theTable, request.user, HistoryTable.DATASET_MODIFIED, message)
                num.content = col["value"]
                num.save()
            except DataNumeric.DoesNotExist:
                dataCreatedNewly = True
                numF = DataNumericForm({"created": datetime.utcnow().replace(tzinfo=utc), "content": col["value"]})
                if numF.is_valid():
                    newData = numF.save(commit=False)
                    message = column.name + _(": new entry: '").__unicode__() + unicode(col["value"]) + "'"
                    history = historyfactory.writeTableHistory(history, theTable, request.user, HistoryTable.DATASET_MODIFIED, message)

        elif column.type.type == Type.DATE:
            try:
                date = dataset.datadate.get(column=column)
                date.modified = datetime.utcnow().replace(tzinfo=utc)
                date.modifier = request.user
                if unicode(date.content) != col["value"]:
                    message = column.name + _(": old: '").__unicode__() + unicode(date.content) + _("', new: '").__unicode__() + unicode(col["value"]) + "'"
                    history = historyfactory.writeTableHistory(history, theTable, request.user, HistoryTable.DATASET_MODIFIED, message)
                date.content = col["value"]
                date.save()
            except DataDate.DoesNotExist:
                dataCreatedNewly = True
                dateF = DataDateForm({"created": datetime.utcnow().replace(tzinfo=utc), "content": col["value"]})
                if dateF.is_valid():
                    newData = dateF.save(commit=False)
                    message = column.name + _(": new entry: '").__unicode__() + unicode(col["value"]) + "'"
                    history = historyfactory.writeTableHistory(history, theTable, request.user, HistoryTable.DATASET_MODIFIED, message)

        elif column.type.type == Type.SELECTION:
            try:
                sel = dataset.dataselection.get(column=column)
                sel.modified = datetime.utcnow().replace(tzinfo=utc)
                sel.modifier = request.user
                if sel.content != col["value"]:
                    message = column.name + _(": old: '").__unicode__() + unicode(sel.content) + _("', new: '").__unicode__() + unicode(col["value"]) + "'"
                    history = historyfactory.writeTableHistory(history, theTable, request.user, HistoryTable.DATASET_MODIFIED, message)
                sel.content = col["value"]
                sel.save()
            except DataSelection.DoesNotExist:
                dataCreatedNewly = True
                selF = DataSelectionForm({"created": datetime.utcnow().replace(tzinfo=utc), "content": col["value"]})
                if selF.is_valid():
                    newData = selF.save(commit=False)
                    message = column.name + _(": new entry: '").__unicode__() + unicode(col["value"]) + "'"
                    history = historyfactory.writeTableHistory(history, theTable, request.user, HistoryTable.DATASET_MODIFIED, message)

        elif column.type.type == Type.BOOL:
            try:
                bool = dataset.databool.get(column=column)
                bool.modified = datetime.utcnow().replace(tzinfo=utc)
                bool.modifier = request.user
                if bool.content != col["value"]:
                    message += column.name + _(": old: '").__unicode__() + unicode(bool.content) + _("', new: '").__unicode__() + unicode(col["value"]) + "',\n"
                bool.content = col["value"]
                bool.save()
            except DataBool.DoesNotExist:
                dataCreatedNewly = True
                boolF = DataBoolForm({"created": datetime.utcnow().replace(tzinfo=utc), "content": col["value"]})
                if boolF.is_valid():
                    newData = boolF.save(commit=False)
                    message = column.name + _(": new entry: '").__unicode__() + unicode(col["value"]) + "'"
                    history = historyfactory.writeTableHistory(history, theTable, request.user, HistoryTable.DATASET_MODIFIED, message)

        elif column.type.type == Type.TABLE:
            try:
                dataTbl = dataset.datatable.get(column=column)
                links = TableLink.objects.filter(dataTable=dataTbl)
                setIDs = list()
                #  remove all links between dataTable and datasets which are not listed in col["value"]
                for link in links:
                    setIDs.append(link.dataset_id)
                    if link.dataset_id not in col["value"]:
                        message = column.name + _(": removed link to dataset: '").__unicode__() + unicode(link.dataset.datasetID) + "'"
                        history = historyfactory.writeTableHistory(history, theTable, request.user, HistoryTable.DATASET_MODIFIED, message)
                        link.delete()

                #  now add any link that does not exist yet
                for id in [index for index in col["value"] if index not in setIDs]:  # this list comprehension returns the difference col["value"] - setIDs
                    try:
                        newDataset = Dataset.objects.get(datasetID=id)
                        newLink = TableLink()
                        newLink.dataTable = dataTbl
                        newLink.dataset = newDataset
                        message = column.name + _(": added link to dataset: '").__unicode__() + id + "'"
                        history = historyfactory.writeTableHistory(history, theTable, request.user, HistoryTable.DATASET_MODIFIED, message)
                        newLink.save()
                    except Dataset.DoesNotExist:
                        return HttpResponse(json.dumps({"errors": [{"code": Error.DATASET_NOTFOUND, "message": _("Could not find dataset with id ").__unicode__() + id + "."}]}), content_type="application/json")

            except DataTable.DoesNotExist:
                dataCreatedNewly = True
                dataTblF = DataTableForm({"created": datetime.utcnow().replace(tzinfo=utc)})
                if dataTblF.is_valid():
                    newData = dataTblF.save(commit=False)

        if dataCreatedNewly:
            if newData is None:
                return HttpResponse(json.dumps({"errors": [{"code": Error.TYPE_NOTYPE, "message": _("Could not add data to column ").__unicode__() + col["name"] + _(". The content type was invalid.").__unicode__()}]}), content_type="application/json")

            else:
                newData.creator = request.user
                newData.column = column
                newData.dataset = Dataset.objects.get(datasetID=datasetID)
                newData.save()

            # this must be performed at the end, because TableLink receives newData, which has to be saved first
            if column.type.type == Type.TABLE and newData is not None:
                for index in col["value"]:  # find all datasets for this
                    try:
                        dataset = Dataset.objects.get(datasetID=index)
                        link = TableLink()
                        link.dataTable = newData
                        link.dataset = dataset
                        message = column.name + _(": added link to dataset: '").__unicode__() + index + "'"
                        history = historyfactory.writeTableHistory(history, theTable, request.user, HistoryTable.DATASET_MODIFIED, message)
                        link.save()
                    except Dataset.DoesNotExist:
                        return HttpResponse(json.dumps({"errors": [{"code": Error.DATASET_NOTFOUND, "message": _("Could not find dataset with id ").__unicode__() + index + "."}]}), content_type="application/json")

    return HttpResponse(json.dumps({"id": dataset.datasetID}), status=200)


def exportTable(request, tableName):
    try:
        table = Table.objects.get(name=tableName, deleted=False)
    except Table.DoesNotExist:
        return HttpResponse(json.dumps({"errors":[{"message":_("Could not find table with name ").__unicode__() + tableName + "."}]}))

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename='" + table.name + "_" + str(datetime.utcnow().replace(tzinfo=utc)) + ".csv'"

    writer = csv.writer(response)
    writer.writerow([table.name + " from " + str(datetime.utcnow().replace(tzinfo=utc))])
    writer.writerow(["system ID"] + request["columns"])

    for datasetID in request["datasets"]:
        try:
            dataset = Dataset.objects.get(datasetID=datasetID)
        except Dataset.DoesNotExist:
            return HttpResponse(json.dumps({"errors":[{"message":_("Could not find dataset with ID ").__unicode__() + datasetID + "."}]}))
        row = list()
        row.append(datasetID)
        for colName in request["columns"]:
            try:
                column = Column.objects.get(name=colName, table=table, deleted=False)
            except Column.DoesNotExist:
                return HttpResponse(json.dumps({"errors":[{"message":_("Could not find column with name ").__unicode__() + colName + _(" in table ").__unicode__() + tableName + "."}]}))
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
