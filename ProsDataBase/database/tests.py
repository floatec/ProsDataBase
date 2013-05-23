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
        group = create_Group()
        self.assertTrue(group.users.get(username = "hans"))
        self.assertTrue(group.users.get(username = "mark"))

