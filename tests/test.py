#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    DIM SDK Test
    ~~~~~~~~~~~~

    Unit test for DIM-SDK
"""
import os
import sys
path = os.path.abspath(__file__)
path = os.path.dirname(path)
path = os.path.dirname(path)
sys.path.insert(0, os.path.join(path, 'sdk'))
sys.path.insert(0, os.path.join(path, 'plugins'))

import asyncio
import unittest

from dimsdk import *
from dimsdk.plugins import *
from plugins.dimplugins import *

from tests.database import CommonFacebook


ExtensionLoader().run()
PluginLoader().run()

g_facebook = CommonFacebook()

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

        # moki_meta = g_immortals.get_meta(identifier=moki_id)
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
        # moki = g_immortals.get_user(identifier=moki_id)
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
        asyncio.run(self.__check_user())

    # noinspection PyMethodMayBeStatic
    async def __check_user(self):
        id1 = ID.parse('moki@4WDfe3zZ4T7opFSi3iDAKiuTnUHjxmXekk')
        meta = await g_facebook.get_meta(identifier=id1)
        if meta is not None:
            moki = await g_facebook.get_user(identifier=id1)
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
        meta = Meta.parse(meta={
            'type': Meta.ETH,
            'key': {
                'algorithm': 'ECC',
                'data': pub
            },
        })
        valid = meta.valid
        identifier = meta.generate_address(network=EntityType.USER)
        print('ETH identifier: %s (%s)' % (identifier, valid))
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
        extra = {}
        key = SymmetricKey.parse(key={
            'algorithm': SymmetricKey.AES,
        })
        data = 'moky'.encode('utf-8')
        ciphertext = key.encrypt(data=data, extra=extra)
        plaintext = key.decrypt(data=ciphertext, params=extra)
        print('AES decrypt: %s' % plaintext)
        self.assertEqual(data, plaintext, 'AES error')

    def test8_rsa(self):
        print('\n---------------- %s' % self)
        data = 'moky'.encode('utf-8')
        extra = {}
        # public key
        pem = '{"algorithm":"RSA","data":"-----BEGIN RSA PUBLIC KEY-----\\r\\n' \
              'MIGJAoGBAL3T0ETpSg4gT394+0JLtDhjpA869fiRkBBiXriX30KEjIzPs41YIwZz' \
              'sV9jP0Pdc/7vjxy8jwhD0Gd3481/BTCKgVS6KPJhxxedWB6G3owqdPE05RLZ8ci2' \
              'gz7kBuDNGsIWnkrs9MjqM5U7cwSgEAtfZiwJfPx67QdEYiOlFDFvAgMBAAE=\\r\\n' \
              '-----END RSA PUBLIC KEY-----"}'
        info = JSON.decode(string=pem)
        key = PublicKey.parse(key=info)
        ciphertext = key.encrypt(data=data, extra=extra)
        b64 = Base64.encode(data=ciphertext)
        print('RSA encrypt: %s' % b64)
        # private key
        pem = '{"algorithm": "RSA", "data": "-----BEGIN RSA PRIVATE KEY-----\\r\\n' \
              'MIICXAIBAAKBgQC909BE6UoOIE9/ePtCS7Q4Y6QPOvX4kZAQYl64l99ChIyMz7ON' \
              'WCMGc7FfYz9D3XP+748cvI8IQ9Bnd+PNfwUwioFUuijyYccXnVgeht6MKnTxNOUS' \
              '2fHItoM+5AbgzRrCFp5K7PTI6jOVO3MEoBALX2YsCXz8eu0HRGIjpRQxbwIDAQAB' \
              'AoGACP5dEra+1HaBbbesp9JwYm+OGU6g0rsKyUvv0u0XHc6r3gwFJMA1QJwAnlVU' \
              'bQGz+jMdY64nVKvp1s0eVOEcvMAdVuvhvX1JyY7BiavHXBybtA+RoMO2QmCF6kQe' \
              'qspJNsCDSANQNEr9mtlMXFZ9MFWlWHw+9JmsbJLvfFiwKLkCQQDjCggtlnoi2IO/' \
              'KFafXMdeiS5vmSU+t4MqU9lZ+yita7MjC4TNnW9M4scFsFAp1Y00vjTgTZ0DkL+U' \
              '0VfEOH0tAkEA1gqhSXzWey2pq/fYnXdjrQSv8z7fuiS+2JcM/NGEw0J4wRzUlY2i' \
              'EeeyrjMHVYkplsV4jhCM19J9VF+iZJFiiwJAP09V1niGmF7t5gk2lnvFsIvqYf4/' \
              'j4yWy9/T1S6fOjS1IEme/8Mt/S+jtedjgzbkiFed4QpjhVIAylvR8IqcBQJBAK77' \
              'B7n1Jb6TqPceambo+IK0p0cbanlZmu+kJQj2HCwoxmFROXV90TYEDe4dZ2yE8owA' \
              'qbqySwIRYUY93JuMw1sCQCGzkuu0LDfiCtSBdQhly5xci85sm/LnGbn4JRXHlDhF' \
              'd6VX8pmjQoHvHNFgPuzF4vu+0vZdirJNi4PQzSQeFmc=\\r\\n' \
              '-----END RSA PRIVATE KEY-----"}'
        info = JSON.decode(string=pem)
        key = PrivateKey.parse(key=info)
        assert isinstance(key, DecryptKey), 'RSA key error: %s' % key
        plaintext = key.decrypt(data=ciphertext, params=extra)
        name = UTF8.decode(data=plaintext)
        print('RSA decrypt: %s' % name)
        self.assertEqual(data, plaintext, 'RSA error')
        # dart
        drt = 'Jtp47h1gHGqJrgpTYn6xa+yj4QvLoOIlUhRXCpKKgqXDZU+ELyTlbCeihHjlPm4p' \
              'ZY2nnEk81BbgMM5ANO/Sr+/7FxAHgNVQP8MEYKJuPJ/4vcQid0Sc/r25L4Q/DXgP' \
              'RL1byk0X4oc4OPlM0+NtJXOZ/jf3IPjjaYMs7zZB1fE='
        ciphertext = Base64.decode(string=drt)
        plaintext = key.decrypt(data=ciphertext, params=extra)
        name = UTF8.decode(data=plaintext)
        print('RSA decrypt: %s' % name)
        # # AES
        # drt = 'HP4uOKPVHpf3y1VNwqUR7ymerRzq6HvzPk6H0WNIbv4928ix+fpTKvvwBBxAaGmZ' \
        #       'ge45W1GeewXX4vzxrDBz6OP7tYskW62QzfLUE19/d3oVVK5pkM6q9gbJ1flPyWJN' \
        #       'aXXYqsng9qdovamYc/YtOdqgR7cFY5DtucnibrgSiTk='
        # ciphertext = Base64.decode(string=drt)
        # plaintext = key.decrypt(data=ciphertext, params=extra)
        # aes = UTF8.decode(data=plaintext)
        # print('RSA decrypt: %s' % aes)


if __name__ == '__main__':
    unittest.main()
