[![Build Status](https://travis-ci.org/lqdc/pysimstr.svg?branch=master)](https://travis-ci.org/lqdc/pysimstr)

#PySimStr

*Fast(ish) string similarity for one vs many comparisons.*


Solves the problem of fuzzy searching many different (unknown in advance)
strings, one at a time, against a relatively large constant collection
of strings that fits in memory many times over.

Example problem:
```py
some_big_collection = ['Foo', 'bar', 'Something Else' ...]

import Levenshtein

def compare_bruteforce(s_to_compare, some_big_collection, threshold):
    for element in some_big_collection:
        score = Levenshtein.jaro_winkler(s_to_compare, element)
        if score >= threshold:
            return True
    return False
```

As an example of real-world performance, this library speeds up string
lookup ~10^4 times when searching for a string in a collection of 10^5
entities with a trigram index and plus-minus 3-letter length
difference when using Jaro-Winkler comparison function.

Usage Example:
```py
    >>> from pysimstr import SimStr
    >>> db = SimStr(idx_size=3, plus_minus=8, cutoff=0.85)
    >>> db.insert(('Harry Potter And The Big Wizard Guy',  # I have not read HP
                   'Game Of Thrones',
                   'Mad Max'))
    >>> db.check("Harry Potter and the Sorcerer's Stone")  # True
    >>> db.check("Harry Something")  # False
    >>> db.retrieve("Mad Monkey")  # ['Mad Max']
    >>> db.retrieve_with_score('Mad Monkey')  # [('Mad Max',
                                              #   0.8690476190476191)]
```

Speedup is achieved by an n-gram indexing strategy
and only comparing strings of similar length.

Most useful with Levenshtein-like distance functions that take a while to compute.

####Note
Comparisons can take a lot longer if the new strings are large compared to
index size. If your incoming dataset has variable sized strings such as strings
of only 3 characters in length and strings of 20 characters in length,
you should make several instances of the SimStr class with different
index sizes.

Compare the larger strings against instances with larger index sizes.
