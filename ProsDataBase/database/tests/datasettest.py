from factory import *
from database.views.api import *
from django.test import TestCase
from django.test.client import *

class DataSetTest(TestCase):
    def test_dataSet(self):
        user = create_RandomUser()

        table1 = create_table(user)

        column1 = create_columns(table1, user)

        datasets = table1.getDatasets()

        connect_User_With_Rights(user, table1)

        for dataset in datasets:
            result = DatasetSerializer.serializeOne(dataset.datasetID, user)

            print result
