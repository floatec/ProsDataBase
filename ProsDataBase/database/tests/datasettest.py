from factory import *
from datetime import datetime
from django.test import TestCase


class DatasetTest(TestCase):
    def test_serializeOne(self):
        schmog = UserFactory.createRandomUser("test")
        table = StructureFactory.createTable(schmog)

        datasetF = DatasetForm({"created": datetime.now()})
        if datasetF.is_valid():
            dataset = datasetF.save(commit=False)
            dataset.table = table
            dataset.creator = schmog
            dataset.save()
            dataset.datasetID = table.generateDatasetID(dataset)
            dataset.save()

        textType = Type.objects.get(type=Type.TEXT)
        numType = Type.objects.get(type=Type.NUMERIC)
        dateType = Type.objects.get(type=Type.DATE)
        selType = Type.objects.get(type=Type.SELECTION)
        boolType = Type.objects.get(type=Type.BOOL)

        textF = DataTextForm({"created": datetime.now(), "content": LiteralFactory.genRandString()})
        if textF.is_valid():
            text = textF.save(commit=False)
            text.creator = schmog
            text.dataset = dataset
            text.column = table.getColumns().get(type=textType)
            text.save()

        numF = DataNumericForm({"created": datetime.now(), "content": LiteralFactory.genRandNumber()})
        if numF.is_valid():
            num = numF.save(commit=False)
            num.creator = schmog
            num.dataset = dataset
            num.column = table.getColumns().get(type=numType)
            num.save()

        dateF = DataDateForm({"created": datetime.now(), "content": datetime.now()})
        if dateF.is_valid():
            date = dateF.save(commit=False)
            date.creator = schmog
            date.dataset = dataset
            date.column = table.getColumns().get(type=dateType)
            date.save()

        selF = DataSelectionForm({"created": datetime.now(), "content": LiteralFactory.genRandString()})
        if selF.is_valid():
            sel = selF.save(commit=False)
            sel.creator = schmog
            sel.dataset = dataset
            sel.column = table.getColumns().get(type=selType)
            sel.save()

        boolF = DataBoolForm({"created": datetime.now(), "content": True})
        if boolF.is_valid():
            bool = boolF.save(commit=False)
            bool.creator = schmog
            bool.dataset = dataset
            bool.column = table.getColumns().get(type=boolType)
            bool.save()

        result = DatasetSerializer.serializeOne(dataset.datasetID, schmog)
        self.assertEquals(dataset.datasetID, result["id"])
        for item in result["data"]:
            if item["type"] == Type.TEXT:
                self.assertEquals(text.content, item["value"])
            if item["type"] == Type.NUMERIC:
                self.assertEquals(num.content, float(item["value"]))
            if item["type"] == Type.DATE:
                self.assertEquals(date.content.strftime('%Y-%m-%d, %H:%M'), item["value"])
            if item["type"] == Type.SELECTION:
                self.assertEquals(sel.content, item["value"])
            if item["type"] == Type.BOOL:
                self.assertEquals(bool.content, item["value"])

    def test_serializeAll(self):
        schmog = UserFactory.createRandomUser("test")
        table = StructureFactory.createTable(schmog)

        datasetList = list()
        for i in range(0, 6):
            datasetF = DatasetForm({"created": datetime.now()})
            if datasetF.is_valid():
                dataset = datasetF.save(commit=False)
                dataset.table = table
                dataset.creator = schmog
                dataset.save()
                dataset.datasetID = table.generateDatasetID(dataset)
                dataset.save()
                datasetList.append(dataset)

        textType = Type.objects.get(type=Type.TEXT)
        numType = Type.objects.get(type=Type.NUMERIC)
        dateType = Type.objects.get(type=Type.DATE)
        selType = Type.objects.get(type=Type.SELECTION)
        boolType = Type.objects.get(type=Type.BOOL)

        textCol = table.getColumns().get(type=textType)
        numCol = table.getColumns().get(type=numType)
        dateCol = table.getColumns().get(type=dateType)
        selCol = table.getColumns().get(type=selType)
        boolCol = table.getColumns().get(type=boolType)

        # 4 datasets have each another type missing
        for i in range(0, 5):
            if i != Type.TEXT:
                textF = DataTextForm({"created": datetime.now(), "content": LiteralFactory.genRandString()})
                if textF.is_valid():
                    text = textF.save(commit=False)
                    text.creator = schmog
                    text.dataset = datasetList[i]
                    text.column = table.getColumns().get(type=textType)
                    text.save()
            if i != Type.NUMERIC:
                numF = DataNumericForm({"created": datetime.now(), "content": LiteralFactory.genRandNumber()})
                if numF.is_valid():
                    num = numF.save(commit=False)
                    num.creator = schmog
                    num.dataset = datasetList[i]
                    num.column = table.getColumns().get(type=numType)
                    num.save()

            if i != Type.DATE:
                dateF = DataDateForm({"created": datetime.now(), "content": datetime.now()})
                if dateF.is_valid():
                    date = dateF.save(commit=False)
                    date.creator = schmog
                    date.dataset = datasetList[i]
                    date.column = table.getColumns().get(type=dateType)
                    date.save()
            if i != Type.SELECTION:
                selF = DataSelectionForm({"created": datetime.now(), "content": LiteralFactory.genRandString()})
                if selF.is_valid():
                    sel = selF.save(commit=False)
                    sel.creator = schmog
                    sel.dataset = datasetList[i]
                    sel.column = table.getColumns().get(type=selType)
                    sel.save()

            if i != Type.BOOL:
                boolF = DataBoolForm({"created": datetime.now(), "content": True})
                if boolF.is_valid():
                    bool = boolF.save(commit=False)
                    bool.creator = schmog
                    bool.dataset = datasetList[i]
                    bool.column = table.getColumns().get(type=boolType)
                    bool.save()

        # the last one has all data elements
        textF = DataTextForm({"created": datetime.now(), "content": LiteralFactory.genRandString()})
        if textF.is_valid():
            text = textF.save(commit=False)
            text.creator = schmog
            text.dataset = datasetList[5]
            text.column = table.getColumns().get(type=textType)
            text.save()

        numF = DataNumericForm({"created": datetime.now(), "content": LiteralFactory.genRandNumber()})
        if numF.is_valid():
            num = numF.save(commit=False)
            num.creator = schmog
            num.dataset = datasetList[5]
            num.column = table.getColumns().get(type=numType)
            num.save()

        dateF = DataDateForm({"created": datetime.now(), "content": datetime.now()})
        if dateF.is_valid():
            date = dateF.save(commit=False)
            date.creator = schmog
            date.dataset = datasetList[5]
            date.column = table.getColumns().get(type=dateType)
            date.save()

        selF = DataSelectionForm({"created": datetime.now(), "content": LiteralFactory.genRandString()})
        if selF.is_valid():
            sel = selF.save(commit=False)
            sel.creator = schmog
            sel.dataset = datasetList[5]
            sel.column = table.getColumns().get(type=selType)
            sel.save()

        boolF = DataBoolForm({"created": datetime.now(), "content": True})
        if boolF.is_valid():
            bool = boolF.save(commit=False)
            bool.creator = schmog
            bool.dataset = datasetList[5]
            bool.column = table.getColumns().get(type=boolType)
            bool.save()

        result = DatasetSerializer.serializeAll(table, schmog)

        # test if all dataset ids are listed and no duplicates exist
        datasetIDs = list()
        for dataset in Dataset.objects.all():
            datasetIDs.append(dataset.datasetID)

        returnedIDs = [dataset["id"] for dataset in result["datasets"]]
        self.assertEquals(datasetIDs, returnedIDs)

        # test if data elements are in the correct columns and datasets
        for resultDataset in result["datasets"]:
            for item in resultDataset["data"]:
                if item["type"] == Type.TEXT:
                    field = DataText.objects.get(content=item["value"])
                    self.assertEquals(field.dataset.datasetID, resultDataset["id"])
                    self.assertEquals(textCol.name, item["column"])
                if item["type"] == Type.NUMERIC:
                    field = DataNumeric.objects.get(content=item["value"])
                    self.assertEquals(field.dataset.datasetID, resultDataset["id"])
                    self.assertEquals(numCol.name, item["column"])
                if item["type"] == Type.DATE:
                    field = DataDate.objects.get(content=item["value"])
                    self.assertEquals(field.dataset.datasetID, resultDataset["id"])
                    self.assertEquals(dateCol.name, item["column"])
                if item["type"] == Type.SELECTION:
                    field = DataSelection.objects.get(content=item["value"])
                    self.assertEquals(field.dataset.datasetID, resultDataset["id"])
                    self.assertEquals(selCol.name, item["column"])
                if item["type"] == Type.BOOL:
                    field = DataBool.objects.get(content=item["value"])
                    self.assertEquals(field.dataset.datasetID, resultDataset["id"])
                    self.assertEquals(boolCol.name, item["column"])