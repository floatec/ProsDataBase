"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from database.models import *
from database.factory import *
from database.serializers import *
from views.api import *


class GroupTest(TestCase):
    def test_user_exist(self):
        """
        if a user is in a group the test goes right
        """
        group = create_Group()

        self.assertTrue(group.users.get(username = 1))
        self.assertTrue(group.users.get(username = 50))
        self.assertTrue(group.users.get(username = 100))
        self.assertTrue(group.users.get(username = 1000))

        with self.assertRaises(DBUser.DoesNotExist):
            group.users.get(username=1001)
            group.users.get(username=-100)
            group.users.get(username=0)


    def test_showAllUsers(self):

        user = create_User()

class TableTest(TestCase):
    def test_serializeAll(self):
        """
        test serializer TableSerializer serializeAll()

        {
            "tables": [
                {"name": "example", "columns": ["columname","anothercolum"]},
                {"name": "2nd", "columns": ["columname","anothercolum"]}
            ]
        }
        """
        table1 = create_table()
        table2 = create_table()
        result =  TableSerializer.serializeAll()
        length = 0

        print result

        self.assertTrue(table1.name in [table["name"] for table in result["tables"]])
        self.assertTrue(table2.name in [table["name"] for table in result["tables"]])


        for list in [table["columns"] for table in result["tables"]]:
            length += len(list)
        self.assertEquals(length, 16)

        self.assertEqual(16, length)

    def test_serializeOne(self):
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
        table1 = create_table()
        result = TableSerializer.serializeOne(table1)

        print result

        self.assertEquals(table1.name,result["name"])
        self.assertEquals(table1.datasets, result["datasets"])