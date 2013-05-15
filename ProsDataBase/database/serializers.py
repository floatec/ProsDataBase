from locale import _group

__author__ = 'My-Tien Nguyen'

from models import *


import json


# TODO: how to convert CharFields to String? unicode(model.CharField()) or model.CharField().__unicode__()? Or entirely different?


class TableSerializer:
    @staticmethod
    def serializeOne(id):
        """
        return table with specified id

        {"name": "example", "column": ["columname","anothercolum"]}
        """
        table = Table.objects.get(pk=id)
        columns = table.getColumns()
        columnNames = []

        for col in columns:
            columnNames.append(col.name)

        result = dict()
        result["name"] = table.name
        result["column"] = columnNames

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

            for col in columns:
                columnNames.append(col.name)

            result["tables"].append({"name": table.name, "column": columnNames})

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
            result["users"].append( user.username)

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

    def serializeAll(self, tableRef):  # tableRef is an instance of table
        result = dict()
        result["name"] = tableRef.name

        columns = Column.objects.filter(table=tableRef)
        columnNames = []
        for col in columns:
            columnNames.append(col.name)
        result["column"] = columnNames

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