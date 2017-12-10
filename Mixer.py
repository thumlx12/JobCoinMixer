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

    depositAddrSet = Set()
    deposit2withdraw = {}
    depoAddrFund = {}

    trans_content_len = 0
    trans_log_num = []

    def __init__(self):
        self.THEHOUSE = hashlib.sha224(str(uuid.uuid1())).hexdigest()
        self.trans_content_len = self.getTransLogLen()
        self.trans_log_num = len(json.loads(self.getTransLog()))

    def getTransLogLen(self):
        request = urllib2.Request(self.TRANS_URL)
        request.get_method = lambda: 'HEAD'
        response = urllib2.urlopen(request)
        return response.info()["Content-Length"]

    def getTransLog(self):
        req = urllib2.Request(self.TRANS_URL)
        response = urllib2.urlopen(req)
        return response.read()

    def genSaltString(self, length):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    def genDepositAddress(self, withdrawAddress, addressList):
        salt = self.genSaltString(random.randint(1, 20))
        adrListStr = ','.join(addressList)
        depositAddress = hashlib.sha224(adrListStr + salt).hexdigest()
        self.deposit2withdraw[depositAddress] = withdrawAddress
        self.depositAddrSet.add(depositAddress)
        return depositAddress

    def sendJobCoin(self, fromAddr, toAddr, amount):
        trans = {'fromAddress': fromAddr, 'toAddress': toAddr, 'amount': str(amount)}
        data = urllib.urlencode(trans)
        req = urllib2.Request(self.TRANS_URL, data)
        response = urllib2.urlopen(req)
        try:
            print('Transaction is a success', trans)
        except:
            print(response.read())

    def monitorTrans(self):
        while True:
            curTransLogLen = self.getTransLogLen()
            if curTransLogLen != self.trans_content_len:
                self.trans_content_len = curTransLogLen
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
            time.sleep(10)

    def doleOutCoin(self):
        while True:
            for DA in self.deposit2withdraw.keys():
                if self.depoAddrFund.has_key(DA):
                    if self.depoAddrFund[DA] > 0.0:
                        doleAmount = self.depoAddrFund[DA] if self.depoAddrFund[DA] < 0.1 else 0.3 * self.depoAddrFund[
                            DA]
                        self.depoAddrFund[DA] -= doleAmount
                        self.sendJobCoin(self.THEHOUSE, self.deposit2withdraw[DA], doleAmount)
                        print('Dole out %s JobCoin to %s successfully.' % (doleAmount, self.deposit2withdraw[DA]))
            time.sleep(10)
