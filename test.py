# The tests are based on this video: https://www.youtube.com/watch?v=1aHNs1aEATg&list=PLLjmbh6XPGK4ISY747FUHXEl9lBxre4mM&index=8&t=0s
from app import app
import unittest

class FlaskTestCase(unittest.TestCase):

          # Ensure that Flask was set up correctly
          def test_index(self):
                    tester = app.test_client(self)
                    response = tester.get('/', content_type='html/text')
                    self.assertEqual(response.status_code, 200)
          
          def test_list_recipes(self):
                    tester = app.test_client(self)
                    response = tester.get('/list_recipes', content_type='html/text')
                    self.assertEqual(response.status_code, 200)

          def test_login(self):
                    tester = app.test_client(self)
                    response = tester.get('/login', content_type='html/text')
                    self.assertEqual(response.status_code, 200)

          
if  __name__ == '__main__':
          unittest.main()