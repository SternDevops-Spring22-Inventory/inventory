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

# from unittest.mock import MagicMock, patch
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
        resp = self.app.get("/inventory")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

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
            new_item["available"], test_item.available, "Availability does not match"
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
            new_item["available"], test_item.available, "Availability does not match"
        )
        self.assertEqual(
            new_item["condition"], test_item.condition.name, "Condition does not match"
        )

  

