# -*- coding: utf-8 -*-
__author__ = 'My-Tien Nguyen'

from models import *


class TableSerializer:
    @staticmethod
    def serializeOne(tableName, user):
        """
        return the table with specified name, along with its columns and datasets.

        {
            "name": "example",
            "datasets": [
                {"id": 38, "data": [ {"column": "id", "type": 1, "value": 0}, "column": "columnname", "type": 0, "value": "aString"}, {"column": "anothercolumn", "type": 5, "value": [1, 2], "table": "aTableName"} ]},  //row 1
                {"id": 18, "data": [ {"column": "id", "type": 1, "value": 17}, "column": "columnname", "type": 0, "value": "aString"}, {"column": "anothercolumn", "type": 5, "value": [13, 14], "table": "aTableName"} ]}   //row 2
            ]
        }
        """
        try:
            table = Table.objects.get(name=tableName)
        except Table.DoesNotExist:
            return None

        result = dict()
        result["name"] = table.name
        result.update(DatasetSerializer.serializeAll(tableName, user))

        return result

    @staticmethod
    def serializeAll(user):
        """
        return all tables with their columns

        {
            "tables": [
                {"name": "example", "columns": ["columname","anothercolum"]},
                {"name": "2nd", "columns": ["columname","anothercolum"]}
            ]
        }
        """
        user = user
        allowedTables = set()

        for rights in RightListForColumn.objects.filter(user=user):
            allowedTables.add(rights.column.table)

        result = dict()
        result["tables"] = list()

        # first find all tables with no group
        tables = Table.objects.filter(name__in=allowedTables)
        for table in tables:
            if table.deleted:
                continue
            columns = table.getColumns()
            columnNames = []
            for col in columns:
                columnNames.append(col.name)

            result["tables"].append({"name": table.name, "columns": columnNames, "category": table.category.name})

        return result

    @staticmethod
    def serializeStructure(tableName):
        """
        return the table with its columns and the column's datatypes as well as ranges

        {
          "category": "categoryname"
          "columns": [
            {"name": "columnname0", "type": 0, "length": 100},
            {"name": "columnname1", "type": 1, "min": "a decimal", "max": "a decimal"},
            {"name": "columnname2", "type": 2, "min": "a date", "max": "a date"},
            {"name": "columnname3", "type": 3, "options": {"0": "opt1", "1": "opt2", "2": "opt3"},
            {"name": "columnname4", "type": 4, "table": "tablename", "shownColumn": "PSA"},
          ]
        }
        """
        table = Table.objects.get(name=tableName)
        if table is None:
            return None

        columns = table.getColumns()
        colStructs = []
        for col in columns:
            comment = col.comment if col.comment is not None else ""
            type = col.type.type
            if type is Type.TEXT:
                colStructs.append({"id": col.id, "name": col.name, "type": Type.TEXT, "length": col.type.getType().length, "comment": comment})
            elif type is Type.NUMERIC:
                colStructs.append({"id": col.id, "name": col.name, "type": Type.NUMERIC, "min": col.type.getType().min, "max": col.type.getType().max, "comment": comment})
            elif type is Type.DATE:
                colStructs.append({"id": col.id, "name": col.name, "type": Type.DATE, "min": col.type.getType().min, "max": col.type.getType().max, "comment": comment})

            elif type is Type.SELECTION:
                options = list()
                for value in col.type.getType().values():
                    options.append({"key": value.index, "value": value.content})
                colStructs.append({"id": col.id, "name": col.name, "type": Type.SELECTION, "options": options, "comment": comment})
            elif type is Type.BOOL:
                colStructs.append({"id": col.id, "name": col.name, "type": Type.BOOL, "comment": comment})
            elif type is Type.TABLE:
                if col.type.getType().column is not None:
                    refCol = col.type.getType().column
                    colStructs.append({"id": col.id, "name": col.name, "type": Type.TABLE, "table": col.type.getType().table.name, "column": refCol.name, "refType": refCol.type.type, "comment": comment})
                else:
                    colStructs.append({"id": col.id, "name": col.name, "type": Type.TABLE, "table": col.type.getType().table.name, "comment": comment})
            else:
                return None

        #  add relation columns, that is, the columns, in which this table can be found in other tables
        typeTables = TypeTable.objects.filter(table=table)
        for typeTable in typeTables:
            typesColumn = Column.objects.get(type=typeTable.type)
            if typeTable.column is None:
                colStructs.append({"name": typesColumn.name + " in " + typesColumn.table.name, "type": Type.LINK, "table": typesColumn.table.name})

        result = dict()
        result["category"] = table.category.name
        result["columns"] = colStructs
        return result

    @staticmethod
    def serializeCategories():
        """
        {
            "categories": ["cat1", "cat2", "cat3"]
        }
        """
        result = dict()
        result["categories"] = list()
        for cat in Category.objects.all():
            result["categories"].append(cat.name)
        return result


    @staticmethod
    def serializeRightsFor(tableName):
        """
        {
            "actors": [
                {
                    "name": "actor1",
                    "tableRights": {"insert": false, "delete": false, "viewLog": true, "rightsAdmin": true},
                    "columnRights": [
                        {"name": "col1", "rights": {"modify": true, "read": true}},
                        {"name": "col2", "rights": {"modify": false, "read": true}},
                        {"name": "col3", "rights": {"modify": false, "read": true}},
                        {"name": "col4", "rights": {"modify": false, "read": true}}
                    ]
                },
                {
                    "name": "actor2",
                    "tableRights": {"viewLog": false, "rightsAdmin": false, "delete": true, "insert": true},
                    "columnRights": []
                }
            ]
        }
        """
        try:
            table = Table.objects.get(name=tableName)
        except Table.DoesNotExist:
            return None

        result = dict()

        result["actors"] = list()
        users = table.getUsersWithRights()
        for user in users:
            userObj = dict()
            userObj["name"] = user.username
            rights = TableSerializer.serializeRightsForActor(user.username, table.name)
            userObj["tableRights"] = rights["tableRights"]
            userObj["columnRights"] = rights["columnRights"]

            result["actors"].append(userObj)

        groups = table.getGroupsWithRights()
        for group in groups:
            groupObj = dict()
            groupObj["name"] = group.name
            rights = TableSerializer.serializeRightsForActor(group.name, table.name)
            groupObj["tableRights"] = rights["tableRights"]
            groupObj["columnRights"] = rights["columnRights"]

            result["actors"].append(groupObj)

        return result


    @staticmethod
    def serializeRightsForActor(name, tableName):
        """
        {
            "name": "actor1",
            "tableRights": {"insert": false, "delete": false, "viewLog": true, "rightsAdmin": true},
            "columnRights": [
                {"name": "col1", "rights": {"modify": true, "read": true}},
                {"name": "col2", "rights": {"modify": false, "read": true}}
            ]
        }
        """
        try:
            table = Table.objects.get(name=tableName)
        except Table.DoesNotExist:
            return None
        # either a user or a group name was passed
        try:
            actor = DBUser.objects.get(username=name)
            user = True
        except DBUser.DoesNotExist:
            actor = DBGroup.objects.get(name=name)
            user = False

        if user:
            try:
                tableRights = RightListForTable.objects.get(user=actor, table=table)
            except RightListForTable. DoesNotExist:
                tableRights = None
            try:
                columnRights = RightListForColumn.objects.filter(user=actor, table=table)
            except RightListForColumn.DoesNotExist:
                columnRights = None
        else:  # a group was passed
            try:
                tableRights = RightListForTable.objects.get(group=actor, table=table)
            except RightListForTable. DoesNotExist:
                tableRights = None
            try:
                columnRights = RightListForColumn.objects.filter(group=actor, table=table)
            except RightListForColumn.DoesNotExist:
                columnRights = None

        result = dict()
        result["tableRights"] = dict()
        result["tableRights"]["rightsAdmin"] = tableRights.rightsAdmin if tableRights else False
        result["tableRights"]["viewLog"] = tableRights.viewLog if tableRights else False
        result["tableRights"]["insert"] = tableRights.insert if tableRights else False
        result["tableRights"]["delete"] = tableRights.delete if tableRights else False

        result["columnRights"] = list()
        for rights in columnRights:
            colObj = dict()
            colObj["name"] = rights.column.name
            colObj["rights"] = dict()
            colObj["rights"]["read"] = rights.read if columnRights else False
            colObj["rights"]["modify"] = rights.modify if columnRights else False

            result["columnRights"].append(colObj)

        return result


