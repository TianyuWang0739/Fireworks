import os
from rango.models import Category, Page
from django.urls import reverse
from django.test import TestCase
from django.conf import settings


FAILURE_HEADER = f"{os.linesep}{os.linesep}{os.linesep}================{os.linesep}Fireworks TEST FAILURE =({os.linesep}================{os.linesep}"
FAILURE_FOOTER = f"{os.linesep}"
f"{FAILURE_HEADER} {FAILURE_FOOTER}"


class FireworksViewTests(TestCase):

    def test_index_view(self):
        """
        Checks that the index view doesn't contain any presentational logic for showing the number of visits.
        This should be removed in the final exercise.
        """
        response = self.client.get(reverse('rango:index'))
        content = response.content.decode()

        self.assertTrue('visits:' not in content.lower())


class FireworksDatabaseConfigurationTests(TestCase):

    def setUp(self):
        pass
    
    def does_gitignore_include_database(self, path):
        """
        Takes the path to a .gitignore file, and checks to see whether the db.sqlite3 database is present in that file.
        """
        f = open(path, 'r')
        
        for line in f:
            line = line.strip()
            
            if line.startswith('db.sqlite3'):
                return True
        
        f.close()
        return False
    
    def test_databases_variable_exists(self):
        """
        Does the DATABASES settings variable exist, and does it have a default configuration?
        """
        self.assertTrue(settings.DATABASES)
        self.assertTrue('default' in settings.DATABASES)
    
    


class FireworksModelTests(TestCase):
    """
    Are the models set up correctly, and do all the required attributes (post exercises) exist?
    """
    def setUp(self):
        category_py = Category.objects.get_or_create(name='Python', views=123, likes=55)
        Category.objects.get_or_create(name='Django', views=187, likes=90)
        
        Page.objects.get_or_create(category=category_py[0],
                                   title='Tango with Django',
                                   url='https://www.tangowithdjango.com',
                                   views=156)
    
    def test_category_model(self):
        """
        Runs a series of tests on the Category model.
        Do the correct attributes exist?
        """
        category_py = Category.objects.get(name='Python')
        self.assertEqual(category_py.views, 123)
        self.assertEqual(category_py.likes, 55)
        
        category_dj = Category.objects.get(name='Django')
        self.assertEqual(category_dj.views, 187)
        self.assertEqual(category_dj.likes, 90)
    
    


class FireworksPopulationScriptTests(TestCase):

    def setUp(self):
        """
        Imports and runs the population script, calling the populate() method.
        """
        try:
            import populate_rango
        except ImportError:
            raise ImportError(f"{FAILURE_HEADER}The tests could not import the populate_rango. Check it's in the right location (the first tango_with_django_project directory).{FAILURE_FOOTER}")
        
        if 'populate' not in dir(populate_rango):
            raise NameError(f"{FAILURE_HEADER}The populate() function does not exist in the populate_rango module. This is required.{FAILURE_FOOTER}")
        

        populate_rango.populate()
    
    def test_categories(self):
        """
        There should be three categories from populate_rango -- Python, Django and Other Frameworks.
        """
        categories = Category.objects.filter()
        categories_len = len(categories)
        categories_strs = map(str, categories)
        
        self.assertEqual(categories_len, 3)
        self.assertTrue('Python' in categories_strs)
        self.assertTrue('Django' in categories_strs)
        self.assertTrue('Other Frameworks' in categories_strs)
    

    def test_counts(self):
        """
        Tests whether each category's likes and views values are the values that are stated in the book.
        Pukes when a value doesn't match.
        """
        details = {'Python': {'views': 128, 'likes': 64},
                   'Django': {'views': 64, 'likes': 32},
                   'Other Frameworks': {'views': 32, 'likes': 16}}
        
        for category in details:
            values = details[category]
            category = Category.objects.get(name=category)
            self.assertEqual(category.views, values['views'])
            self.assertEqual(category.likes, values['likes'])
    
    def check_category_pages(self, category, page_titles):
        """
        Performs a number of tests on the database regarding pages for a given category.
        Do all the included pages in the population script exist?
        The expected page list is passed as page_titles. The name of the category is passed as category.
        """
        category = Category.objects.get(name=category)
        pages = Page.objects.filter(category=category)
        pages_len = len(pages)
        page_titles_len = len(page_titles)
        
        self.assertEqual(pages_len, len(page_titles))
        
        for title in page_titles:
            try:
                page = Page.objects.get(title=title)
            except Page.DoesNotExist:
                raise ValueError(f"{FAILURE_HEADER}The page '{title}' belonging to category '{category}' was not found in the database produced by populate_rango.{FAILURE_FOOTER}")
            
            self.assertEqual(page.category, category)


class FireworksConfigurationTests(TestCase):
    """
    Tests the configuration of the Django project -- can cookies be used, at least on the server-side?
    """
    def test_middleware_present(self):
        """
        Tests to see if the SessionMiddleware is present in the project configuration.
        """
        self.assertTrue('django.contrib.sessions.middleware.SessionMiddleware' in settings.MIDDLEWARE)
    
    def test_session_app_present(self):
        """
        Tests to see if the sessions app is present.
        """
        self.assertTrue('django.contrib.sessions' in settings.INSTALLED_APPS)