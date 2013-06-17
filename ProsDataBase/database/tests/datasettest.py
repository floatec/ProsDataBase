from factory import *
from database.views.api import *
from django.test import TestCase
from django.test.client import *

class DataSetTest(TestCase):
    def test_dataSet(self):
        user = create_RandomUser()

        table1 = create_table(user)

        column1 = create_columns(table1, user)

        connect_User_With_Rights(user, table1)

        result = TableSerializer.serializeOne(table1.name, user)

        print result
