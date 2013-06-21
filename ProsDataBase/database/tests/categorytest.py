from django.test import TestCase
from factory import *
from ..views.api import *
from django.test.client import Client


class CategoryTest(TestCase):

    def test_TableSerializer_SerializeCategories(self):
        # return empty result if no category exists
        serial = TableSerializer.serializeCategories()
        self.assertTrue("categories" in serial)
        self.assertTrue(len(serial["categories"]) == 0)

        # serialize all categories, check if no phantom category appears, no category misses
        names = list()
        for i in range(0, 10):
            catF = CategoryForm({"name": LiteralFactory.genRandString()})
            cat = catF.save()
            names.append(cat.name)

        serial = TableSerializer.serializeCategories()
        self.assertTrue("categories" in serial)
        self.assertEquals(names, serial["categories"])

    def test_modifyCategories(self):
        # create categories
        reqBody = dict()
        reqBody["categories"] = list()
        for i in range(0, 10):
            reqBody["categories"].append({"new": LiteralFactory.genRandString()})

        tablefactory.modifyCategories(reqBody)

        categoryNames = list()
        for category in Category.objects.all():
            categoryNames.append(category.name)

        self.assertEquals(categoryNames, [category["new"] for category in reqBody["categories"]])

        # change category names
        reqBody = dict()
        reqBody["categories"] = list()
        for catName in categoryNames:
            reqBody["categories"].append({"old": catName, "new": LiteralFactory.genRandString()})

        tablefactory.modifyCategories(reqBody)

        categoryNames = list()
        for category in Category.objects.all():
            categoryNames.append(category.name)

        tablefactory.modifyCategories(reqBody)
        self.assertEquals(categoryNames, [cat["new"] for cat in reqBody["categories"]])

    def test_showCategories(self):
        # show all categories, check if no phantom category appears, no category misses
        names = list()
        for i in range(0, 10):
            catF = CategoryForm({"name": LiteralFactory.genRandString()})
            cat = catF.save()
            names.append(cat.name)

        response = showCategories()
        self.assertTrue("categories" in json.loads(response.content))
        self.assertEquals(names, json.loads(response.content)["categories"])

    def test_categories(self):
        # test PUT request
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

        # test GET request
        response = c.get(path='/api/category/')
        self.assertEquals(categoryNames, [category for category in json.loads(response.content)["categories"]])