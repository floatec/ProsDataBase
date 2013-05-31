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
        result["datasets"] = list()
        try:
            datasets = table.getDatasets()
        except Dataset.DoesNotExist:
            pass

        for dataset in datasets:
            row = dict()
            row["id"] = dataset.pk
            row["data"] = list()

            data = dataset.getData()
            for primitiveData in data:
                for item in primitiveData:
                    dataObj = dict()
                    dataObj["column"] = item.column.name
                    dataObj["type"] = item.column.type.type
                    if dataObj["type"] == Type.TABLE:
                        dataObj["value"] = list()
                        for link in DataTableToDataset.objects.filter(DataTable=item):
                            dataObj["value"].append(link.dataset_id)
                    else:
                        try:
                            dataObj["value"] = str(item.content)
                        except UnicodeEncodeError:
                            dataObj["value"] = unicode(item.content)

                    row["data"].append(dataObj)

            result["datasets"].append(row)

        return json.dumps(result)

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
        tables = Table.objects.all()
        result = dict()
        result["tables"] = []

        for table in tables:
            columns = table.getColumns()
            columnNames = []
            print columns
            for col in columns:
                print "hi"
                columnNames.append(col.name)

            result["tables"].append({"name": table.name, "column": columnNames})

        return json.dumps(result)

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
        return json.dumps(result)


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

        return json.dumps(result)

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

        return json.dumps(result)


class GroupSerializer:
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

        return json.dumps(result)

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
        groups = DBGroup.objects.all()
        result = dict()
        result["groups"] = []

        for group in groups:
            result["groups"].append(group.name)

        return json.dumps(result)


class DatasetSerializer:

    def serializeAll(self, tableRef):
        """
        return all datasets of table tableRef

        {
            "name": "example",
            "columns": ["columname", "anothercolum"],
            "datasets": [
                [value, value],
                [value, value]
            ]
        }
        """
        result = dict()
        result["name"] = tableRef.name

        columns = Column.objects.filter(table=tableRef)
        columnNames = []
        for col in columns:
            columnNames.append(col.name)
        result["columns"] = columnNames

        datasetList = []
        datasets = Dataset.objects.filter(table=tableRef)
        for dataset in datasets:
            values = dataset.getData().values()
            datasetList.append(values)
        result["datasets"] = datasetList

        return json.dumps(result)

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