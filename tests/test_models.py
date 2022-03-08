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
        logging.info('WHOA HERE WE GO STARTING THE CREATE TEST')
        item = Items(name="Blue shirt", category="shirt", available=True, condition=Condition.NEW)
        self.assertTrue(item is not None)
        self.assertEqual(item.id, None)
        self.assertEqual(item.name, "Blue shirt")
        self.assertEqual(item.category, "shirt")
        self.assertEqual(item.available, True)
        self.assertEqual(item.condition, Condition.NEW)
        item = Items(name="Blue shirt", category="shirt", available=False, condition=Condition.USED)
        self.assertEqual(item.available, False)
        self.assertEqual(item.condition, Condition.USED)
        logging.info('Damn that was fast...')

    def test_add_an_item(self):
        """Create an item and add it to the database"""
        items = Items.all()
        self.assertEqual(items, [])
        item = Items(name="Blue shirt", category="shirt", available=True, condition=Condition.NEW)
        self.assertTrue(item is not None)
        self.assertEqual(item.id, None)
        item.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertEqual(item.id, 1)
        items = Items.all()
        self.assertEqual(len(items), 1)

    def test_update_a_pet(self):
        """Update a Pet"""
        pet = PetFactory()
        logging.debug(pet)
        pet.create()
        logging.debug(pet)
        self.assertEqual(pet.id, 1)
        # Change it an save it
        pet.category = "k9"
        original_id = pet.id
        pet.update()
        self.assertEqual(pet.id, original_id)
        self.assertEqual(pet.category, "k9")
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        pets = Pet.all()
        self.assertEqual(len(pets), 1)
        self.assertEqual(pets[0].id, 1)
        self.assertEqual(pets[0].category, "k9")

    def test_delete_a_pet(self):
        """Delete a Pet"""
        pet = PetFactory()
        pet.create()
        self.assertEqual(len(Pet.all()), 1)
        # delete the pet and make sure it isn't in the database
        pet.delete()
        self.assertEqual(len(Pet.all()), 0)

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
        self.assertIn("available", data)
        self.assertEqual(data["available"], item.available)
        self.assertIn("condition", data)
        self.assertEqual(data["condition"], item.condition)

    def test_deserialize_an_item(self):
        """Test deserialization of an Item"""
        data = {
            "id": 1,
            "name": "Blue shirt",
            "category": "shirt",
            "available": True,
            "condition": "NEW",
        }
        item = Items()
        item.deserialize(data)
        self.assertNotEqual(item, None)
        self.assertEqual(item.id, None)
        self.assertEqual(item.name, "Blue shirt")
        self.assertEqual(item.category, "shirt")
        self.assertEqual(item.available, True)
        self.assertEqual(item.condition, Condition.NEW)

    def test_deserialize_missing_data(self):
        """Test deserialization of a Pet with missing data"""
        data = {"id": 1, "name": "Kitty", "category": "cat"}
        pet = Pet()
        self.assertRaises(DataValidationError, pet.deserialize, data)

    def test_deserialize_bad_data(self):
        """Test deserialization of bad data"""
        data = "this is not a dictionary"
        pet = Pet()
        self.assertRaises(DataValidationError, pet.deserialize, data)

    def test_deserialize_bad_available(self):
        """Test deserialization of bad available attribute"""
        test_pet = PetFactory()
        data = test_pet.serialize()
        data["available"] = "true"
        pet = Pet()
        self.assertRaises(DataValidationError, pet.deserialize, data)

    def test_deserialize_bad_condition(self):
        """Test deserialization of bad condition attribute"""
        test_pet = PetFactory()
        data = test_pet.serialize()
        data["gender"] = "male"  # wrong case
        pet = Pet()
        self.assertRaises(DataValidationError, pet.deserialize, data)

    def test_find_pet(self):
        """Find a Pet by ID"""
        pets = PetFactory.create_batch(3)
        for pet in pets:
            pet.create()
        logging.debug(pets)
        # make sure they got saved
        self.assertEqual(len(Pet.all()), 3)
        # find the 2nd pet in the list
        pet = Pet.find(pets[1].id)
        self.assertIsNot(pet, None)
        self.assertEqual(pet.id, pets[1].id)
        self.assertEqual(pet.name, pets[1].name)
        self.assertEqual(pet.available, pets[1].available)

    def test_find_by_category(self):
        """Find Pets by Category"""
        Pet(name="Fido", category="dog", available=True).create()
        Pet(name="Kitty", category="cat", available=False).create()
        pets = Pet.find_by_category("cat")
        self.assertEqual(pets[0].category, "cat")
        self.assertEqual(pets[0].name, "Kitty")
        self.assertEqual(pets[0].available, False)

    def test_find_by_name(self):
        """Find a Pet by Name"""
        Pet(name="Fido", category="dog", available=True).create()
        Pet(name="Kitty", category="cat", available=False).create()
        pets = Pet.find_by_name("Kitty")
        self.assertEqual(pets[0].category, "cat")
        self.assertEqual(pets[0].name, "Kitty")
        self.assertEqual(pets[0].available, False)

    def test_find_by_availability(self):
        """Find Pets by Availability"""
        Pet(name="Fido", category="dog", available=True).create()
        Pet(name="Kitty", category="cat", available=False).create()
        Pet(name="Fifi", category="dog", available=True).create()
        pets = Pet.find_by_availability(False)
        pet_list = list(pets)
        self.assertEqual(len(pet_list), 1)
        self.assertEqual(pets[0].name, "Kitty")
        self.assertEqual(pets[0].category, "cat")
        pets = Pet.find_by_availability(True)
        pet_list = list(pets)
        self.assertEqual(len(pet_list), 2)

    def test_find_by_gender(self):
        """Find Pets by Gender"""
        Pet(name="Fido", category="dog", available=True, gender=Gender.MALE).create()
        Pet(
            name="Kitty", category="cat", available=False, gender=Gender.FEMALE
        ).create()
        Pet(name="Fifi", category="dog", available=True, gender=Gender.MALE).create()
        pets = Pet.find_by_gender(Gender.FEMALE)
        pet_list = list(pets)
        self.assertEqual(len(pet_list), 1)
        self.assertEqual(pets[0].name, "Kitty")
        self.assertEqual(pets[0].category, "cat")
        pets = Pet.find_by_gender(Gender.MALE)
        pet_list = list(pets)
        self.assertEqual(len(pet_list), 2)

    def test_find_or_404_found(self):
        """Find or return 404 found"""
        pets = PetFactory.create_batch(3)
        for pet in pets:
            pet.create()

        pet = Pet.find_or_404(pets[1].id)
        self.assertIsNot(pet, None)
        self.assertEqual(pet.id, pets[1].id)
        self.assertEqual(pet.name, pets[1].name)
        self.assertEqual(pet.available, pets[1].available)

    def test_find_or_404_not_found(self):
        """Find or return 404 NOT found"""
        self.assertRaises(NotFound, Pet.find_or_404, 0)