class UserSerializer:
    @staticmethod
    def serializeOne(username):
        """
        {
            "name": "myname",
            "groups": ["groupname1", "groupname2", "groupname3"],
            "groupCreator": true,
            "tableCreator": false
        }
        """
        try:
            user = DBUser.objects.get(username=username)
        except DBUser.DoesNotExist:
            return None

        result = dict()
        result["name"] = username
        result["groups"] = list()

        for m in Membership.objects.filter(user=user):
            result["groups"].append(m.group.name)

        result["tableCreator"] = user.tableCreator
        result["groupCreator"] = user.groupCreator
        result["userManager"] = user.userManager
        result["admin"] = user.admin

        return result

    @staticmethod
    def serializeAll():
        """
        return all tables with their columns

        {
            "users": [
                {"id":"1","name": "example"},
                {"id":"2","name": "example2"}]}
            ]
        }
        """
        users = DBUser.objects.all()
        result = dict()
        result["users"] = []

        for user in users:
            result["users"].append(user.username)

        return result


class GroupSerializer:
    @staticmethod
    def serializeOne(id):
        """
        {
            "name": "group1",
            "users": [
                {"name": "John Doe"},
                {"name": "Alex Anonymus"}
            ]
        }
        """
        try:
            group = DBGroup.objects.get(name=id)
        except DBGroup.DoesNotExist:
            return False

        theGroup = dict()
        theGroup["name"] = group.name
        theGroup["tableCreator"] = group.tableCreator
        theGroup["groupCreator"] = group.groupCreator
        theGroup["userManager"] = group.userManager
        theGroup["admins"] = list()
        theGroup["users"] = list()

        for m in Membership.objects.filter(group=group, isAdmin=True):
            theGroup["admins"].append(m.user.username)

        for m in Membership.objects.filter(group=group, isAdmin=False):
            theGroup["users"].append(m.user.username)

        return theGroup

    @staticmethod
    def serializeAll():
        """
        return all groups

        """
        groups = DBGroup.objects.all()
        result = dict()
        result["groups"] = []

        for group in groups:
            result["groups"].append(GroupSerializer.serializeOne(group.name))

        return result


