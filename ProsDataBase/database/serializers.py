# -*- coding: utf-8 -*-
__author__ = 'My-Tien Nguyen'

from models import *


import json


# TODO: how to convert CharFields to String? unicode(model.CharField()) or model.CharField().__unicode__()? Or entirely different?


class TableSerializer:
    @staticmethod
    def serializeOne(tableName):
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
        table = Table.objects.get(name=tableName)

        if table is None:  # table does not exist!
            return False

        result = dict()
        result["name"] = table.name
        result.update(DatasetSerializer.serializeAll(tableName))

        return result

    @staticmethod
    def serializeAll():
        """
        return all tables with their columns

        {
            "tables": [
                {"name": "example", "columns": ["columname","anothercolum"]},
                {"name": "2nd", "columns": ["columname","anothercolum"]}
            ]
        }
        """
        result = dict()
        result["tables"] = list()
        result["tableGroups"] = list()

        # first find all tables with no group
        tables = Table.objects.filter(tablegroup=None)
        for table in tables:
            if table.deleted:
                continue
            columns = table.getColumns()
            columnNames = []
            for col in columns:
                columnNames.append(col.name)

            result["tables"].append({"name": table.name, "columns": columnNames})

        # now find all tables with a group
        groups = TableGroup.objects.all()
        for group in groups:
            groupObj = dict()
            groupObj["name"] = group.name
            groupObj["tables"] = list()

            tables = Table.objects.filter(tablegroup=group)
            for table in tables:
                if table.deleted:
                    continue
                columns = table.getColumns()
                columnNames = []
                for col in columns:
                    columnNames.append(col.name)

                groupObj["tables"].append({"name": table.name, "columns": columnNames})

            result["tableGroups"].append(groupObj)
        return result

    @staticmethod
    def serializeStructure(tableName):
        """
        return the table with its columns and the column's datatypes as well as ranges

        {
          "columns": [
            {"name": "columnname0", "type": 0, "length": 100},
            {"name": "columnname1", "type": 1, "min": "a decimal", "max": "a decimal"},
            {"name": "columnname2", "type": 2, "min": "a date", "max": "a date"},
            {"name": "columnname3", "type": 3, "options": {"0": "opt1", "1": "opt2", "2": "opt3"},
            {"name": "columnname4", "type": 4, "table": "tablename"},
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
                colStructs.append({"name": col.name, "type": Type.TEXT, "length": col.type.getType().length, "comment": comment})
            elif type is Type.NUMERIC:
                colStructs.append({"name": col.name, "type": Type.NUMERIC, "min": col.type.getType().min, "max": col.type.getType().max, "comment": comment})
            elif type is Type.DATE:
                colStructs.append({"name": col.name, "type": Type.DATE, "min": col.type.getType().min, "max": col.type.getType().max, "comment": comment})

            elif type is Type.SELECTION:
                options = list()
                for value in col.type.getType().values():
                    options.append({"key": value.index, "value": value.content})
                colStructs.append({"name": col.name, "type": Type.SELECTION, "options": options, "comment": comment})
            elif type is Type.BOOL:
                colStructs.append({"name": col.name, "type": Type.BOOL, "comment": comment})
            elif type is Type.TABLE:
                colStructs.append({"name": col.name, "type": Type.TABLE, "table": col.type.getType().table.name, "comment": comment})
            else:
                return None

        result = dict()
        result["columns"] = colStructs
        return result


class UserSerializer:
    @staticmethod
    def serializeOne(id):
        """
        return table with specified id

        {"id":"1","name": "example"}
        """
        user = AbstractUser.objects.get(pk=id)

        result = dict()
        result["name"] = user.username
        result["id"] = user.id

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
    def serializeOne(id):
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
                        columnForDisplay = typeTable.column

                        refDataList = link.dataset.getData()
                        for refData in refDataList:
                            for refItem in refData:
                                print refItem.column
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
    def serializeAll(tableRef):
        try:
            datasets = Dataset.objects.filter(table=tableRef)
        except Dataset.DoesNotExist:
            pass

        result = dict()
        result["datasets"] = list()
        for dataset in datasets:
            if dataset.deleted:
                continue
            result["datasets"].append(DatasetSerializer.serializeOne(dataset.datasetID))

        return result

    def serializeBy(self, tableRef, rangeFlag, filter):  # tuple of criteria-dicts
        result = dict()
        result["name"] = tableRef.name

        columns = Column.objects.filter(table=tableRef)
        columnNames = []
        for col in columns:
            columnNames.append(col.name)
        result["column"] = columnNames

        datasetList = []
        datasets = Dataset.objects.filter(table=tableRef)
        for crit in filter:
            if len(crit) < 3 and rangeFlag:
                for dataset in datasets:
                    field = crit.iterkeys().next()