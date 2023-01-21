#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    DIM SDK Test
    ~~~~~~~~~~~~

    Unit test for DIM-SDK
"""

import unittest

from dimsdk import *
from plugins.dimplugins import *

from tests.database import Database

register_all_factories()
register_plugins()

g_facebook = Database()

moki_id = ID.parse(identifier='moki@4WDfe3zZ4T7opFSi3iDAKiuTnUHjxmXekk')
hulk_id = ID.parse(identifier='hulk@4YeVEN3aUnvC1DNUufCq1bs9zoBSJTzVEj')


# def print_data(data: CAData):
#     clazz = data.__class__.__name__
#     print('<%s>' % clazz)
#     print('    <issuer>%s</issuer>' % data.issuer)
#     print('    <validity>%s</validity>' % data.validity)
#     print('    <subject>%s</subject>' % data.subject)
#     print('    <key>%s</key>' % data.key)
#     print('</%s>' % clazz)
#
#
# def print_ca(ca: CertificateAuthority):
#     clazz = ca.__class__.__name__
#     print('<%s>' % clazz)
#     print('    <version>%d</version>' % ca.version)
#     print('    <sn>%s</sn>' % ca.sn)
#     print('    <info>%s</info>' % ca.info)
#     print('    <signature>%s</signature>' % Base64.encode(ca.signature))
#     print('</%s>' % clazz)


common = {}


class CATestCase(unittest.TestCase):

    def test1_subject(self):
        print('\n---------------- %s' % self)

        # issuer = {
        #     'O': 'GSP',
        #     'OU': 'Service Operation Department',
        #     'CN': 'dim.chat',
        # }
        #
        # common['issuer'] = CASubject(issuer)
        # print('issuer: ', common['issuer'])
        # self.assertEqual(common['issuer'].organization, issuer['O'])
        #
        # subject = {
        #     'C': 'CN',
        #     'ST': 'Guangdong',
        #     'L': 'Guangzhou',
        #
        #     'O': 'GSP',
        #     'OU': 'Service Operation Department',
        #     'CN': '127.0.0.1',
        # }
        #
        # common['subject'] = CASubject(subject)
        # print('subject: ', common['subject'])
        # self.assertEqual(common['subject'].organization, subject['O'])

    def test2_validity(self):
        print('\n---------------- %s' % self)

        # validity = {
        #     'NotBefore': 123,
        #     'NotAfter': 456,
        # }
        # common['validity'] = CAValidity(validity)
        # print('validity: ', common['validity'])

    def test3_key(self):
        print('\n---------------- %s' % self)

        # moki_meta = g_immortals.meta(identifier=moki_id)
        # moki_pk = moki_meta.key
        # common['key'] = moki_pk
        # print('pubic key: ', common['key'])

    def test4_ca(self):
        print('\n---------------- %s' % self)

        # info = {
        #     'Issuer': common['issuer'],
        #     'Validity': common['validity'],
        #     'Subject': common['subject'],
        #     'Key': common['key'],
        # }
        # common['info'] = CAData(info)
        # print_data(common['info'])
        #
        # moki = g_immortals.user(identifier=moki_id)
        #
        # string = json.dumps(common['info']).encode('utf-8')
        # signature = moki.sign(string)
        # ca = {
        #     'version': 1,
        #     'sn': 1234567,
        #     'info': string,
        #     'signature': Base64.encode(signature)
        # }
        # common['ca'] = CertificateAuthority(ca)
        # print_ca(common['ca'])


class EntityTestCase(unittest.TestCase):

    def test1_immortals(self):
        print('\n---------------- %s' % self)

        id1 = ID.parse('moki@4WDfe3zZ4T7opFSi3iDAKiuTnUHjxmXekk')
        meta = g_facebook.meta(identifier=id1)
        if meta is not None:
            moki = g_facebook.user(identifier=id1)
            print('moki: ', moki)


# class CommandTestCase(unittest.TestCase):
#
#     def test1_receipt(self):
#         print('\n---------------- %s' % self)
#
#         content = ReceiptCommand(message='OK!')
#         print('receipt: %s' % content)


class CryptoTestCase(unittest.TestCase):

    def __test_keccak(self, string: str, exp: str):
        data = string.encode('utf-8')
        d = keccak256(data)
        res = Hex.encode(d)
        print('Keccak256 ( %s ):\n\t%s' % (string, res))
        self.assertEqual(exp, res)

    def test1_keccak(self):
        print('\n---------------- %s' % self)
        exp = '96b07f3103d45cc7df2dd6e597922a17f48c86257dffe790d442bbd1ff46514d'
        self.__test_keccak(string='moky', exp=exp)

        exp = '1c8aff950685c2ed4bc3174f3472287b56d9517b9c948127319a09a7a36deac8'
        self.__test_keccak(string='hello', exp=exp)

        exp = '4e03657aea45a94fc7d47ba826c8d667c0d1e6e33a64a036ec44f58fa12d6c45'
        self.__test_keccak(string='abc', exp=exp)

        data = '04' \
               '50863ad64a87ae8a2fe83c1af1a8403cb53f53e486d8511dad8a04887e5b2352' \
               '2cd470243453a299fa9e77237716103abc11a1df38855ed6f2ee187e9c582ba6'
        exp = 'fc12ad814631ba689f7abe671016f75c54c607f082ae6b0881fac0abeda21781'
        self.__test_keccak(string=data, exp=exp)

    @staticmethod
    def __public_key(pem: str) -> PublicKey:
        p_key = PublicKey.parse({
            'algorithm': 'ECC',
            'data': pem,
        })
        print('public key: %s' % p_key)
        return p_key

    @staticmethod
    def __private_key(pem: str) -> PrivateKey:
        s_key = PrivateKey.parse({
            'algorithm': 'ECC',
            'data': pem,
        })
        print('private key: %s' % s_key)
        pri = s_key.data
        print('private data: %s' % Hex.encode(pri))

        p_key = s_key.public_key
        print('public key: %s' % p_key)

        pub = p_key.data
        print('pub data: %s' % Hex.encode(pub))
        return s_key

    def __test_eth_address(self, pem: str, exp: str):
        s_key = self.__private_key(pem=pem)
        p_key = s_key.public_key
        pub = p_key.data
        address = ETHAddress.from_data(fingerprint=pub)
        print('ETH address: %s' % address)
        self.assertEqual(exp, address)

    def __test_eth_meta(self, pem: str, exp: str):
        s_key = self.__private_key(pem=pem)
        p_key = s_key.public_key

        pub = p_key.data
        sig = s_key.sign(pub)
        print('signature: %s' % Hex.encode(sig))
        ok = p_key.verify(pub, sig)
        self.assertTrue(ok)

        pub = Hex.encode(data=p_key.data)
        meta = ETHMeta({
            'type': MetaType.ETH.value,
            'key': {
                'algorithm': 'ECC',
                'data': pub
            },
        })
        identifier = meta.generate_address(network=EntityType.USER)
        print('ETH identifier: %s' % identifier)
        self.assertEqual(identifier, exp)

    def test2_eth(self):
        print('\n---------------- %s' % self)
        pem = '18e14a7b6a307f426a94f8114701e7c8e774e7f9a47e2c2035db29a206321725'
        exp = '0x3E9003153d9A39D3f57B126b0c38513D5e289c3E'
        self.__test_eth_address(pem=pem, exp=exp)
        self.__test_eth_meta(pem=pem, exp=exp)

        s_key = self.__private_key('')
        print('generate private key: %s' % s_key)

        s_key = self.__private_key(pem='-----BEGIN PRIVATE KEY-----\n\
MIGNAgEAMBAGByqGSM49AgEGBSuBBAAKBHYwdAIBAQQgRc9oT0qckFAW57khXTzbWXWX1Kcy3St5\n\
hiSV1fx9YZagBwYFK4EEAAqhRANCAASYjO9EH0g7K/8/IB/VQaDDSMNK38lPLedpBbBo9yi6ttR1\n\
MY/5Zguh/nrE2EzI6Bk7yW3F6b2LMr9X031ydzlR\n\
-----END PRIVATE KEY-----')
        print('private key: %s' % s_key)

        p_key = s_key.public_key
        print('public key: %s' % p_key)
        pub = p_key.data
        print('pub data: %s' % Hex.encode(pub))

        p_key = self.__public_key(pem='-----BEGIN PUBLIC KEY-----\n\
MFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAEmIzvRB9IOyv/PyAf1UGgw0jDSt/JTy3naQWwaPcourbU\n\
dTGP+WYLof56xNhMyOgZO8ltxem9izK/V9N9cnc5UQ==\n\
-----END PUBLIC KEY-----')
        print('public key: %s' % p_key)
        pub = p_key.data
        print('pub data: %s' % Hex.encode(pub))

        data = 'moky'.encode('utf-8')
        sig = s_key.sign(data=data)
        print('signature : %s' % Hex.encode(sig))
        ok = p_key.verify(data, sig)
        self.assertTrue(ok)
        exp = '3046022100da3774377c56165d400567d205f01a416599c800c6a3e08e6297f2' \
              'c8d234b5f80221008370153e800db98880cd012fec439304c5ece48ee2636303' \
              'fc001d463d14b311'
        print('signature2: %s' % exp)
        ok = p_key.verify(data, Hex.decode(exp))
        self.assertTrue(ok)

    def test3_aes(self):
        print('\n---------------- %s' % self)
        key = SymmetricKey.parse(key={
            'algorithm': SymmetricKey.AES,
        })
        data = 'moky'.encode('utf-8')
        ciphertext = key.encrypt(data=data)
        plaintext = key.decrypt(data=ciphertext)
        print('AES decrypt: %s' % plaintext)
        self.assertEqual(data, plaintext, 'AES error')


if __name__ == '__main__':
    unittest.main()
