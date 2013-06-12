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

    # Jetzt passts
    def test_showOneUser(self):
        user1 = DBUser.objects.create_user(username="Spongebob")
        user2 = DBUser.objects.create_user(username="Patrick", tableCreator=True,admin=True,userManager=True)

        user1.save()
        user2.save()

        result = UserSerializer.serializeOne(user1.username)
        result2 = UserSerializer.serializeOne(user2.username)

        print result

        # ===================================================
        # test the user have the same name in the result
        # ===================================================
        self.assertTrue(user1.username in result["name"])
        self.assertTrue(user1.is_active)
        self.assertFalse(user1.tableCreator)
        self.assertFalse(user1.admin)
        self.assertFalse(user1.userManager)

        self.assertTrue(user2.username in result2["name"])
        self.assertTrue(user2.is_active)
        self.assertTrue(user2.tableCreator)
        self.assertTrue(user2.admin)
        self.assertTrue(user2.userManager)


    # User der keine createTable-Rechte hat kann eine Tabelle erstellen
    def test_showUserRights(self):
        user1 = DBUser.objects.create_user(username="Gunther", tableCreator=True)
        user1.save()

        user2 = DBUser.objects.create_user(username="Mammut")
        user2.save()

        table = create_table(user1)

        connect_User_With_Rights(user1,table)
        connect_User_With_Rights(user2,table)

        result = UserSerializer.serializeAllWithRights()

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
                self.assertTrue(user["tableCreator"])
                self.assertTrue(user["active"])
                self.assertFalse(user["admin"])
                self.assertFalse(user["userManager"])
            elif user["name"] == user2.username:
                self.assertFalse(user["tableCreator"])
                self.assertTrue(user["active"])
                self.assertFalse(user["admin"])
                self.assertFalse(user["userManager"])