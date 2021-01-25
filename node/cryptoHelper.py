import binascii
from Crypto.PublicKey import RSA
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme
from Crypto.Hash import SHA256
import json
import index
from loggerWrapper import LoggerWrapper

log = LoggerWrapper(__name__, index.PATH).logger


class CryptoHelper:

    def __init__(self):
        pk = ''
        with open(index.PK_LOC, 'rb') as f:
            pk = f.read()
        
        self.privateKey = RSA.import_key(pk)


    def getDigest(self, byteString):
        return SHA256.new(byteString).hexdigest()


    def isVerified(self, signature, byteString):
        pass


    def signPrePrepareMessage(self, phase, viewNum, seqNum, digest):
        byteString = f'{phase},{viewNum},{seqNum},{digest}'.encode('utf-8')
        return self.__getSignature(byteString)
    

    def signPBFTMessage(self, phase, viewNum, seqNum, digest, fromNode):
        byteString = f'{phase},{viewNum},{seqNum},{fromNode},{digest}'.encode('utf-8')
        return self.__getSignature(byteString)


    def __getSignature(self, byteString):
        hashValue = SHA256.new(byteString)
        signer = PKCS115_SigScheme(self.privateKey)
        signatureByte = signer.sign(hashValue)
        signatureStr = binascii.hexlify(signatureByte).decode('utf-8')
        log.debug(f'signature is {signatureStr}')
        return signatureStr


    def __verifySignature(self, signature, byteString):

        hashValue = SHA256.new(msg)
        isVerified = False
        verifier = PKCS115_SigScheme(pubKey)
        try:
            verifier.verify(hashValue, signature)
            log.debug("Signature is valid.")
            isVerified = True
        except:
            log.error("Signature is invalid.")
        
        return isVerified