from Mixer import *
import threading

if __name__ == "__main__":
    userAddressList1 = ['BobAdd1', 'BobAdd2', 'BobAdd3', 'BobAdd4', 'BobAdd5']
    withdrawAddr1 = 'Bob\'s_secret_vault'

    userAddressList2 = ['CaroAdd1', 'CaroAdd2', 'Caroadd3', 'CaroAdd4']
    withdrawAddr2 = 'Caro\'s_secret_cache'

    myMixer = Mixer()
    print('The House Account is:', myMixer.THEHOUSE)

    deposit_addr1 = myMixer.genDepositAddress(withdrawAddr1, userAddressList1)
    print('Bob\'s Deposit Address is:', deposit_addr1)

    deposit_addr2 = myMixer.genDepositAddress(withdrawAddr2, userAddressList2)
    print('Caro\'s Deposit Address is:', deposit_addr2)

    t1 = threading.Thread(target=myMixer.monitorTrans, args=())
    t1.start()
    t2 = threading.Thread(target=myMixer.doleoutCoin, args=())
    t2.start()