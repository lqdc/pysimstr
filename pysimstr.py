#!/usr/bin/env python3
'''
@file simstr.py
@date Sun 17 May 2015 06:58:33 PM PDT
@author Roman Sinayev
@email roman.sinayev@gmail.com
@detail Fast(ish) string similarity for one vs many comparisons.
'''

from collections import defaultdict

import Levenshtein


def make_unique_ngrams(s, n):
    """Make a set of unique n-grams from a string."""
    return set(s[i:i + n] for i in range(len(s) - n + 1))


class UnintitializedError(Exception):
    pass


class SimStr(object):
    """Fast(ish) string similarity for one vs many comparisons.

    Parameters
    ----------

    cutoff : float, default=0.85
             cutoff to use for the comparison function. 0 is no cutoff.

    idx_size : int, default=3
               only consider items that have this many consecutive elements
               in common.  Larger indexes allow for faster computation, but
               can lead to more false negatives.

    plus_minus : int, default=3
                 Only consider strings that are different in this many
                 characters in length.

    comparison_func : callable, default=Levenshtein.jaro_winkler
                      a function that takes two strings as arguments
                      and returns a float type similarity score between them.
                      Comparison can be assymmetric and the string to check is
                      assumed to be the left/first arg.

    Examples
    --------

    >>> from pysimstr import SimStr
    >>> db = SimStr(idx_size=3, plus_minus=8)
    >>> db.insert(('Harry Potter And The Big Wizard Guy',  # I have not read HP
                   'Game Of Thrones',
                   'Mad Max'))
    >>> db.check("Harry Potter and the Sorcerer's Stone")  # True
    >>> db.check("Harry Something")  # False
    >>> db.retrieve("Mad Monkey")  # ['Mad Max']
    >>> db.retrieve_with_score('Mad Monkey')  # [('Mad Max',
                                              #   0.8690476190476191)]


    """
    def __init__(self,
                 cutoff=0.85,
                 idx_size=3,
                 plus_minus=3,
                 comparison_func=Levenshtein.jaro_winkler):
        self.cutoff = cutoff

        if idx_size < 1 or type(idx_size) is not int:
            raise ValueError('Index size has to be a positive integer')

        self.idx_size = idx_size
        self._els_idxed = None
        self.plus_minus = plus_minus
        self.comparison_func = comparison_func

    def check(self, s, instant_exact=True):
        """Check if a string is in the DB.

        :param s: str, string to check against the DB.
        :param instant_exact: bool, look up exact matches with a hash lookup.
        :return: True or False
        :rtype: bool

        """
        all_sets = self._get_comparison_strings(s)
        if instant_exact and s in all_sets:  # exact match
            return True

        for comparison_string in all_sets:
            if self.comparison_func(s, comparison_string) >= self.cutoff:
                return True
        return False

    def retrieve(self, s):
        """Retrieve all similar strings from the DB.

        :param s: str, string to check against the DB.
        :return: list of all similar strings.
        :rtype: list

        """
        all_similar = []
        for comparison_string in self._get_comparison_strings(s):
            if self.comparison_func(s, comparison_string) >= self.cutoff:
                all_similar.append(comparison_string)
        return all_similar

    def retrieve_with_score(self, s):
        """Retrieve all similar strings from the DB.

        :param s: str, string to check against the DB.
        :return: list of tuples - [(simlar_string, score)].
                 Empty list if not found.
        :rtype: list

        """
        all_similar = []
        for comparison_string in self._get_comparison_strings(s):
            score = self.comparison_func(s, comparison_string)
            if score >= self.cutoff:
                all_similar.append((comparison_string, score))

        return all_similar

    def insert(self, seq):
        """
        Populates the DB from a sequence of strings, ERASING PREVIOUS STATE.

        :param seq: an iterable

        """
        # erase previous elements and make defaultdict for easier insertion.
        self._els_idxed = defaultdict(lambda: defaultdict(set))
        if type(seq) is str:
            raise ValueError('Provided argument should be a sequence of strings'
                             ', but not a string itself.')
        for el in seq:
            if type(el) is not str:
                raise ValueError('Element %s is not a string' % (el,))
            for gram in make_unique_ngrams(el, self.idx_size):
                self._els_idxed[gram][len(el)].add(el)

        # convert defaultdict to dict so as to not increase size when checking
        # for presence of an element
        self._finalize_db()

    def _finalize_db(self):
        """Convert defaultdicts to regular dicts."""
        for k, v in self._els_idxed.items():
            self._els_idxed[k] = dict(v)
        self._els_idxed = dict(self._els_idxed)

    def _get_comparison_strings(self, s):
        """Find all similar strings"""
        str_len = len(s)
        comparison_idxs = make_unique_ngrams(s, self.idx_size)
        min_len = len(s) - self.plus_minus

        if min_len < 0:
            min_len = 0

        if self._els_idxed is None:
            raise UnintitializedError('Database not created')

        all_sets = set()
        for idx in comparison_idxs:
            found_idx = self._els_idxed.get(idx, None)
            if found_idx is None:
                continue
            for i in range(min_len, str_len + self.plus_minus):
                found_len = found_idx.get(i, None)
                if found_len is not None:
                    all_sets = all_sets.union(found_len)
        return all_sets
