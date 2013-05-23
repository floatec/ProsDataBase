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

        self.assertTrue(group.users.get(username = "hans"))
        self.assertTrue(group.users.get(username = "mark"))

        with self.assertRaises(DBUser.DoesNotExist):
            group.users.get(username="hans")

    def test_table(self):
        """

        """
        table = create_table()