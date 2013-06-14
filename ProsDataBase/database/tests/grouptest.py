from django.test import TestCase
from database.models import *
from database.tests.factory import *

# funzt bisher alles
class GroupTest(TestCase):

    def test_showAllGroups(self):
        # =================================================================
        # tests the api showAllGroups
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

        # =================================================================
        # test the quantity of the result is correct
        # =================================================================
        length = 0
        for array in [group["users"] for group in result["groups"]]:
            length += len(array)
        self.assertEquals(length, 2000)

        # =================================================================
        # test the tableCreator and groupCreator are False
        # =================================================================
        for group in result["groups"]:
            if group["name"] == group1.name:
                self.assertFalse(group["tableCreator"])
            elif group["name"] == group2.name:
                self.assertFalse(group["tableCreator"])

    def test_showOneGroup(self):

        group = create_Group()

        result = GroupSerializer.serializeOne(group)

        # =================================================================
        # tests the users in the result are the same users in the group
        # =================================================================
        groupMember = list()
        for m in Membership.objects.filter(group=group):
            groupMember.append((m.user.username))

        for user in groupMember:
            self.assertTrue(user in result["users"])

        # =================================================================
        # test the quantity of the result is correct
        # =================================================================
        self.assertEquals(len(result["users"]), 1000)