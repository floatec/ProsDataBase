from django.test import TestCase
from ..models import *
from ..tests.factory import *
from ..tablefactory import deleteTable
from ..views.api import login
from django.contrib import auth


class TableTest(TestCase):
    # Mittlerweile passt alles
    def test_showAllTables(self):
        # =================================================================
        # test serializer TableSerializer serializeAll()
        # {
        #     "tables": [
        #         {"name": "example", "columns": ["columname","anothercolum"]},
        #         {"name": "2nd", "columns": ["columname","anothercolum"]}
        #     ]
        # }
        # =================================================================

        schmog = create_RandomUser()

        table1 = create_table(schmog)
        table2 = create_table(schmog)


        column1 = create_columnsWithPatients(table1, schmog)
        column2 = create_columnsWithPatients(table2, schmog)

        connect_User_With_TableRights(schmog,table1)
        connect_User_With_TableRights(schmog,table2)

        for col in table1.getColumns():
            connect_User_With_ColumnRights(schmog,col)
        for col in table2.getColumns():
            connect_User_With_ColumnRights(schmog,col)

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
                obj =  table
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
    def test_showTable(self):

        user = create_RandomUser()

        table1 = create_table(user)

        column1 = create_columnsWithPatients(table1, user)

        connect_User_With_TableRights(user, table1)
        for column in table1.getColumns():
            connect_User_With_ColumnRights(user, column)
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

        user = create_RandomUser()

        table1 = create_table(user)

        column1 = create_columns(table1, user)

        connect_User_With_TableRights(user, table1)

        deleteTable(table1.name,user)
        # ==============================================================
        # tests the table is flaged as deleted
        # ==============================================================
        self.assertTrue(table1.deleted)

    def test_structerTest(self):

        user = create_RandomUser()
        table = create_table(user)
        column = create_columnsWithPatients(table, user)
        connect_User_With_TableRights(user,table)
        connect_User_With_ColumnRights(user, column)
        result = TableSerializer.serializeStructure(table.name, user)

        print result