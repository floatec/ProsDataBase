from django.test import TestCase
from ..models import *
from ..tests.factory import *
from ..views.api import *

class UserTest(TestCase):
    def test_showAllUser(self):
        listofuser = list()
        listofuser2 = list()

        for i in range(1,101):
            listofuser.append(UserFactory.createRandomUser())
            listofuser2.append(UserFactory.createRandomUser())

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

    # Jetzt passts
    def test_showOneUser(self):
        user1 = UserFactory.createRandomUser()
        user2 = UserFactory.createRandomUser()
        user2.tableCreator=True
        user2.admin=True
        user2.userManager=True
        user2.is_active = False


        result = UserSerializer.serializeOne(user1.username)
        result2 = UserSerializer.serializeOne(user2.username)

        print result
        print result2

        # ===================================================
        # test the user have the same name in the result
        # ===================================================
        self.assertTrue(user1.username in result["name"])
        self.assertTrue(user1.is_active)
        self.assertTrue(user1.tableCreator)
        self.assertFalse(user1.admin)
        self.assertFalse(user1.userManager)

        self.assertTrue(user2.username in result2["name"])
        self.assertFalse(user2.is_active)
        self.assertTrue(user2.tableCreator)
        self.assertTrue(user2.admin)
        self.assertTrue(user2.userManager)

    # User der keine createTable-Rechte hat kann eine Tabelle erstellen
    def test_showUserRights(self):
        user1 = UserFactory.createUserWithName("Gunther", "abc")

        user2 = UserFactory.createUserWithName("Mammut", "abx")

        table = StructureFactory.createTable(user1)

        UserFactory.createTableRights(user1,table)
        UserFactory.createTableRights(user2,table)

        result = UserSerializer.serializeAllWithRights(user1)

        print result

        # ================================================================
        # tests the name of the users
        # ================================================================
        self.assertTrue(user1.username in [user["name"] for user in result["users"]])
        self.assertTrue(user2.username in [user["name"] for user in result["users"]])

        # ================================================================
        # tests the userright is given to the right user
        # ================================================================
        for user in result["users"]:
            if user["name"] == user1.username:
                self.assertFalse(user["tableCreator"])
                self.assertTrue(user["active"])
                self.assertFalse(user["admin"])
                self.assertFalse(user["userManager"])
            elif user["name"] == user2.username:
                self.assertFalse(user["tableCreator"])
                self.assertTrue(user["active"])
                self.assertFalse(user["admin"])
                self.assertFalse(user["userManager"])

    def test_login(self):
        serial = UserSerializer.serializeAll()
        self.assertTrue("users" in serial)
        self.assertEquals(len(serial["users"]), 0)

        usernames = list()
        for i in range(0,10):
            userF = UserFactory.createUserWithName("tim", "abc")
            user = userF.save()
            usernames.append(user.username)

        response = showAllUsers()
        self.asserTrue("users" in json.loads(response.content))
        self.assertEquals(usernames, json.loads(response.content["users"]))