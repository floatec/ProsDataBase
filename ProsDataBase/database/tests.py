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
        # =================================================================
        # if a user is in a group the test goes right
        # =================================================================
        group = create_Group()

        self.assertTrue(group.users.get(username = 1))
        self.assertTrue(group.users.get(username = 50))
        self.assertTrue(group.users.get(username = 100))
        self.assertTrue(group.users.get(username = 1001))

        with self.assertRaises(DBUser.DoesNotExist):
            group.users.get(username=1001)
            group.users.get(username=-100)
            group.users.get(username=0)


    def test_showAllGroups(self):
        # =================================================================
        # return all groups
        # =================================================================
        self.maxDiff = None
        group1 = create_Group()
        group2 = create_Group()

        result = GroupSerializer.serializeAll()

        groupMembers1 = list()
        for m1 in Membership.objects.filter(group=group1):
            groupMembers1.append(m1.user.username)

        groupMembers2 = list()
        for m2 in Membership.objects.filter(group=group2):
            groupMembers2.append(m2.user.username)

        # =================================================================
        # test the name of the group is the same groupname in the result
        # =================================================================
        self.assertTrue(group1.name in [group["name"] for group in result["groups"]])
        self.assertTrue(group2.name in [group["name"] for group in result["groups"]])

        # =================================================================
        # test the users in the group are the same users in the result
        # =================================================================
        for group in result["groups"]:
            if group["name"] == group1.name:
                self.assertEquals(groupMembers1, group["users"])
                break
            elif group["name"] == group2.name:
                self.assertEquals(groupMembers2, group["users"])





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
        self.assertEqual(16, length)

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