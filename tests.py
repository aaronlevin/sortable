# -*- coding: utf-8 -*-

import json
import unittest
from models import BinaryNode
from models import Item
from models import Listing
from models import Product
from models import Tree

class TestItem(unittest.TestCase):

    def test_removal_of_special_characters(self):
        item = Item()
        test_string = 'hello%(*)@$)(aaa333$$$%%%^^^&&&aaa333!@#$%^&*()-_\]}[{;:\'"?/.>,<'
        self.assertEqual(item.remove_non_alpha_characters(test_string), 'helloaaa333aaa333.')
        del item

    def test_purification(self):
        item = Item()
        test_string = 'aArOn!!!@@@###$$$%%%^^^&&&***((()))lEvIn'
        self.assertEqual(item.purify(test_string), 'aaronlevin')
        del item

class TestListingClass(unittest.TestCase):

    def setUp(self):
        data = open('data/test_listings.txt', 'r')
        self.data = []
        self.json_objects = []
        for row in data:
            self.data.append(row)
            self.json_objects.append(json.loads(row))
        data.close()

    def test_instantiation(self):
        listings = []
        for index, data in enumerate(self.data):
            tmp_listing = Listing(data)
            self.assertEqual(tmp_listing.title, self.json_objects[index]['title'])
            self.assertEqual(tmp_listing.manufacturer, self.json_objects[index]['manufacturer'])
            self.assertEqual(tmp_listing.currency, self.json_objects[index]['currency'])
            self.assertEqual(tmp_listing.price, self.json_objects[index]['price'])
            del tmp_listing

    def test_instantiation_values(self):
        for index, data in enumerate(self.data):
            if index == 0:
                tmp_listing = Listing(data)
                self.assertEqual(tmp_listing.title, 'title1 weird-canada rocks 14.4GB')
                self.assertEqual(tmp_listing.currency, 'CAD')
                self.assertEqual(tmp_listing.manufacturer, 'manu1')
                self.assertEqual(tmp_listing.price, '35.99')
                del tmp_listing
    
class TestProductClass(unittest.TestCase):
    def setUp(self):
        data = open('data/test_products.txt', 'r')
        self.data = []
        self.json_objects = []
        for row in data:
            self.data.append(row)
            self.json_objects.append(json.loads(row))
        data.close()

    def test_instantiation(self):
        products = []
        for index, data in enumerate(self.data):
            tmp_product = Product(data)
            self.assertEqual(tmp_product.product_name, self.json_objects[index]['product_name'])
            self.assertEqual(tmp_product.manufacturer, self.json_objects[index]['manufacturer'])
            self.assertEqual(tmp_product.model, self.json_objects[index]['model'])
            if 'family' in self.json_objects[index]:
                self.assertEqual(tmp_product.family, self.json_objects[index]['family'])
            else:
                self.assertEqual(tmp_product.family, None)
            self.assertEqual(tmp_product.announced_date, self.json_objects[index]['announced-date'])
            del tmp_product

