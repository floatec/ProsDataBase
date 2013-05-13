__author__ = 'My-Tien Nguyen'

from models import *
import json


# TODO: how to convert CharFields to String? unicode(model.CharField()) or model.CharField().__unicode__()? Or entirely different?


class TableSerializer:
    @staticmethod
    def serializeOne(id):
        table = Table.objects.get(pk=id)
        dataDescrs = table.dataDescrs()
        dataDescrNames = []

        for col in dataDescrs:
            dataDescrNames.append(unicode(col.name))

        result = dict()
        result["name"] = table.name
        result["dataDescr"] = dataDescrNames

        return json.dumps(result)

    @staticmethod
    def serializeAll():
        tables = Table.objects.all()
        result = dict()
        result["tables"] = []

        for table in tables:
            dataDescrs = table.dataDescrs()
            dataDescrNames = []

            for col in dataDescrs:
                dataDescrNames.append(col.name)

            result["tables"].append({"name": table.name, "dataDescr": dataDescrNames})

        return json.dumps(result)


class DatasetSerializer:

    def serializeAll(self, tableRef):  # tableRef is an instance of table
        result = dict()
        result["name"] = tableRef.name

        dataDescrs = DataDescr.objects.filter(table=tableRef)
        dataDescrNames = []
        for col in dataDescrs:
            dataDescrNames.append(col.name)
        result["dataDescr"] = dataDescrNames

        datasetList = []
        datasets = Dataset.objects.filter(table=tableRef)
        for dataset in datasets:
            values = dataset.data().values()
            datasetList.append(values)
        result["datasets"] = datasetList

        return json.dumps(result)

    def serializeBy(self, tableRef, rangeFlag, filter):  # tuple of criteria-dicts
        result = dict()
        result["name"] = tableRef.name

        dataDescrs = DataDescr.objects.filter(table=tableRef)
        dataDescrNames = []
        for col in dataDescrs:
            dataDescrNames.append(col.name)
        result["dataDescr"] = dataDescrNames

        datasetList = []
        datasets = Dataset.objects.filter(table=tableRef)
        for crit in filter:
            if len(crit) < 3 and rangeFlag:
                for dataset in datasets:
                    field = crit.iterkeys().next()