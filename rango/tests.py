from django.test import TestCase

# Create your tests here.


class Test(TestCase):
    def get(self):
        self.client.post()