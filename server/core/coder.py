import time
import hashlib

from Crypto.Cipher import AES
import base64
import re

class Secure():
    def __init__(self, key, iv):
        self.key = key # aes key must be 16, 24, or 32 bytes long
        self.iv  = iv # the iv length has to be the same length as the block size
    
    """
    Encodes the content and returns base64 encoded cipher
    """
    def encode(self, content, urlSafe = False):
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        blockSize = len(self.iv)
        pad = blockSize - len(content) % blockSize
        content = content + pad * chr(pad)

        ciphertext = cipher.encrypt(content)
        if urlSafe:
            ciphertext = base64.urlsafe_b64encode(ciphertext)
            ciphertext = self._replacePadding(ciphertext, '=','_')
            
        return ciphertext
    
    def decode(self, ciphertext, urlSafe = False):
        if urlSafe:
            originalCipherText = ciphertext
            ciphertext = self._replacePadding(ciphertext, '_','=')
            ciphertext = base64.urlsafe_b64decode(ciphertext)
            if (len(ciphertext) % 16 ) != 0:
                # wrong padding, try to adjust it
                ciphertext = base64.urlsafe_b64decode(originalCipherText)
        crypter = AES.new(self.key, AES.MODE_CBC, self.iv)
        content = crypter.decrypt(ciphertext)

        return content[:-ord(content[-1])]

    def _replacePadding(self, text, find, replace):
        m = re.search('(\\'+find+')*$', text)
        if m:
            padding = m.group()
            length = len(padding)
            if length:
                text = text[0:-length] + (replace * length)
        return text

from http import normalizeUri
class SecureLink():
    def __init__(self, key, iv, chKey, skipPaths=None):
        if skipPaths is None:
            skipPaths = []
        self.cipher = Secure(key, iv)
        self.chKey  = chKey
        self.skipPaths = skipPaths

    def encode(self, methods, userId, path, prefixes=None, depth=0, expiration=3600):
        if prefixes is None:
            prefixes = []
        finalTime = time.time() + expiration

        path = normalizeUri(path)
        path = path.strip('/')
        parts = path.split('/')

        content = '/'.join([
            "%s" % finalTime,
            "%s" % len(parts),
            ','.join(methods),
            "%s" % userId,
            "%s" % depth,
            ','.join(prefixes)
        ])

        token  = self.cipher.encode(content, True)
        checkSum = hashlib.md5(token+self.chKey+path).hexdigest()

        return  "%s/%s/%s" % (token, checkSum, path)

    def decode(self, path, skipPaths=None):
        path = path.strip('/')
        
        parts = path.split('/')
        token = parts.pop(0)
        checkSum = parts.pop(0)
        if len(parts) == 0:
            parts.append('/')

        content =  self.cipher.decode(token, True)
        [finalTime, partsLen, methods, userId, depth, prefixes] = content.split('/')
        finalTime = float(finalTime)
        prefixes  = prefixes.split(',')

        if parts[0] in prefixes:
            prefix = parts.pop(0)

        if time.time() > finalTime:
            raise ValueError('Timestamp has expired')

        partsLen = int(partsLen)

        if not skipPaths:
            skipPaths = self.skipPaths
        if len(skipPaths):
            if parts[0] in skipPaths:
                # skip the URL check and checksum and
                return [finalTime, methods.split(','), userId, '/'.join(parts), partsLen]

        depth    = int(depth)
        partsToUse = parts[0:partsLen]
        leftParts  = parts[partsLen+1:]
        if len(leftParts) > depth:
            raise ValueError('Path does not match rules')

        allowedPath = '/'.join(partsToUse)
        allowedPath = allowedPath.strip('/')
        calculatedCheckSum = hashlib.md5(token+self.chKey+allowedPath).hexdigest()

        if checkSum != calculatedCheckSum:
            raise ValueError('Invalid checksum')

        return [finalTime, methods.split(','), userId, '/'.join(parts), partsLen]