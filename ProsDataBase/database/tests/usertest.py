from django.test import TestCase
from database.models import *
from database.tests.factory import *
from database.views.api import *

class UserTest(TestCase):
    def test_showAllUser(self):

        group = create_Group()

        result = UserSerializer.serializeAll()

        print result