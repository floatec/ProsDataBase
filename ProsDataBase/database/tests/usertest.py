from django.test import TestCase
from database.models import *
from database.tests.factory import *
from database.views.api import *

class UserTest(TestCase):
    def test_showAllUser(self):
        listofuser = create_User(101)
        listofuser2 = create_User(101)

        result = UserSerializer.serializeAll()

        # ===================================================
        # tests the count of the users
        # ===================================================
        length = 0
        for user in result["users"]:
            length += 1
        self.assertEquals(length, 200)

        # ===================================================
        # test the users are in the result
        # ===================================================
        for user in listofuser:
            self.assertTrue(user.username in result["users"])

        for user in listofuser2:
            self.assertTrue(user.username in result["users"])

    # DER SCHEISS GEHT NEEED
    def test_showOneUser(self):
        users = create_User(2)

        result = UserSerializer.serializeOne(user)

        print users