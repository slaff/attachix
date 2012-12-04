import os
import sys
import unittest
sys.path.insert(0,'../../')
sys.path.insert(1,'../../lib/')

import core.coder

class CoderTestCase(unittest.TestCase):

    def setUp(self):
        self.cipher = core.coder.Secure(
            iv=os.urandom(16), # 16 bytes long
            key=os.urandom(32), # 16, 24 or 32
        )

        self.clearText = '''
        ARC4 is short for "Alleged RC4". In September of 1994, someone posted C code to both the Cypherpunks mailing list and to the Usenet newsgroup sci.crypt, claiming that it implemented the RC4 algorithm. This claim turned out to be correct. Note that there's a damaging class of weak RC4 keys; this module won't warn you about such keys.

A similar anonymous posting was made for Alleged RC2 in January, 1996.

An example usage of the DES module:

>>> from Crypto.Cipher import DES
>>> obj=DES.new('abcdefgh', DES.MODE_ECB)
>>> plain="Guido van Rossum is a space alien."
>>> len(plain)
34
>>> obj.encrypt(plain)
Traceback (innermost last):
  File "<stdin>", line 1, in ?
ValueError: Strings for DES must be a multiple of 8 in length
>>> ciph=obj.encrypt(plain+'XXXXXX')
>>> ciph
'\021,\343Nq\214DY\337T\342pA\372\255\311s\210\363,\300j\330\250\312\347\342I\3215w\03561\303dgb/\006'
>>> obj.decrypt(ciph)
'Guido van Rossum is a space alien.XXXXXX'
        '''

    def testSimple(self):
        encodedText = self.cipher.encode(self.clearText)
        self.assertEquals(self.clearText, self.cipher.decode(encodedText))

    def testNegativeSimple(self):
        encodedText = self.cipher.encode(self.clearText)
        self.assertNotEquals(self.clearText[0:10], self.cipher.decode(encodedText))

    def testBase64(self):
        encodedText = self.cipher.encode(self.clearText, True)
        self.assertEquals(self.clearText, self.cipher.decode(encodedText, True))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()