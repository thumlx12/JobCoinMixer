import uuid
import hashlib
import random, string
from sets import Set
import urllib2
import urllib
import time
import json


class Mixer:
    THEHOUSE = ""
    TRANS_URL = 'http://jobcoin.gemini.com/cabdriver/api/transactions'

    depositAddrSet = Set() #store all deposit addresses
    deposit2withdraw = {} #key: deposit address, value: withdraw address that is linked to the deposit address
    depoAddrFund = {} #key: deposit address, value: how much JobCoin left in the address

    trans_content_len = 0
    trans_log_num = []

    def __init__(self):
        '''
        1. Use uuid and sha224 hash function to generate unique House Account Address.
        2. Get a snapshot of the transanction log page so that we can monitor transaction changes.
        '''
        self.THEHOUSE = hashlib.sha224(str(uuid.uuid1())).hexdigest()
        self.trans_content_len = self.getTransLogContentLen()
        self.trans_log_num = len(json.loads(self.getTransLog()))

    def getTransLogContentLen(self):
        '''
        :return: the length of the content of the transaction page
        '''
        request = urllib2.Request(self.TRANS_URL)
        request.get_method = lambda: 'HEAD'
        response = urllib2.urlopen(request)
        return response.info()["Content-Length"]

    def getTransLog(self):
        '''
        :return: the content (as a string) of the transaction page
        '''
        req = urllib2.Request(self.TRANS_URL)
        response = urllib2.urlopen(req)
        return response.read()

    def genSaltString(self, length):
        '''
        :param length: anticipated length of the salt string
        :return: the salt string
        '''
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    def genDepositAddress(self, withdrawAddress, addressList):
        '''
        :param withdrawAddress: the withdraw address provided by the user
        :param addressList: a list of new, unused addresses that the user owns
        :return: a unique deposit address
        '''
        salt = self.genSaltString(random.randint(1, 20))
        adrListStr = ','.join(addressList)
        depositAddress = hashlib.sha224(adrListStr + salt).hexdigest()
        self.deposit2withdraw[depositAddress] = withdrawAddress
        self.depositAddrSet.add(depositAddress)
        return depositAddress

    def sendJobCoin(self, fromAddr, toAddr, amount):
        '''
        :param fromAddr: sender's address
        :param toAddr: receiver's address
        :param amount: the amount of JobCoin
        :return: the status code
        '''
        trans = {'fromAddress': fromAddr, 'toAddress': toAddr, 'amount': str(amount)}
        data = urllib.urlencode(trans)
        req = urllib2.Request(self.TRANS_URL, data)
        response = urllib2.urlopen(req)
        try:
            print('Transaction is a success', trans)
        except:
            print(response.read())
        finally:
            return response.code

    def monitorTrans(self):
        '''
        Monitor the transactions of JobCoin. (in 5-second time granularity)
        If anyone sends money to any one of the deposit addresses,
        this method will then transfer the money to the House Account.
        :return:
        '''
        while True:
            curTransLogContentLen = self.getTransLogContentLen()
            if curTransLogContentLen != self.trans_content_len:
                self.trans_content_len = curTransLogContentLen
                curTransLog = json.loads(self.getTransLog())
                for i in range(self.trans_log_num, len(curTransLog)):
                    if self.depositAddrSet.__contains__(curTransLog[i]['toAddress']):
                        amount = curTransLog[i]['amount']
                        oneDepositAddr = curTransLog[i]['toAddress']
                        if not self.depoAddrFund.has_key(oneDepositAddr):
                            self.depoAddrFund[oneDepositAddr] = 0.0
                        self.depoAddrFund[oneDepositAddr] += float(amount)
                        time.sleep(1)
                        self.sendJobCoin(oneDepositAddr, self.THEHOUSE, amount)
                self.trans_log_num = len(curTransLog)
            time.sleep(5)

    def doleoutCoin(self):
        '''
        Dole out a user's all JobCoin to his withdraw address in several times.
        :return:
        '''
        while True:
            for DA in self.deposit2withdraw.keys():
                if self.depoAddrFund.has_key(DA):
                    if self.depoAddrFund[DA] > 0.0:
                        doleAmount = self.depoAddrFund[DA] \
                            if self.depoAddrFund[DA] < 0.1 \
                            else random.uniform(0.2, 0.5) * self.depoAddrFund[DA]
                        self.depoAddrFund[DA] -= doleAmount
                        self.sendJobCoin(self.THEHOUSE, self.deposit2withdraw[DA], doleAmount)
                        print('Dole out %s JobCoin to %s successfully.' % (doleAmount, self.deposit2withdraw[DA]))
            time.sleep(5)
