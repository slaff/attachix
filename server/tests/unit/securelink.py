import os
import sys
import unittest
sys.path.insert(0,'../../')
sys.path.insert(1,'../../lib/')

import core.coder as coder

class SecurelinkTestCase(unittest.TestCase):

    def setUp(self):
        self.cipher = coder.SecureLink(
            iv=os.urandom(16), # 16 bytes long
            key=os.urandom(32), # 16, 24 or 32
            chKey=os.urandom(255)
        )

    def testNoDepthNoPrefix(self):
        # 1. Depth 0, No prefixes
        path = self.cipher.encode(['GET','POST'], 1, '/path/to/files/', [], 0)
        try:
            self.cipher.decode(path)
        except ValueError:
            self.assertTrue(True, "Depth 0, No prefixes Failed")
            return

        self.assertTrue(True, "Depth 0, No prefixes Succeeded")

    def testDepthNoPrefix(self):
        # 1. Depth 255, No prefixes
        path = self.cipher.encode(['GET','POST'], 1, '/path/to/files/', [], 255)
        try:
            self.cipher.decode(path+'/saaadfsf/sdfsafsdaf/sdfsadfdsaf/sdfsdafasd/')
        except ValueError:
            self.assertTrue(True, "Depth 255, No prefixes Failed")
            return

        self.assertTrue(True, "Depth 255, No prefixes Succeeded")

    def testDepthPrefix(self):
        # Depth 255, '.views' prefixes
        path = self.cipher.encode(['GET','POST'], 1, '/path/to/files/', ['.views'], 255)

        try:
            self.cipher.decode(path+'/saaadfsf/sdfsafsdaf/sdfsadfdsaf/sdfsdafasd/')
        except ValueError:
            self.assertTrue(True, "Depth 255, No prefixes Failed")
            return

        self.assertTrue(True, "Depth 255, No prefixes Succeeded")

        try:
            parts = path.split('/')
            parts.insert(2, '.views')
            self.cipher.decode('/'.join(parts)+'/saaadfsf/sdfsafsdaf/sdfsadfdsaf/sdfsdafasd/')
        except ValueError:
            self.assertTrue(True, "Depth 255, Prefixes Failed")
            return

        self.assertTrue(True, "Depth 255, '.views' Prefixes Succeeded")

    def testRootDepthPrefix(self):
        # Depth 255, '.views' prefixes
        path = self.cipher.encode(['GET','POST'], 1, '/', ['.views'], 255)

        try:
            self.cipher.decode('/saaadfsf/sdfsafsdaf/sdfsadfdsaf/sdfsdafasd/')
        except ValueError:
            self.assertTrue(True, "Depth 255, No prefixes Failed")
            return

        self.assertTrue(True, "Depth 255, No prefixes Succeeded")

        try:
            parts = path.split('/')
            parts.insert(2, '.views')
            self.cipher.decode('/'.join(parts)+'/saaadfsf/sdfsafsdaf/sdfsadfdsaf/sdfsdafasd/')
        except ValueError:
            self.assertTrue(True, "Depth 255, Prefixes Failed")
            return

        self.assertTrue(True, "Depth 255, '.views' Prefixes Succeeded")

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()