from django.test import TestCase
from database.models import *
from database.tests.factory import *
from database.views.api import *


class TableTest(TestCase):
    def test_serializeAll(self):
        # =================================================================
        # test serializer TableSerializer serializeAll()
        #
        # {
        #     "tables": [
        #         {"name": "example", "columns": ["columname","anothercolum"]},
        #         {"name": "2nd", "columns": ["columname","anothercolum"]}
        #     ]
        # }
        # =================================================================
        schmog = DBUser.objects.create_user(username="test")
        schmog.save()

        table1 = create_table()
        table2 = create_table()
        result =  TableSerializer.serializeAll()
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

        self.assertEquals(length, 16)
        print result

    def test_serializeOne(self):
        # =================================================================
        #return the table with specified name, along with its columns and datasets.
        #
        # {
        #     "name": "example",
        #     "datasets": [
        #         {"id": 38, "data": [ {"column": "id", "type": 1, "value": 0}, "column": "columnname", "type": 0, "value": "aString"}, {"column": "anothercolumn", "type": 5, "value": [1, 2], "table": "aTableName"} ]},  //row 1
        #         {"id": 18, "data": [ {"column": "id", "type": 1, "value": 17}, "column": "columnname", "type": 0, "value": "aString"}, {"column": "anothercolumn", "type": 5, "value": [13, 14], "table": "aTableName"} ]}   //row 2
        #     ]
        # }
        # =================================================================
        table1 = create_table()
        result = TableSerializer.serializeOne(table1.name)

        table1Cols = list()
        for col in table1.getColumns():
            table1Cols.append(col.name)

        print result

        self.assertTrue(table1.name in [table["name"] in result["name"]])