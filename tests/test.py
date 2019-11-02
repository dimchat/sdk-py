#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    DIM SDK Test
    ~~~~~~~~~~~~

    Unit test for DIM-SDK
"""
import json
import unittest

from dimsdk import *

from mkm.crypto.utils import base64_encode
from mkm.immortals import Immortals

from tests.database import Database

g_facebook = Database()

g_immortals = Immortals()
moki_id = g_immortals.identifier(string='moki@4WDfe3zZ4T7opFSi3iDAKiuTnUHjxmXekk')
hulk_id = g_immortals.identifier(string='hulk@4YeVEN3aUnvC1DNUufCq1bs9zoBSJTzVEj')


def print_data(data: CAData):
    clazz = data.__class__.__name__
    print('<%s>' % clazz)
    print('    <issuer>%s</issuer>' % data.issuer)
    print('    <validity>%s</validity>' % data.validity)
    print('    <subject>%s</subject>' % data.subject)
    print('    <key>%s</key>' % data.key)
    print('</%s>' % clazz)


def print_ca(ca: CertificateAuthority):
    clazz = ca.__class__.__name__
    print('<%s>' % clazz)
    print('    <version>%d</version>' % ca.version)
    print('    <sn>%s</sn>' % ca.sn)
    print('    <info>%s</info>' % ca.info)
    print('    <signature>%s</signature>' % base64_encode(ca.signature))
    print('</%s>' % clazz)


common = {}


class CATestCase(unittest.TestCase):

    def test1_subject(self):
        print('\n---------------- %s' % self)

        issuer = {
            'O': 'GSP',
            'OU': 'Service Operation Department',
            'CN': 'dim.chat',
        }

        common['issuer'] = CASubject(issuer)
        print('issuer: ', common['issuer'])
        self.assertEqual(common['issuer'].organization, issuer['O'])

        subject = {
            'C': 'CN',
            'ST': 'Guangdong',
            'L': 'Guangzhou',

            'O': 'GSP',
            'OU': 'Service Operation Department',
            'CN': '127.0.0.1',
        }

        common['subject'] = CASubject(subject)
        print('subject: ', common['subject'])
        self.assertEqual(common['subject'].organization, subject['O'])

    def test2_validity(self):
        print('\n---------------- %s' % self)

        validity = {
            'NotBefore': 123,
            'NotAfter': 456,
        }
        common['validity'] = CAValidity(validity)
        print('validity: ', common['validity'])

    def test3_key(self):
        print('\n---------------- %s' % self)

        moki_meta = g_immortals.meta(identifier=moki_id)
        moki_pk = moki_meta.key
        key = moki_pk
        common['key'] = PublicKey(key)
        print('pubic key: ', common['key'])

    def test4_ca(self):
        print('\n---------------- %s' % self)

        info = {
            'Issuer': common['issuer'],
            'Validity': common['validity'],
            'Subject': common['subject'],
            'Key': common['key'],
        }
        common['info'] = CAData(info)
        print_data(common['info'])

        moki = g_immortals.user(identifier=moki_id)

        string = json.dumps(common['info']).encode('utf-8')
        signature = moki.sign(string)
        ca = {
            'version': 1,
            'sn': 1234567,
            'info': string,
            'signature': base64_encode(signature)
        }
        common['ca'] = CertificateAuthority(ca)
        print_ca(common['ca'])


class EntityTestCase(unittest.TestCase):

    def test1_immortals(self):
        print('\n---------------- %s' % self)

        id1 = g_facebook.identifier('moki@4WDfe3zZ4T7opFSi3iDAKiuTnUHjxmXekk')
        moki = g_facebook.user(identifier=id1)
        print('moki: ', moki)


class CommandTestCase(unittest.TestCase):

    def test1_receipt(self):
        print('\n---------------- %s' % self)

        cmd = ReceiptCommand.new(message='OK!')
        print('receipt: %s' % cmd)


if __name__ == '__main__':
    unittest.main()
