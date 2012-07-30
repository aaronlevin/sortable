# -*- coding: utf8 -*-
import codecs

from models import BinaryNode
from models import Listing
from models import Product
from models import Tree 

def main():
   
    listings_data = (row for row in open('data/listings.txt', 'rU'))
    products_data = [row for row in open('data/products.txt', 'rU')]
   

    # Build product trees
    # 1. product_tree is the 4-level tree used to split product data for ranking purposes
    # 2. product_search_tree is the Binary Search tree used to quickly aggregate the results and output them 
    print 'Constructing trees'
    product_tree = Tree()
    for index, prod in enumerate(products_data):
        product = Product(prod)
        product_tree.insert(product)
        if index == 0:
            product_search_tree = BinaryNode(product)
        else:
            product_search_tree.insert(product)

    print 'Matching listings'
    for listing_row in listings_data:
        listing = Listing(listing_row)
        match = product_tree.find(listing)
        if match is not None:
            product_search_tree.insert_payload(data=match, payload=listing.original_string)

    print 'traversing product tree and writing output'
    with codecs.open('results.txt','w',encoding='utf-8') as result_file:
        product_search_tree.traverse_with_action(lambda node: result_file.write(node.result_output))

if __name__ == u'__main__':
    main()
