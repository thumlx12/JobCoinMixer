from Mixer import *
import threading
from ecdsa import SigningKey
if __name__ == "__main__":
    userAddressList1 = ['BobAddr1', 'BobAddr2', 'BobAddr3', 'BobAddr4', 'BobAddr5']
    withdrawAddr1 = 'Bob\'s_secret_vault'

    userAddressList2 = ['CaroAddr1', 'CaroAddr2', 'Caroaddr3', 'CaroAddr4','CaroAddr5']
    withdrawAddr2 = 'Caro\'s_secret_cache'

    myMixer = Mixer()
    print('The House Account is:', myMixer.THEHOUSE)

    deposit_addr1 = myMixer.genDepositAddress(withdrawAddr1, userAddressList1)
    print('Bob\'s Deposit Address is:', deposit_addr1)

    deposit_addr2 = myMixer.genDepositAddress(withdrawAddr2, userAddressList2)
    print('Caro\'s Deposit Address is:', deposit_addr2)

    myMixer.sendJobCoin('Richman', deposit_addr1, 5.32)
    myMixer.sendJobCoin('Richman', deposit_addr2, 10.22)

    t1 = threading.Thread(target=myMixer.monitorTrans, args=())
    t1.start()
    t2 = threading.Thread(target=myMixer.doleoutCoin, args=())
    t2.start()