class TestBinaryProductsAndListings(unittest.TestCase):
    def setUp(self): 
        self.test_product_1 = Product('{"product_name":"Nikon-s6100","manufacturer":"Nikon","model":"S6100","family":"Coolpix","announced-date":"2011-02-08T19:00:00.000-05:00"}')
        self.test_product_2_no_family = Product('{"product_name":"Casio_QV-5000SX","manufacturer":"Casio","model":"QV-5000SX","announced-date":"1998-04-19T20:00:00.000-04:00"}')
        self.test_product_3 = Product('{"product_name":"Casio_Exilim_EX-H20G","manufacturer":"Casio","model":"EX-H20g","family":"Exilim","announced-date":"2010-09-19T20:00:00.000-04:00"}')
        self.test_listing_1 = Listing('{"title":"Canon PowerShot D10 12.1 MP Waterproof Digital Camera with 3x Optical Image Stabilized Zoom and 2.5-inch LCD (Blue/Silver)","manufacturer":"Canon Canada","currency":"CAD","price":"420.33"}')
        self.test_listing_2 = Listing('{"title":"Olympus PEN E-PL1 12.3MP Live MOS Micro Four Thirds Interchangeable Lens Digital Camera with 14-42mm f/3.5-5.6 Zuiko Digital Zoom Lens (Black)","manufacturer":"Olympus Canada","currency":"CAD","price":"598.97"}')
        self.test_listing_3_unicode = Listing('{"title":"Canon - EOS 400D - Appareil photo numérique reflex boîtier nu - 10,1 Mpix","manufacturer":"Canon","currency":"EUR","price":"279.00"}')
        self.tree = Tree()
        self.tree.insert(self.test_product_1)
        self.tree.insert(self.test_product_2_no_family)
        self.tree.insert(self.test_product_3)
 
    def test_binary_manufacturer_setup(self):
        # There's two manufacturers: "casio" and "nikon"
        self.assertEqual(len(self.tree._children), 2)
        self.assertEqual(self.tree._children[0]._type, 'manufacturer')
        self.assertEqual(self.tree._children[1]._type, 'manufacturer')
        self.assertEqual(self.tree._children[0]._id, 'nikon')
        self.assertEqual(self.tree._children[1]._id, 'casio')

    def test_binary_family_setup(self):
        # For the Nikon, there's only one family and it's "coolpix"
        self.assertEqual(len(self.tree._children[0]._children), 1)
        self.assertEqual(self.tree._children[0]._children[0]._type,'family')
        self.assertEqual(self.tree._children[0]._children[0]._id,'coolpix')
        # For Casio, there should be two family children: "None" and "exilim"
        self.assertEqual(len(self.tree._children[1]._children), 2)
        self.assertEqual(self.tree._children[1]._children[0]._type,'family')
        self.assertEqual(self.tree._children[1]._children[0]._id, None)
        self.assertEqual(self.tree._children[1]._children[1]._type,'family')
        self.assertEqual(self.tree._children[1]._children[1]._id,'exilim')
        
    def test_binary_model_setup(self):
        # Only one model for the `nikon` branch
        self.assertEqual(len(self.tree._children[0]._children[0]._children),1)
        # brevity
        nikon_model = self.tree._children[0]._children[0]._children[0]
        self.assertEqual(nikon_model._type, 'model')
        self.assertEqual(nikon_model._id,'s6100')
        # Should be only model modein in separate branches of the `Casio` branch
        self.assertEqual(len(self.tree._children[1]._children[0]._children),1)
        self.assertEqual(len(self.tree._children[1]._children[1]._children),1)
        casio_model_1 = self.tree._children[1]._children[0]._children[0]
        casio_model_2 = self.tree._children[1]._children[1]._children[0]
        self.assertEqual(casio_model_1._type, 'model')
        self.assertEqual(casio_model_1._id,'qv5000sx')
        self.assertEqual(casio_model_2._type,'model')
        self.assertEqual(casio_model_2._id,'exh20g')

    def test_find_returns_product(self):
        self.assertEqual(isinstance(self.tree.find(Listing('{"title":"Casio Exilim EX-H20G EXILIM Hi-Zoom; 14.1 MP; 4320 x 3240 pixels; 4 x; 10 x; 3.2 - 5.7; 3.2 - 7.5 (EX-H20GSREDA)","manufacturer":"CASIO","currency":"GBP","price":"246.24"}')),Product), True)


