from math import *
from web3 import Web3
from web3.middleware import geth_poa_middleware
from ..Common import *


# pip install web3
class MetaMask(object):
    web3 = None
    contract = None
    host = ''
    chainId = 0
    contractPath = ''
    keyPath = ''
    abi = None
    addr = ''

    def __init__(self, host, chainId, contract='contract', addr=''):
        self.host = host
        self.chainId = chainId
        self.web3 = self.createWeb3(host)

        self.contractPath = root_path() + '/contract'
        self.keyPath = self.contractPath + '/keystore'
        makedir(self.contractPath)
        makedir(self.keyPath)
        abi = file_get_contents(self.contractPath + '/' + contract + '.abi')
        if abi is None:
            print("Cann't read the abi file")
            exit(0)
        self.abi = json_decode(abi)
        if len(addr) == 0:
            addr = file_get_contents(self.contractPath + '/' + contract + '.addr')
            if addr is None:
                print("Cann't read the addr file")
                exit(0)
        self.addr = Web3.toChecksumAddress(addr.lower())

        self.contract = self.web3.eth.contract(address=self.addr, abi=self.abi)

    def createWeb3(self, host, timeout=60):
        web3 = Web3(Web3.HTTPProvider(host, request_kwargs={'timeout': timeout}))
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)  # 注入poa中间件，解决兼容问题
        return web3

    # 获取余额
    def getBalance(self, account, scale=8, decimals=0):
        account = Web3.toChecksumAddress(account.lower())
        try:
            res = self.contract.functions.balanceOf(account).call()  # 合约方法
        except Exception as ex:
            print(str(ex))
            res = self.web3.eth.get_balance(account)  # RPC方法
        return Decimal(str(self.decodeValue(res, scale, decimals)))

    # 获取hash数据
    def getHashData(self, hashStr, host=''):
        web3 = self.createWeb3(host) if len(host) > 0 else self.web3
        res = None
        try:
            res = web3.eth.get_transaction_by_block(hashStr)
        except Exception as ex:
            print(str(ex))
            exit(0)
        return res

    # 判断hash数据是否正确
    def checkHashData(self, hashStr, froms, to, price=0, host=''):
        res = self.getHashData(hashStr, host)
        priceCorrect = True
        if float(price) > 0:
            value = float(self.decodeValue(int(res['value'], 16)))
            priceCorrect = value != float(price)
        return froms.lower() == res['from'].lower() and to.lower() == res['to'].lower() and priceCorrect

    # 获取精度
    def getDecimals(self):
        decimals = 18
        try:
            res = self.contract.functions.decimals().call()
            if int(res) > 0:
                decimals = res
        except Exception as ex:
            print(str(ex))
        return int(decimals)

    # 上链金额检测(上链时必须加精度)
    def setValue(self, value, add_decimals=True):
        if add_decimals:
            if '.' in str(value) or len(str(value)) < 8:
                value = self.encodeValue(value)
        else:
            if '.' not in str(value) and len(str(value)) > 8:
                value = self.decodeValue(value)
        return value

    # 金额加精度
    def encodeValue(self, value, decimals=0):
        if is_numeric(value):
            if float(value) < 0:
                print('Amount cannot be negative')
                exit(0)
            if decimals <= 0:
                decimals = self.getDecimals()
            value = Decimal(str(value)) * Decimal('1'+'0'*decimals)
        return str(value)

    # 金额去精度
    def decodeValue(self, value, scale=8, decimals=0):
        if decimals <= 0:
            decimals = self.getDecimals()
        # return round(Decimal(str(value)) / Decimal('1'+'0'*decimals), scale)
        amount = Decimal(str(value)) / Decimal('1'+'0'*decimals)
        if is_numeric(amount):
            amounts = str(amount).split('.')
            amount = amounts[0]
            if len(amounts) > 1:
                amount += '.'+amounts[1][:decimals]
        else:
            if preg_match(r'\d{'+str(decimals)+r'}$', value):
                amount = preg_replace(r'(\d{'+str(decimals)+r'})$', r'.\1', value)
            else:
                amount = '0'*decimals + value
                amount = preg_replace(r'(\d{'+str(decimals)+r'})$', r'.\1', amount)
                amount = '0' + preg_replace(r'^0+', '', amount)
        amounts = str(amount).split('.')
        amount = amounts[0]
        if len(amounts) > 1:
            amount += '.'+amounts[1][:scale]
        return amount

    # 10进制转16进制
    def decHex(self, dec, isPrefix=False):
        res = hex(int(dec)).split('x')[-1]
        if isPrefix:
            res = '0x' + res
        return res

    # 16进制转10进制
    def hexDec(self, hexStr):
        return int(hexStr, 16)

    # 获取gasPrice
    def gasPrice(self, default_gwei=1):
        res = int(self.web3.eth.gas_price)
        gwei = ceil(float(Decimal(str(res)) / (Decimal(str(default_gwei)) * Decimal('1'+'0'*9))))
        return str(gwei)

    # 执行并估算一个交易需要的gas用量
    def estimateGas(self, row, default_gas=1800000):
        arr = {
            'from': row['from'],
            'to': row['to'] if 'to' in row.keys() else '',
            'data': row['data'] if 'data' in row.keys() else '',
        }
        try:
            res = self.web3.eth.estimate_gas(arr)
            res = int(res)
            if res < 0:
                res = default_gas
        except Exception as ex:
            print(str(ex))
            res = default_gas
        return Decimal(str(ceil(Decimal(str(res)) / Decimal('10000')))) * Decimal('10000') + Decimal('10000')

    # 生成矿工费选项
    def createGas(self, froms, gas=1800000):
        return {
            'from': Web3.toChecksumAddress(froms.lower()),
            'gas': self.decHex(gas, True)
        }

    # 生成交易数据
    def transactionData(self, raw, froms, to='', value='', default_gas=1800000, default_gwei=1):
        # 返回指定地址发生的交易数量
        nonce = ''
        try:
            nonce = self.web3.eth.get_transaction_count(Web3.toChecksumAddress(froms.lower()))
        except Exception as ex:
            print(str(ex))
            exit(0)
        raw['from'] = Web3.toChecksumAddress(froms.lower())
        if len(to) > 0:
            raw['to'] = Web3.toChecksumAddress(to.lower())
        # raw['gasPrice'] = self.decHex(self.web3.toWei(self.gasPrice(default_gwei), 'gwei'), True)
        # raw['gasLimit'] = self.decHex(int(self.estimateGas(raw, default_gas)), True)
        if len(str(value)) == 0:
            value = 0
        raw['value'] = self.decHex(value, True)
        raw['chainId'] = self.chainId
        raw['nonce'] = self.decHex(nonce, True)
        # write_log(raw, self.contractPath + '/log.txt')
        # 获取签名
        file = self.keyPath + '/' + (froms[2:] if froms[0:2] == '0x' else froms) + '.json'
        if os.path.isfile(file) is False:
            print('The certificate file does not exist')
            exit(0)
        credential = self.web3.eth.account.sign_transaction(raw, private_key=ethParam['private_key'])
        return credential.rawTransaction

    # 转账交易
    def transfer(self, froms, to, value):
        hashStr = ''
        try:
            # self.web3.toWei(value, 'ether')
            value = self.encodeValue(value)
            raw = self.contract.functions.transfer(Web3.toChecksumAddress(to.lower()), value).build_transaction(self.createGas(froms))
            # 发起裸交易
            hashStr = self.web3.eth.send_raw_transaction(self.transactionData(raw, froms, Web3.toChecksumAddress(to.lower()), value))
            hashStr = self.web3.toHex(hashStr)
        except Exception as ex:
            print(str(ex))
            exit(0)
        return self.waitForTransaction(hashStr)

    # 循环获取到hash数据为止
    def waitForTransaction(self, hashStr, host='', timeout=60, interval=1):
        web3 = self.createWeb3(host) if len(host) > 0 else self.web3
        now = timestamp()
        while True:
            try:
                res = web3.eth.get_transaction_by_block(hashStr)
                if res is not None:
                    break
                if timestamp() - now > timeout:
                    break
                time.sleep(interval)
            except Exception as ex:
                print(str(ex))
                exit(0)
        return res
