import unittest
from app import app, do_login, do_logout
from models import db, User,  Saved

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///sporky_test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False

app.config['WTF_CSRF_ENABLED'] = False

class SporkyTestCase(unittest.TestCase):
    """Test views and functionality of Sporky Flask app"""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(
            username="testuser",
            password="testuser",
            email="test@test.com",
            image_url=None
        )
        self.testuser_id = 1234
        self.testuser.id = self.testuser_id

        db.session.commit()

    def tearDown(self):
        """Clean up fouled transactions"""

        db.session.rollback()

    def test_login_logout(self):
        """Test user login/logout"""

        with self.client as c:
            # test login
            resp = c.post('/login',
                          data={'username': 'testuser',
                                'password': 'testuser'},
                          follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Hello, testuser!', html)

            # test logout
            resp = c.get('/logout', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Goodbye, testuser!', html)

    def test_signup(self):
        """Test user signup"""

        with self.client as c:
            resp = c.post('/signup',
                          data={'username': 'testuser2',
                                'password': 'testuser2',
                                'email': 'test2@test.com'},
                          follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Hello, testuser2!', html)

    def test_save_recipe(self):
        """Test saving a recipe"""

        with self.client as c:
            # login user
            do_login(self.testuser)

            # test saving a recipe
            resp = c.post('/save_recipe/12345',
                          data={'used': 'Test',
                                'rating': 5,
                                'notes': 'Test'},
                          follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Recipe saved', html)

            # test trying to save the same recipe again
            resp = c.post('/save_recipe/12345',
                          data={'used': 'Test',
                                'rating': 5,
                                'notes': 'Test'},
                          follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Recipe already saved', html)

    def test_show_favorites(self):
        """Test showing saved recipes"""

        with self.client as c:
            # login user
            do_login(self.testuser)

            # add saved recipe
            saved_recipe = Saved(user_id=self.testuser.id, recipe_id=1)
            db.session.add(saved_recipe)
            db.session.commit()

            # get saved recipes
            response = c.get('/favorites')

            # check response status code
            self.assertEqual(response.status_code, 200)

            # check saved recipe is displayed
            self.assertIn('My Favorite Recipe', response.data.decode('utf-8'))