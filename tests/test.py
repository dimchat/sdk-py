#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    DIM SDK Test
    ~~~~~~~~~~~~

    Unit test for DIM-SDK
"""

import unittest

from dimsdk import ReceiptCommand


class CommandTestCase(unittest.TestCase):

    def test1_receipt(self):
        print('\n---------------- %s' % self)

        cmd = ReceiptCommand.new(message='OK!')
        print('receipt: %s' % cmd)


if __name__ == '__main__':
    unittest.main()
