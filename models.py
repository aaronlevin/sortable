# -*- coding: utf8 -*-

import json

class Item(object):
    """Pseudo-abstract class. Mainly used to provide string-related functions to process the data. These
    functions were common to both the Product and Listing class, so it made sense to stick them in here. 
    The `Item` class will contain several class-level members whose insantiation has some performance
    costs and therefore its important for them to only be loaded once"""

    delchars = ''.join(c for c in map(chr, range(256)) if ( (not c.isalnum()) and (c not in ('.')) ) )

    @classmethod
    def remove_non_alpha_characters(cls, dirty_string):
        """This method accepts a `dirty_string` and purfiys it by removing
        all non-alphanumeric characters. This method accepts both ASCII and Unicode strings.
        
        By `flat_string` we mean a string with only alphanumeric characters (no spaces, dashes or periods).
        """
        if isinstance(dirty_string, unicode):
            translate_table = dict((ord(char), None) for char in cls.delchars)
            return dirty_string.translate(translate_table)
        else:
            assert isinstance(dirty_string, str)
            return dirty_string.translate(None, cls.delchars)

    @classmethod
    def purify(cls, dirty_string):
        """This method uses `remove_non_alpha_characters` and `str.lower()` to return a "pure" string.
        """
        return cls.remove_non_alpha_characters(dirty_string).lower()

class Listing(Item):
    """Object that contains information for a listing.

    Instance members:
        - `original_string`: The original json string
        - `title`: title portion of json string
        - `title_pure`: purified title
        - `manufacturer`: manufacturer portion of json string
        - `manufacturer_pure`: purified manufacturer
    """

    title_separators = ('with','for','avec') # used to split `title` into `sub_title`

    def __init__(self, json_string_listing):
        """Constructor for Listing expects a string object formated like JSON as follows:
            {"title" : "Fujifilm FinePix S1600 12 MP Digital Cmaera with 15x Long Zoom (Black)",
             "manufacturer" : "Fujifilm Canada", 
             "currency" : "CAD",
             "price" : "729.95"
            }
        """
        super(Listing, self).__init__() # Call parent constructor
        listing_data = json.loads(json_string_listing)
        self.original_string = json_string_listing
        self.title = listing_data['title']
        self.title_pure = self.__class__.purify(self.title)
        self.manufacturer = listing_data['manufacturer']
        self.manufacturer_pure = self.__class__.purify(listing_data['manufacturer'])

        # find the important part of the title by splitting on title_separators
        self.sub_title = None
        for sep in self.__class__.title_separators:
            if len(self.title.lower().split(sep))>1:
                self.sub_title = self.__class__.purify(self.title.lower().split(sep)[0])

    def __unicode__(self):
        """Returns a unicode version of the string. Used for debugging
        """
        return_string = u''
        return_string += u'********** LISTING **********' + u'\n'
        return_string += u'Title: ' + self.title + u'\n'
        return_string += u'Manufacturer: ' + self.manufacturer + u'\n'
        return_string += u'-----------------------------' + u'\n'
        return return_string

    def __str__(self):
        """For laziness
        """
        return unicode(self).encode('utf-8')


class Product(Item):

    def __init__(self, json_string_listing):
        """Constructor for Products expects a string object in JSON format as follows:
            {"product_name":"Sony_Cyber-shot-_DSC_W310",
            "manufacturer":"Sony",
            "family":"Cyber Shot",
            "model":"DSC_W310",
            "announce-date":"2012-01-06T19:0:00:00.000-05:00"
            }
        """
        super(Product, self).__init__() # Call parent constructor
        product_data = json.loads(json_string_listing)
        self.product_name = product_data['product_name']
        self.manufacturer = product_data['manufacturer']
        self.manufacturer_pure = self.purify(product_data['manufacturer'])
        if 'family' in product_data:
            self.family = product_data['family']
            self.family_pure = self.purify(product_data['family'])
        else:
            self.family = None
            self.family_pure = None
        self.model = product_data['model']
        self.model_pure = self.__class__.purify(self.model)

    def __unicode__(self):
        return_string = u''
        return_string += u'********** PRODUCT **********' + u'\n'
        return_string += u'Product: ' + self.product_name + u'\n'
        return_string += u'Manufacturer: ' + self.manufacturer + u'\n'
        return_string += u'Family: ' + unicode(self.family) + u'\n'
        return_string += u'Model: ' + self.model + u'\n'
        return_string += u'-----------------------------' + u'\n'
        return return_string

    def __str__(self):
        return unicode(self).encode('utf-8')

    # A number of comparison operations are defined for use with the binary trees.
    
    def __eq__(self, other):
        """Override the comparison object.
        """
        if isinstance(other, Product):
            return self.product_name == other.product_name
        else:
            return False

    def __le__(self, other):
        """Override less-than-or-equal
        """
        if other is None:
            return False
        elif isinstance(other, Product):
            return self.product_name <= other.product_name
        else:
            return self.product_name <= other

    def __lt__(self, other):
        """Override less-than
        """
        if other is None:
            return False
        elif isinstance(other, Product):
            return self.product_name < other.product_name
        else:
            return self.product_name < other

    def __gt__(self, other):
        """Override greater-than
        """
        if other is None:
            return False
        elif isinstance(other, Product):
            return self.product_name > other.product_name
        else:
            return self.product_name > other

