from django.test import TestCase
from database.models import *
from database.tests.factory import *
from database.views.api import *

class UserTest(TestCase):
    def test_showAllUser(self):

        group1 = create_Group()
        group2 = create_Group()
        result =  UserSerializer.serializeAll()

        listofUsers1 = list()
        for m1 in Membership.objects.filter(group=group1):
            listofUsers1.append(m1.user.username)

        listofUsers2 = list()
        for m2 in Membership.objects.filter(group=group2):
            listofUsers2.append(m2.user.username)

        if group["name"] == group1.name:
            self.assertEquals(listofUsers1, group["users"])
        elif group["name"] == group2.name:
            self.assertEquals(listofUsers2, group["users"])

        # ===================================================
        # tests the count of the users
        # ===================================================
        length = 0
        for user in result["users"]:
            length += 1
        self.assertEquals(length, 1000)

        # ===================================================
        # test the users are in the result
        # ===================================================