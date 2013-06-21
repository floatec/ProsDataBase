from django.test import TestCase
from factory import *
from ..views.api import *
from django.test.client import Client


class CategoryTest(TestCase):

    def test_categories(self):
        # test if multiple categories can be created with categories()
        user = UserFactory.createRandomUser(password="test")
        c = Client()
        c.login(username=user.username, password="test")

        reqBody = dict()
        reqBody["categories"] = list()
        for i in range(0, 10):
            reqBody["categories"].append({"new": LiteralFactory.genRandString()})

        c.put(path='/api/category/', data=json.dumps(reqBody), content_type="application/json")

        categoryNames = list()
        for category in Category.objects.all():
            categoryNames.append(category.name)

        self.assertEquals(categoryNames, [category["new"] for category in reqBody["categories"]])

        # test if categories can be changed with modifyCategories()