class NodeFactory(object):
    """Factory that generates specialized Tree structure used to traverse products quickly.

    Has a factory-esque pattern where a new type of node is generated depending on the `_type` attribute.
    This is because the matching methods for each node depend on the level of the tree (i.e. matching
    at the `model` level is different from matching at the `family` level (`model` will be more strict)).

    At the base of the tree are products, so if the node type is `Model`, then the node will hold members of
    the `Product` class. 
    """
    def __new__(cls, node, product):
        if node._type is 'god':
            return ManufacturerNode(product)
        elif node._type == 'manufacturer':
            return FamilyNode(product)
        elif node._type == 'family':
            return ModelNode(product)
        else:
            return product 

class Tree(object):
    """This is a specialized, 4-level tree based on the following Product hierarchy:
        
        - Manufacturer
        - - Family
        - - - Model
        - - - - Product
        
        Where `Product` is a product class. To construct the tree, we pass a `Product` and at each level,
        a node is created with a value (`_id`). 

        This Tree is used for fast(er) matching. The idea is that since the `Listing` item contains a `manufacturer`
        property, if a listing does not match on the manufactuer, we shouldn't even bother checking any other products.
        For example: if the Manufactuer is Sony, why bother checking any products with manufacturer Casio.

        Additionally, this Tree encapsulates the matching algorithm, by recursively running through the Tree and updating
        a dictionary (in the `_get_rank` method this is the `product_dict`) to hold rankings at each level of the hierarchy.
        An (simple) algorithm is then applied to the high-level ranking and the best result can be chosen.
    """

    _type = 'god' 
    _append = '_pure'

    def __init__(self, product=None):
        self._children = []
        if product is not None:
            self._id = product.__dict__[self.__class__._type + self.__class__._append] if self.__class__._type is not None else None
            self._children.append(NodeFactory(self.__class__, product))
        else:
            self._id = None
    
    def _get_rank(self, product_dict):
        return product_dict['manufacturer'] * (product_dict['family'] + product_dict['model'])

    def find(self, listing):
        """Given a listing object, this method will traverse the tree, finding the best matched Product.
        `find` uses `get_matches` to get all mathces with a rank > 0. It then finds the highest ranked
        and returns that Product.
        """
        top_rank = 0
        top_match = None
        results = self.get_matches(listing)
        if len(results) == 0:
            return None
        elif len(results) == 1:
            return results[0]['product']
        else:
            for result in results:
                rank = self._get_rank(result)
                if rank > top_rank:
                    top_rank = rank
                    top_match = result['product']
            return top_match

    def get_matches(self, listing, result_dict={}):
        """Recursive class method that updates a `result_dict` as it traverses the tree. It uses a pseudo-map-reduce pattern to aggregate
        the recursive results from child calls. In other words, it does the following:
            
            1. for each child node, find the ranks and populate the `match_stack` with the ranks that matter.
            
            2. If the child is None (i.e. for `Family` nodes), include it in the `match_stack`.
               If the rank is larger than 0, include it in the `match_stack`. 

            3. Now, the match_stack has a list of child nodes that are good matches for further exploration in the tree.

               If the `match_stack` is 0, then we've found no such good matches, and we shoudl stop exploring. This means that somewhere mid-tree,
               we've found that while a parent node had a good match, none of the children are good, so we should stop.

            4. After excluding the case of no matches, we iterate over the matches we have. But first, we need to copy the `result_dict`. So, for each match,
               make a copy of the result_dict (if there is only one match, don't copy).

            5. Now, for each child node in the `match_stack`, recursively use the `get_matches` method, passing the original listing and the `result_dict`.

            6. Once this has been done, we need to collect the results and aggregate them. This is why the recursive `get_matches` happen in a `+=` block. Python
               does pretty efficient list concatenation this way.

            7. Once the results have been aggregated and concatenated, we return them.

        The cool part about this is that the `result_dict` is updated at each node, uniquely, by using the `_type` attribute as the keys. This is great because
        we can efficiently traverse the tree, filtering out the bad branches while also accounting for cases where good matches in higher nodes lead to poor lower nodes, all
        the while abstracting the actual coallation and ranking algorithm to another function. So, we can calculate a "rank" at each node, and then allow another function to
        determine how to deal with multiple matches.
        """
        match_stack = [] 
        results = []
        collector = []
       
        for child in self._children:
            tmp_rank = child.rank_calc(listing)
            if child._id is None:
                match_stack.append((child, tmp_rank))
            else:
                if tmp_rank > 0:
                    match_stack.append((child, tmp_rank))

        stack_length = len(match_stack)
        if stack_length == 0:
            # Gone down the wrong branch, nothing more to see here. Stop.
            del result_dict
            return [] 
        else:
            for index, (child, rank) in enumerate(match_stack):
                if index == (stack_length - 1):
                    # Let's be efficient and prevent copying when we don't need to.
                    result_dict[child._type] = rank
                    results.append(result_dict)
                else:
                    # OK, now we really need to copy
                    tmp = result_dict.copy()
                    tmp[child._type] = rank
                    results.append(tmp)
        
            for index, (child, rank) in enumerate(match_stack):
                tmp = child.get_matches(listing, results[index])
                collector += tmp if tmp is not None else [] 
            return collector 

    def insert(self, product):
        """Method to recursively add nodes to the tree.
        """
        match = False
        for child in self._children:
            if child._id == product.__dict__[child._type + self.__class__._append]:
                match = True
                child.insert(product) 
        if not match:
            self._children.append(NodeFactory(self.__class__, product))

