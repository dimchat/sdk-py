#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    DIM SDK Test
    ~~~~~~~~~~~~

    Unit test for DIM-SDK
"""

import unittest

from dimsdk import *


class EntityTestCase(unittest.TestCase):

    def test1_immortals(self):
        print('\n---------------- %s' % self)

        facebook = Facebook()
        id1 = facebook.identifier('moki@4WDfe3zZ4T7opFSi3iDAKiuTnUHjxmXekk')
        moki = facebook.user(identifier=id1)
        print('moki: ', moki)


class CommandTestCase(unittest.TestCase):

    def test1_receipt(self):
        print('\n---------------- %s' % self)

        cmd = ReceiptCommand.new(message='OK!')
        print('receipt: %s' % cmd)


if __name__ == '__main__':
    unittest.main()
