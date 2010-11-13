from django.test.client import Client
from django.test import TestCase

class CustomcommentsBaseTestCase(TestCase):
    fixtures = ['../../aggregator/fixtures/test_data.json', ]



class CustomcommentsTestCase(CustomcommentsBaseTestCase):
    pass



    

