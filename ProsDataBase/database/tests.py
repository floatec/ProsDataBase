"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from database.models import *
import base64
import unittest
from django.test.client import Client

class DBUserTest(TestCase):
    def setUp(self):

        self.hans = DBUser.objects.create_user(username="hans")
        self.gunther = DBUser.objects.create_user(username="gunther")

    def test_user_existing(self):
        self.assertEqual(self.hans.get_username(),"hans")
        self.assertEqual(self.gunther.get_username(),"gunther")

class DBGroupTest(TestCase):
    def setUp(self):
        self.group1 = DBGroup(name="bambam")
        self.group1.save()
        self.group2 = DBGroup(name="kokojambo")
        self.group2.save()

        self.hans = DBUser.objects.create_user(username="hans")
        self.gunther = DBUser.objects.create_user(username="gunther")
        self.mark = DBUser.objects.create_user(username="mark")

        self.m1 = Membership(user=self.hans, group=self.group1)
        self.m1.save()
        self.m2 = Membership(user=self.gunther, group=self.group1)
        self.m2.save()
        self.m3 = Membership(user=self.mark, group=self.group2)
        self.m3.save()


    def test_group(self):

        self.assertEquals(self.group1.name, "bambam")
        self.assertEquals(self.m1.user, self.hans)

        self.assertTrue(self.group1.users.get(username = "hans"))
        self.assertTrue(self.group1.users.get(username = "gunther"))
        self.assertTrue(self.group2.users.get(username = "mark"))