class ManufacturerNode(Tree):
   
    _type = 'manufacturer'

    def rank_calc(self, listing):
        return len(self._id) if self._id in listing.manufacturer_pure else 0

    def get_matches(self, listing, result_dict):
        collector = []
        length = len(result_dict)
        for index, child in enumerate(self._children):
            rank = self.rank_calc(listing)
            if index == (length -1):
                result_dict['family'] = rank 
                collector += child.get_matches(listing, result_dict)
            else:
                tmp = result_dict.copy()
                tmp['family'] = self.rank_calc(listing)
                collector += child.get_matches(listing, tmp)
        return collector

class FamilyNode(Tree):

    _type = 'family'

    def rank_calc(self, listing):
        if self._id is not None:
            return len(self._id) if self._id in listing.title_pure else 0
        else:
            return 0
    
class ModelNode(Tree):
    """The model node appears at the bottom of the tree, so it has a specialized `insert` method
    and `get_matches` method.
    """

    _type = 'model'

    def rank_calc(self, listing):
        if listing.sub_title is not None:
            return len(self._id) if self._id in listing.sub_title else 0
        else:
            return len(self._id) if self._id in listing.title_pure else 0

    def get_matches(self, listing, result):
        result['product'] = self._children[0]
        return [result]


    def insert(self, product):
        if product not in self._children:
            self._children.append(product)

class BinaryNode(object):
    """Binary Tree node implementation to assist with fast lookup of `product_name` for coallation of listing results.
    Binary Tree has left and right child with data that can be any object implementing a total ordering
    """
    
    def __init__(self, data=None):
        """BinaryNode initializer

        data: any data object implementing a total ordering
        """
        self.left = None
        self.right = None
        self.data = data
        self.payload = None 

    def insert(self, data):
        """Class method to insert data recursively.

        data: data to be inserted. must implement a total ordering.
        """
        if data <= self.data:
            if self.left is None:
                self.left = BinaryNode(data)
            else:
                self.left.insert(data)
        else:
            if self.right is None:
                self.right = BinaryNode(data)
            else:
                self.right.insert(data)

    def lookup(self, data):
        """Recursive lookup to find node where `self.data = data`
        """
        if self.data is None:
            return self.right.lookup(data)
        elif data < self.data:
            return None if self.left is None else self.left.lookup(data)
        elif data > self.data:
            return None if self.right is None else self.right.lookup(data)
        else:
            return self

    def insert_payload(self, data, payload):
        """Method to find a node and insert a payload.
        """
        node = self.lookup(data)
        if node is not None:
            # Yay, we found a node. Now, insert payload
            if node.payload is not None:
                node.payload.append(payload)
            else:
                node.payload = [payload]
        else:
            raise Exception('Was not able to find a node with %s', data)

    def remove_payload(self, data):
        """Method to find a node and pop most recent payload off
        """

        node = self.lookup(data)
        if node is not None:
            if node.payload is not None:
                node.payload.pop()
            else:
                pass
        else:
            raise Exception('Was not able to find node with %s', data)

    @property
    def result_output(self):
        """Output formatting for the final result.

        **NOTE**: appends new-line character at end
        """
        result_string = u''
        if self.payload is not None and self.data is not None:
            result_string += u'{"product_name": "'
            result_string += self.data.product_name
            result_string += u'", "listings": ['
            for index, listing in enumerate(self.payload):
                result_string += u'"'
                result_string += listing.decode('utf-8')
                result_string += u'"'
                result_string += u', ' if index != (len(self.payload)-1) else u''
            result_string += u']}'
            result_string += u'\n'
        
        return result_string

    def traverse_with_action(self, action):
        """Method to traverse every node below, on both left and right sides.
        Action will be applied to the node.
        """
        action(self)
        
        if self.left is not None:
            self.left.traverse_with_action(action)
        
        if self.right is not None:
            self.right.traverse_with_action(action)

