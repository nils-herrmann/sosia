#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for queries module."""

from nose.tools import assert_equal, assert_true
from scopus import ScopusSearch

from sosia.utils import find_country, parse_doc, query_journal


def test_find_country():
    pubs = ScopusSearch('AU-ID(6701809842)').results
    received = find_country(['6701809842'], pubs, 2000)
    assert_equal(received, 'Germany')


def test_parse_doc():
    received = parse_doc('55208373700', 2012, refresh=False, verbose=False)
    received_list = parse_doc(['55208373700','55208373700'], 2012, 
                              refresh=False, verbose=False)
    expected_refs = '29144517611 57849112238 51249091642 70449099678 '\
        '84865231386 15944370019 8744256776 0004256525 84866333650 '\
        '78650692566 0002969912 0007622058 0000169440 0003685848 '\
        '43049125937 43149086011 84866332328 27744606594 2442709303 '\
        '84866309814 34248571923 0029824384 34548317343 3142544611 '\
        '84866333054 0003457562 0032394091 0001116544 84866324358 '\
        '84866328142 0039484749 0001275239 34249696486 70449641263 '\
        '0035654659 77953978121 55049124635 67650248718 39149084479 '\
        '40749109418 35348862941 0030559826 34547860480 77953702055 '\
        '18144372897 0004062815 84972591424 0034423919 0033675552 '\
        '0034424078 0027767147 0035654590 4243112264 29144486677 '\
        '0004164119 84866328143 33645383647 84866326504 23044470851 '\
        '78649697033 2442654430 0141625872 30444461409 0034435025 '\
        '47949124687 84920182751 84887864855 84866332329 84984932935 '\
        '33845620645 0942299814'
    assert_equal(received['refs'], expected_refs)
    assert_equal(received_list['refs'], expected_refs)
    expected_abs = 'Through an analysis of 497 foreign researchers in Italy '\
        'and Portugal we verify the impact of home linkages on return '\
        'mobility choices and scientific productivity. We consider the '\
        'presence of several different types of linkages of the researchers '\
        'working abroad with their country of origin and control for the '\
        'most relevant contextual factors (age, research area, position in '\
        'the host country, etc.). The probability of return to their home '\
        'country and scientific productivity in the host country are both '\
        'higher for researchers that maintain home linkages. We conclude '\
        'that the presence of home linkages directly benefits both '\
        'countries in addition to the indirect benefit of expanding the '\
        'scientific networks. Policy implications and suggestions for '\
        'further research are discussed.'
    assert_equal(received['abstracts'], expected_abs)


def test_query_journal():
    # test a journal with more than 5k publications in one year
    res = query_journal("11000153773",[2006],refresh=False)
    assert_true(45000 < len(res.get("2006")) < 50000)