Sortable Coding Challenge
=========================

# About Me

My name is [Aaron Levin](http://aaronlevin.ca). I live in Toronto. I am a Pure Mathematician (MSc. Mathematics, University of Albeta, 2008), ex-Used Record Dealer, [award-winning](http://music.cbc.ca/#/blogs/2011/3/Edmontons-Weird-Canada-named-Best-Canadian-Music-Site) music-blogger, and wanna-be software engineer. Secretly I've always wanted to be an engineer (I actually *am* an engineer, but not of the software variety - more of the laser variety). During my undergraduate studies (BSc. Engineering Physics, University of Alberta, 2005) I focused on Computational Physics. Afterwards, I spent a year using computers to study High-Temperature Superconductors at the University of Waterloo before discovering the orgy of abstraction that is Mathematics. In the end I went into Media to take a break from academia and all the while kept thinking back to my days writing code. I recently concluded that developing software provided me with an endless stream of joy, frustration, inspiration, and challenge. This is what I would like to be doing with my day. Thus, I decided to dive into Python in my spare time. Having been formally trained in C++, I welcomed Python's ease and beauty and am still in awe by its power and, well, fun and personality.  

This challenged seemed like a great entry-point to getting my feet wet. In the process I had a lot of fun. 

## About My Software Experience

- At school I learned: C, C++, Assembler (MC68000)  
- In my spare-time I work with: Python, \*SQL, MongoDB  
- At work I use: Python, R, SQLServer 2008, SQLite  
- For web-development I enjoy: Flask (Python web-framework), MongoDB (because it's so easy)  
- I wish I had learned: Haskell, Django, Go 

## About My Education Experience

- MSc. Mathematics (University of Alberta). Original research extending the [Perron-Frobenius Theorem](http://en.wikipedia.org/wiki/Perron%E2%80%93Frobenius_theorem) to an infinite-dimensional setting. The *Perron-Frobenius Theorem* is used extensively in Linear Algebra and computer algorithms. It's a very powerful and interesting theorem.
- (partial) MSc. Physics (University of Waterloo). Studied Computational Physics in the area of High-Temperature Superconductors. 
- BSc. Engineering Physics (University of Alberta). Focused in Computational Physics / Numerical Methods and Condensed Matter Physics.   

# Instructions

I tried to make sure the only dependency was Python 2.7. So, I didn't use any external libraries. Basically: make sure you have Python 2.7 and you should be good to go. 

- To run the code: `git clone https://github.com/weirdcanada/weirdcanada.git` and then `python main.py`. The program will spit out the results to `results.txt`. 
- If you feel like it, there are tests: `python tests.py` 

Other notes:

- Make sure when you `git clone` you leave the `listings.txt` and `products.txt` in the `data` directory. 

# Methodology

When I started I really wanted to use probabilistic methods. I wanted to use Levenshtein distance and all the fun language metrics and mathematics at my disposal. I even came up with a clever idea to make some horrible assumption (no antonyms) and map all the letters to multiplications of prime numbers to get a unique, numeric representation for each word, using this to very quickly make matches. However, as I thought about the problem (mainly: no false positives) and looked at the data-set, I began to implement a more direct methodology. A probabilistic method would always result in *some* false-positives and since the data-set was fairly simple and structured, it didn't seem necessary to go down that road. In a real world application, I would have spent a lot more time doing unsupervised learning on the text itself before parsing (for example: detecting seperator words ('with', 'for', 'avec') and other language structures).

Instead, I focused on using the hierarchial nature of the `products.txt` feed to structure a specialized `Tree` where clusters of branches represented a hierarchy consisting of: `Manufacturer`, `Family`, `Model`. Matches were ranked on how well they matched for all the levels (i.e. you *had* to match `Manufacturer`, and have good matches for both `Family` and `Model`). Additionally, this tree was traversed for matching purposes, which lead to some efficiencies as we didn't need to traverse branches where Manufactuerer matched (i.e. if `Sony` was nowhere in the listing text, don't go down the `Sony` tree/branch/thinger). 

After finding all the matches, I needed somewhere to store and aggregate them. A Binary tree was used for this. 

Insofar as data structures and algorithms are concerned, I found that Python's `in` was quite fast and seemed to implement many of the better string-search algorithms. I did a lot of benchmarking in looking at Python's `in` versus `set` intersection and other native types and found that `in` was comparably fast. 

## Product Tree

![4-Level Product Tree](http://weirdcanada.com/binary/images/Product_Tree.png)

## Binary Product Tree

![Binary Search (Product) Tree](http://weirdcanada.com/binary/images/Binary_Search_Product_Tree.png)


