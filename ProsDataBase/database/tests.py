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
    def test_table(self):
        """
        tests a table
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

        self.assertTrue(table1.name in [deinamudda["name"] for deinamudda in result["tables"]])
        self.assertTrue(table2.name in [deinamudda["name"] for deinamudda in result["tables"]])

        tablelist = result["tables"]
        namelist = []
        length = 0
        for table in tablelist:
            name = table["name"]
            namelist.append(name)
            length += len(table["columns"])

        self.assertTrue(table1.name in namelist)
        self.assertTrue(table2.name in namelist)


        #for list in [deinamudda["columns"] for deinamudda in result["tables"]]:
         #   length += len(list)
        #self.assertEquals(length, 16)

        self.assertEqual(16, length)
