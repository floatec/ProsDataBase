from django.test import TestCase
from database.models import *
from database.tests.factory import *
from database.tablefactory import deleteTable
from database.views.api import login
from django.contrib import auth


class TableTest(TestCase):
    # !!!!!! TABELLENNAME WIRD NICHT GEFUNDEN UND DIE COLUMNS WERDEN NICHT GEFUNDEN
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

        column1 = create_columns(table1, schmog)
        column2 = create_columns(table2, schmog)

        connect_User_With_Rights(schmog,table1)
        connect_User_With_Rights(schmog,table2)

        result =  TableSerializer.serializeAll(schmog)

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
        self.assertTrue(table1.name in [table["name"] for table in result["tables"]])
        self.assertTrue(table2.name in [table["name"] for table in result["tables"]])

        # =================================================================
        # tests the number of columns in the table
        # =================================================================
        for array in [table["columns"] for table in result["tables"]]:
            length += len(array)

        #self.assertEquals(length, 10)
        print result

    # !!!!!! TABELLENNAME WIRD NICHT GEFUNDEN
    def test_showTable(self):
        # =================================================================
        #return the table with specified name, along with its columns and datasets.
        # {
        #     "name": "example",
        #     "datasets": [
        #         {"id": 38, "data": [ {"column": "id", "type": 1, "value": 0}, "column": "columnname", "type": 0, "value": "aString"}, {"column": "anothercolumn", "type": 5, "value": [1, 2], "table": "aTableName"} ]},  //row 1
        #         {"id": 18, "data": [ {"column": "id", "type": 1, "value": 17}, "column": "columnname", "type": 0, "value": "aString"}, {"column": "anothercolumn", "type": 5, "value": [13, 14], "table": "aTableName"} ]}   //row 2
        #     ]
        # }
        # =================================================================


        user = create_RandomUser()

        table1 = create_table(user)

        column1 = create_columns(table1, user)

        connect_User_With_Rights(user, table1)

        result = TableSerializer.serializeOne(table1.name,user)

        table1Cols = list()
        for col in table1.getColumns():
            table1Cols.append(col.name)

        self.assertEquals(table1.name, result["name"])

        print result

    # SOLLTE SO EIGENTLICH KLAPPEN
    def test_deleteTable(self):

        user = create_RandomUser()


        table1 = create_table(user)

        column1 = create_columns(table1, user)

        connect_User_With_Rights(user, table1)

        result = TableSerializer.serializeAll(user)

        #deleteTable(table1.name,user)
        # ==============================================================
        # tests the table is flaged as deleted
        # ==============================================================
        #self.assertTrue(table1.deleted)
        #print result

        print user