class DatasetSerializer:

    @staticmethod
    def serializeOne(id, user):
        """
        {
            "id": "2.2013_192_B",
            "data": [
                {"column": "columnname1", "type": 0, "value": "aText"},
                {"column": "columnname2", "type": 1, "value": 392.03},
                {"column": "columnname3", "type": 2, "value": "2013-08-22 10:55:00"},
                {"column": "columnname4", "type": 3, "value": "aSelectionOption"},
                {"column": "columnname5", "type": 4, "value": true},
                {"column": "columnname6", "type": 5, "value": ["5.2013_3_B", "5.2013_4_K"], "table": "aTableName"}
            ]
        }
        """
        try:
            dataset = Dataset.objects.get(datasetID=id)
        except Dataset.DoesNotExist:
            return None

        result = dict()
        result["id"] = dataset.datasetID
        result["data"] = list()

        datalist = dataset.getData()
        for data in datalist:
            for item in data:

                dataObj = dict()
                dataObj["column"] = item.column.name
                dataObj["type"] = item.column.type.type

                if dataObj["type"] == Type.TABLE:
                    dataObj["value"] = list()
                    for link in DataTableToDataset.objects.filter(DataTable=item):
                        valObj = dict()
                        valObj["id"] = link.dataset.datasetID
                        typeTable = item.column.type.getType()
                        columnForDisplay = typeTable.column if typeTable.column else None
                        if columnForDisplay:
                            refDataList = link.dataset.getData()
                            for refData in refDataList:
                                for refItem in refData:
                                    if refItem.column == columnForDisplay:
                                        valObj["value"] = refItem.content

                        dataObj["value"].append(valObj)

                else:
                    try:
                        dataObj["value"] = str(item.content)
                    except UnicodeEncodeError:
                        dataObj["value"] = unicode(item.content)

                result["data"].append(dataObj)

        return result

    @staticmethod
    def serializeAll(tableRef, user):
        try:
            datasets = Dataset.objects.filter(table=tableRef)
        except Dataset.DoesNotExist:
            pass

        result = dict()
        result["datasets"] = list()
        for dataset in datasets:
            if dataset.deleted:
                continue
            result["datasets"].append(DatasetSerializer.serializeOne(dataset.datasetID, user))

        return result

    @staticmethod
    def serializeBy(request, tableName, user):
        """
        {
            "column": "columnname",
            "child": {
                "column": "columnInRelatedTable",
                "child": {
                    "column": "columnname2", "min": 12, "max": 20
                }
            }
        }
        """
        try:
            table = Table.objects.get(name=tableName)
        except Table.DoesNotExist:
            return None

        try:
            column = table.getColumns().get(name=request["column"])
        except Column.DoesNotExist:
            return None

        if "child" not in request:  # filter only with criteria on this table
            result = dict()
            result["datasets"] = list()

            ownDatasets = Dataset.objects.filter(table=table)
            if column.type.type == Type.TEXT:
                dataTexts = DataText.objects.filter(dataset__in=ownDatasets, content__contains=request["substr"])
                for data in dataTexts:
                    result["datasets"].append(DatasetSerializer.serializeOne(data.dataset.datasetID, user))
            if column.type.type == Type.NUMERIC:
                dataNumerics = DataNumeric.objects.filter(dataset__in=ownDatasets, content__gte=request["min"], content__lte=request["max"])
                for data in dataNumerics:
                    result["datasets"].append(DatasetSerializer.serializeOne(data.dataset.datasetID, user))
            if column.type.type == Type.DATE:
                dataDates = DataDate.objects.filter(dataset__in=ownDatasets, content__gte=request["min"], content__lte=request["max"])
                for data in dataDates:
                    result["datasets"].append(DatasetSerializer.serializeOne(data.dataset.datasetID, user))
            if column.type.type == Type.SELECTION:
                dataSelections = DataSelection.objects.filter(dataset__in=ownDatasets, content__in=request["options"])
                for data in dataSelections:
                    result["datasets"].append(DatasetSerializer.serializeOne(data.dataset.datasetID, user))

            return result

        else:  # filter with criteria on nested table
            nextTable = column.type.getType().table.name
            return DatasetSerializer.serializeBy(request["child"], nextTable, user)