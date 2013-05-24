"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from database.models import *
from factory import *

class GroupTest(TestCase):
    def test_user_exist(self):
        """
        testet ob ein user in einer Gruppe ist
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

class TableTest(TestCase):
    def test_table(self):
        """
        testet eine tabelle
        """

        table = create_table()
        self.assertTrue(table.getDataSets.all())