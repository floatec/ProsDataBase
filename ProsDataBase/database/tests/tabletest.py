import json
from django.test.client import Client
from django.test import TestCase
from ..tests.factory import *
from ..tablefactory import deleteTable


class TableTest(TestCase):
    # Mittlerweile passt alles
    def test_serializeAll(self):
        # =================================================================
        # test serializer TableSerializer serializeAll()
        # {
        #     "tables": [
        #         {"name": "example", "columns": ["columname","anothercolum"]},
        #         {"name": "2nd", "columns": ["columname","anothercolum"]}
        #     ]
        # }
        # =================================================================

        schmog = UserFactory.createRandomUser()

        table1 = StructureFactory.createTable(schmog)
        table2 = StructureFactory.createTable(schmog)

        DataFactory.genRandDatasets(table1, schmog, 10)
        DataFactory.genRandDatasets(table2, schmog, 10)

        UserFactory.createTableRights(schmog, table1)
        UserFactory.createTableRights(schmog, table2)

        for col in table1.getColumns():
            UserFactory.createColRights(schmog, col)
        for col in table2.getColumns():
            UserFactory.createColRights(schmog, col)

        result = TableSerializer.serializeAll(schmog)

        length = 0
        table1Cols = list()
        for col in table1.getColumns():
            table1Cols.append(col.name)

        table2Cols = list()
        for col in table2.getColumns():
            table2Cols.append(col.name)
        # =================================================================
        # tests the columns of the tables have the same name as the columns of the result
        # =================================================================
        for table in result["tables"]:
            if table["name"] == table1.name:
                obj = table
                self.assertEquals(table1Cols, obj["columns"])
            elif table["name"] == table2.name:
                obj = table
                self.assertEquals(table2Cols, obj["columns"])

        # =================================================================
        # tests the name of the table
        # =================================================================
        print [table["name"] for table in result["tables"]]
        self.assertTrue(table1.name in [table["name"] for table in result["tables"]])
        self.assertTrue(table2.name in [table["name"] for table in result["tables"]])

        # =================================================================
        # tests the number of columns in the table
        # =================================================================
        for array in [table["columns"] for table in result["tables"]]:
            length += len(array)

        self.assertEquals(length, 10)
        print result

    # Mittlerweile passt alles
    def test_serializeOne(self):

        user = UserFactory.createRandomUser()

        table1 = StructureFactory.createTable(user)

        DataFactory.genRandDatasets(table1, user)

        UserFactory.createTableRights(user, table1)
        for column in table1.getColumns():
            UserFactory.createColRights(user, column)
        result = TableSerializer.serializeOne(table1.name,user)
        print result
        table1Cols = list()
        for col in table1.getColumns():
            table1Cols.append(col.name)

        # ==============================================================
        # tests the name is the same name in the result
        # ==============================================================
        self.assertEquals(table1.name, result["name"])

        datasets = table1.getDatasets()
        for dataset in datasets:
            id = dataset.datasetID

        # ==============================================================
        # tests the datasets are always the same datasets in the result
        # ==============================================================
            for datasetObj in result["datasets"]:
                if datasetObj["id"] == id:
                    for data in dataset.getData():
                        for item in data:
                            self.assertTrue(item.column.name in [column["column"] for column in datasetObj["data"]])
                            for data in datasetObj["data"]:
                                if data["column"] == item.column.name:
                                    self.assertEquals(str(item.content), data["value"])
        print result

    def test_deleteTable(self):
        user = UserFactory.createRandomUser()
        table1 = StructureFactory.createTable(user)
        UserFactory.createTableRights(user, table1)
        deleteTable(table1.name, user)
        # ==============================================================
        # tests if the table is flagged as deleted
        # ==============================================================
        self.assertTrue(table1.deleted)

    def test_TableSerializerSerializeStructure(self):
        user = UserFactory.createRandomUser()
        table = StructureFactory.createTable(user)
        DataFactory.genRandDatasets(table, user)
        UserFactory.createTableRights(user, table)
        for column in table.getColumns():
            UserFactory.createColRights(user, column)
        result = TableSerializer.serializeStructure(table.name, user)

        print result


    def test_test(self):

        user = UserFactory.createRandomUser(password="test")
        c = Client()
        c.login(username=user.username, password="test")

        reqBody = dict()
        reqBody["tables"] = list()
        reqBody["columns"] = list()
        for i in range(0, 10):
            reqBody["tables"].append({"name": LiteralFactory.genRandString()})

        c.put(path='/api/category/', data=json.dumps(reqBody), content_type="application/json")

        categoryNames = list()
        for category in Category.objects.all():
            categoryNames.append(category.name)

        self.assertEquals(categoryNames, [category["new"] for category in reqBody["categories"]])
