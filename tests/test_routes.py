"""
Inventory API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN

  While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_service.py:TestPetServer
"""

import os
import logging
import unittest

from unittest.mock import MagicMock, patch
from urllib.parse import quote_plus
from service import app, status
from service.models import db, init_db
from tests.factories import ItemFactory

# Disable all but critical errors during normal test run
# uncomment for debugging failing tests
logging.disable(logging.CRITICAL)

# DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')
DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/inventory"
CONTENT_TYPE_JSON = "application/json"


######################################################################
#  T E S T   C A S E S
######################################################################
class TestItemServer(unittest.TestCase):
    """Item Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        db.drop_all()  # clean up the last tests
        db.create_all()  # create new tables
        self.app = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def _create_items(self, count):
        """Factory method to create items in bulk"""
        items = []
        for _ in range(count):
            test_item = ItemFactory()
            resp = self.app.post(
                BASE_URL, json=test_item.serialize(), content_type=CONTENT_TYPE_JSON
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test item"
            )
            new_item = resp.get_json()
            test_item.id = new_item["id"]
            items.append(test_item)
        return items

    def test_index(self):
        """Test the Home Page"""
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn(b"Inventory Demo REST API Service", resp.data)    

    def test_get_item_list(self):
        """Get a list of Items"""
        self._create_items(5)
        resp = self.app.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)    

    def test_get_item(self):
        """Get a single Item"""
        # get the id of an item
        test_item = self._create_items(1)[0]
        resp = self.app.get(
            "/inventory/{}".format(test_item.id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], test_item.name)

    def test_get_item_not_found(self):
        """Get an Item thats not found"""
        resp = self.app.get("/inventory/0")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)    
  
    def test_create_item(self):
        """Create a new Item"""
        test_item = ItemFactory()
        logging.debug(test_item)
        resp = self.app.post(
            BASE_URL, json=test_item.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)
        # Check the data is correct
        new_item = resp.get_json()
        self.assertEqual(new_item["name"], test_item.name, "Names do not match")
        self.assertEqual(
            new_item["category"], test_item.category, "Categories do not match"
        )
        self.assertEqual(
            new_item["quantity"], test_item.quantity, "Quantity does not match"
        )
        self.assertEqual(
            new_item["condition"], test_item.condition.name, "Condition does not match"
        )
        # Check that the location header was correct
        resp = self.app.get(location, content_type=CONTENT_TYPE_JSON)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_item = resp.get_json()
        self.assertEqual(new_item["name"], test_item.name, "Names do not match")
        self.assertEqual(
            new_item["category"], test_item.category, "Categories do not match"
        )
        self.assertEqual(
            new_item["quantity"], test_item.quantity, "Quantity does not match"
        )
        self.assertEqual(
            new_item["condition"], test_item.condition.name, "Condition does not match"
        )

    def test_update_item(self):
        """Update an existing Item"""
        # create a item to update
        test_item = ItemFactory()
        resp = self.app.post(
            BASE_URL, json=test_item.serialize(), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the item
        new_item = resp.get_json()
        logging.debug(new_item)
        new_item["category"] = "unknown"
        resp = self.app.put(
            "/inventory/{}".format(new_item["id"]),
            json=new_item,
            content_type=CONTENT_TYPE_JSON,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_item = resp.get_json()
        self.assertEqual(updated_item["category"], "unknown")

    def test_delete_item(self):
        """Delete an Item"""
        test_item = self._create_items(1)[0]
        resp = self.app.delete(
            "{0}/{1}".format(BASE_URL, test_item.id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.app.get(
            "{0}/{1}".format(BASE_URL, test_item.id), content_type=CONTENT_TYPE_JSON
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


    ######################################################################
    # T E S T   E R R O R   H A N D L E R S
    ######################################################################

    def test_method_not_allowed(self):
        resp = self.app.put('/inventory')
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    @patch("service.models.Items.find_by_category")
    def test_server_error(self, server_error_mock):
        """Test a 500 Internal Server Error Handler"""
        server_error_mock.return_value = None  # code expects a list
        # Turn off testing to allow production behavior
        app.config["TESTING"] = False
        resp = self.app.get(BASE_URL, query_string="category=shirt")
        app.config["TESTING"] = True
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_create_item_no_content_type(self):
        """Create a Item with no content type"""
        resp = self.app.post(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)