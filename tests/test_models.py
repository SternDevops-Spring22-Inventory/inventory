"""
Test cases for Item Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_pets.py:TestPetModel

"""
import os
import logging
import unittest
from werkzeug.exceptions import NotFound
from service.models import Items, Condition, DataValidationError, db
from service import app
from tests.factories import ItemFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  I T E M   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestItemModel(unittest.TestCase):
    """Test Cases for Item Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Items.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.drop_all()  # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()
        db.drop_all()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_item(self):
        """Create an item and assert that it exists"""
        item = Items(name="blue shirt", category="shirt", quantity=2, condition=Condition.NEW)
        self.assertTrue(item is not None)
        self.assertEqual(item.id, None)
        self.assertEqual(item.name, "blue shirt")
        self.assertEqual(item.category, "shirt")
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.condition, Condition.NEW)
        item = Items(name="blue shirt", category="shirt", quantity=2, condition=Condition.USED)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.condition, Condition.USED)

    def test_add_an_item(self):
        """Create an item and add it to the database"""
        items = Items.all()
        self.assertEqual(items, [])
        item = Items(name="blue shirt", category="shirt", quantity=2, condition=Condition.NEW)
        self.assertTrue(item is not None)
        self.assertEqual(item.id, None)
        item.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(item.id, 1)
        items = Items.all()
        self.assertEqual(len(items), 1)

    def test_read_a_item(self):
        """Read an Item"""
        item = ItemFactory()
        logging.debug(item)
        item.create()
        self.assertEqual(item.id, 1)
        # Fetch it back
        found_item = Items.find(item.id)
        self.assertEqual(found_item.id, item.id)
        self.assertEqual(found_item.name, item.name)
        self.assertEqual(found_item.category, item.category)
        self.assertEqual(found_item.quantity, item.quantity)
        self.assertEqual(found_item.condition, item.condition)

    def test_delete_a_item(self):
        """Delete an Item"""
        item = ItemFactory()
        item.create()
        self.assertEqual(len(Items.all()), 1)
        # delete the item and make sure it isn't in the database
        item.delete()
        self.assertEqual(len(Items.all()), 0)

    def test_serialize_an_item(self):
        """Test serialization of an Item"""
        item = ItemFactory()
        data = item.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], item.id)
        self.assertIn("name", data)
        self.assertEqual(data["name"], item.name)
        self.assertIn("category", data)
        self.assertEqual(data["category"], item.category)
        self.assertIn("quantity", data)
        self.assertEqual(data["quantity"], item.quantity)
        self.assertIn("condition", data)
        self.assertEqual(data["condition"], item.condition.name)

    def test_deserialize_an_item(self):
        """Test deserialization of an Item"""
        data = {
            "id": 1,
            "name": "Blue shirt",
            "category": "shirt",
            "quantity": 2,
            "condition": "NEW",
        }
        item = Items()
        item.deserialize(data)
        self.assertNotEqual(item, None)
        self.assertEqual(item.id, None)
        self.assertEqual(item.name, "Blue shirt")
        self.assertEqual(item.category, "shirt")
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.condition, Condition.NEW)


    def test_deserialize_missing_data(self):
        """Test deserialization of an Item with missing data"""
        data = {"id": 1, "name": "white socks", "category": "socks"}
        item = Items()
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_deserialize_bad_data(self):
        """Test deserialization of bad data"""
        data = "this is not a dictionary"
        item = Items()
        self.assertRaises(DataValidationError, item.deserialize, data)  

    def test_deserialize_bad_quantity(self):
        """Test deserialization of bad quantity attribute"""
        test_item = ItemFactory()
        data = test_item.serialize()
        data["quantity"] = "5"
        item = Items()
        self.assertRaises(DataValidationError, item.deserialize, data)           

    def test_deserialize_bad_condition(self):
        """Test deserialization of bad condition attribute"""
        test_item = ItemFactory()
        data = test_item.serialize()
        data["condition"] = "new"  # wrong case
        item = Items()
        self.assertRaises(DataValidationError, item.deserialize, data)

    def test_update_a_item(self):
        """Update an Item"""
        item = ItemFactory()
        logging.debug(item)
        item.create()
        logging.debug(item)
        self.assertEqual(item.id, 1)
        # Change it an save it
        item.category = "shirt"
        original_id = item.id
        item.update()
        self.assertEqual(item.id, original_id)
        self.assertEqual(item.category, "shirt")
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        items = Items.all()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].id, 1)
        self.assertEqual(items[0].category, "shirt")

    def test_find_by_name(self):
        """Find an Item by Name"""
        Items(name="blueShirt", category="shirt", quantity=10).create()
        Items(name="blackPants", category="pants", quantity=5).create()
        search_item = Items.find_by_name("blueShirt")
        self.assertEqual(search_item[0].category, "shirt")
        self.assertEqual(search_item[0].name, "blueShirt")
        self.assertEqual(search_item[0].quantity, 10)

    def test_find_by_category(self):
        """Find Items by Category"""
        Items(name="blue shirt", category="shirt", quantity=5).create()
        Items(name="white socks", category="socks", quantity=0).create()
        items = Items.find_by_category("socks")
        self.assertEqual(items[0].category, "socks")
        self.assertEqual(items[0].name, "white socks")
        self.assertEqual(items[0].quantity, 0)