class TestBinarySearchTree(unittest.TestCase):
    def setUp(self):
        self.numeric_tree = BinaryNode()
        self.product_tree = BinaryNode()
        self.numeric_tree.insert(10)
        self.numeric_tree.insert(20)
        self.numeric_tree.insert(15)
        self.numeric_tree.insert(5)
        self.numeric_tree.insert(2)
        self.numeric_tree.insert(7)
        self.test_product_1 = Product('{"product_name":"Nikon-s6100","manufacturer":"Nikon","model":"S6100","family":"Coolpix","announced-date":"2011-02-08T19:00:00.000-05:00"}')
        self.test_product_2_no_family = Product('{"product_name":"Casio_QV-5000SX","manufacturer":"Casio","model":"QV-5000SX","announced-date":"1998-04-19T20:00:00.000-04:00"}')
        self.test_product_3 = Product('{"product_name":"Casio_Exilim_EX-H20G","manufacturer":"Casio","model":"EX-H20g","family":"Exilim","announced-date":"2010-09-19T20:00:00.000-04:00"}')
        self.product_tree.insert(self.test_product_1)
        self.product_tree.insert(self.test_product_2_no_family)
        self.product_tree.insert(self.test_product_3)

    def test_numeric_tree(self):
        self.assertEqual(self.numeric_tree.right.data, 10)
        self.assertEqual(self.numeric_tree.right.right.data, 20)
        self.assertEqual(self.numeric_tree.right.right.left.data, 15)
        self.assertEqual(self.numeric_tree.right.left.data, 5)
        self.assertEqual(self.numeric_tree.right.left.left.data, 2)
        self.assertEqual(self.numeric_tree.right.left.right.data, 7)

    def test_product_tree(self):
        self.assertEqual(self.product_tree.right.data.product_name,'Nikon-s6100')
        self.assertEqual(self.product_tree.right.left.data.product_name, 'Casio_QV-5000SX')
        self.assertEqual(self.product_tree.right.left.left.data.product_name, 'Casio_Exilim_EX-H20G')

    def test_numeric_lookup(self):
        self.assertEqual(self.numeric_tree.lookup(15).data, 15)
        self.assertEqual(self.numeric_tree.lookup(7).data, 7)
        self.assertEqual(self.numeric_tree.lookup(2).data, 2)
        self.assertEqual(self.numeric_tree.lookup(1),None)
        self.assertEqual(self.numeric_tree.lookup(1290410), None)

    def test_product_lookup(self):
        self.assertEqual(self.product_tree.lookup(self.test_product_1).data, self.test_product_1)
        self.assertEqual(self.product_tree.lookup(self.test_product_2_no_family).data, self.test_product_2_no_family)
        self.assertEqual(self.product_tree.lookup(self.test_product_3).data, self.test_product_3)
        self.assertEqual(self.product_tree.lookup(Product('{"product_name":"Fujifilm-AX305","manufacturer":"Fujifilm","model":"AX305","family":"FinePix","announced-date":"2011-02-15T19:00:00.000-05:00"}')), None)

    def test_insert_and_pop_payload(self):
        self.product_tree.insert_payload(self.test_product_3, 'I am the payload')
        self.assertEqual(self.product_tree.lookup(self.test_product_3).payload[0], 'I am the payload')
        self.product_tree.insert_payload(self.test_product_3, 'Another payload')
        self.assertEqual(len(self.product_tree.lookup(self.test_product_3).payload), 2)
        self.assertEqual(self.product_tree.lookup(self.test_product_3).payload[1],'Another payload')
        self.product_tree.remove_payload(self.test_product_3)
        self.assertEqual(len(self.product_tree.lookup(self.test_product_3).payload), 1)
        self. product_tree.remove_payload(self.test_product_3)
        self.assertEqual(len(self.product_tree.lookup(self.test_product_3).payload), 0)

    def test_result_output(self):
        self.product_tree.insert_payload(self.test_product_2_no_family, 'payload')
        self.assertEqual(self.product_tree.lookup(self.test_product_2_no_family).result_output, u'{"product_name": "Casio_QV-5000SX", "listings": ["payload"]}\n')
        self.assertEqual(self.product_tree.lookup(self.test_product_3).result_output, u'')

    def test_traverse_with_action(self):
        node_counter = [] 
        self.numeric_tree.traverse_with_action(lambda x: node_counter.append(1))
        self.assertEqual(len(node_counter), 7) # 7 to account for initial null node.
 
if __name__ == '__main__':
    
    unittest.main()
