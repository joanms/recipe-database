# The tests are based on this video: https://www.youtube.com/watch?v=1aHNs1aEATg&list=PLLjmbh6XPGK4ISY747FUHXEl9lBxre4mM&index=8&t=0s
from app import app
import unittest

class FlaskTestCase(unittest.TestCase):

          def test_index(self):
                    tester = app.test_client(self)
                    response = tester.get('/', content_type='html/text')
                    self.assertEqual(response.status_code, 200)

          def test_add_recipe(self):
                    tester = app.test_client(self)
                    response = tester.get('/add_recipe', follow_redirects=True)
                    self.assertIn(b'Add Your Own Recipe', response.data)

          def test_insert_recipe(self):
                    tester = app.test_client(self)
                    response = tester.get('/insert_recipe', content_type='html/text')
                    self.assertEqual(response.status_code, 200)

          def test_list_recipes(self):
                    tester = app.test_client(self)
                    response = tester.get('/list_recipes', content_type='html/text')
                    self.assertEqual(response.status_code, 200)

          def test_login(self):
                    tester = app.test_client(self)
                    response = tester.get('/login', follow_redirects=True)
                    self.assertIn(b'Please Enter Your Username', response.data)

if  __name__ == '__main__':
          unittest.main()