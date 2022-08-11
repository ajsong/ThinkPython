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
    abi = None
    addr = ''
    privateKey = ''

    def __init__(self, host, chainId, contract='contract', addr=''):
        self.host = host
        self.chainId = chainId
        self.contractPath = root_path() + '/contract'
        makedir(self.contractPath)
        abi = file_get_contents(self.contractPath + '/' + contract + '.abi')
        self.abi = json_decode(abi)
        if len(addr) == 0:
            addr = file_get_contents(self.contractPath + '/' + contract + '.addr')
        self.addr = self.address(addr)

        self.web3 = self.createWeb3(host)
        self.contract = self.web3.eth.contract(address=self.addr, abi=self.abi)

    def createWeb3(self, host, timeout=60):
        web3 = Web3(Web3.HTTPProvider(host, request_kwargs={'timeout': timeout}))
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)  # 注入poa中间件，解决兼容问题
        return web3

    # ChecksumAddress
    def address(self, account):
        return Web3.toChecksumAddress(account.lower())

    # 获取余额
    def getBalance(self, account, scale=8, decimals=0):
        account = self.address(account)
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
            value = int(Decimal(str(value)) * Decimal('1'+'0'*decimals))
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

    # 打印所有方法
    def functions(self):
        for func in self.contract.all_functions():
            print(func)

    # 获取gasPrice
    def gasPrice(self, default_gwei=1):
        res = int(self.web3.eth.gas_price)
        gwei = int(Decimal(str(res)) / (Decimal(str(default_gwei)) * Decimal('1'+'0'*9)))
        return str(gwei)

    # 生成矿工费选项
    def createGas(self, froms, gas=1800000, default_gwei=1):
        return {
            'from': self.address(froms),
            'gas': self.decHex(gas, True),
            'gasPrice': self.decHex(self.web3.toWei(self.gasPrice(default_gwei), 'gwei'), True)
        }

    # 生成交易数据
    def transactionData(self, raw, froms, to=''):
        # 返回指定地址发生的交易数量
        nonce = ''
        try:
            nonce = self.web3.eth.get_transaction_count(self.address(froms))
        except Exception as ex:
            print(str(ex))
            exit(0)
        raw['from'] = self.address(froms)
        if len(to) > 0: raw['to'] = self.address(to)  # 存在to即是走链通道, 不存在即是走合约通道
        raw['chainId'] = self.chainId
        raw['nonce'] = self.decHex(nonce, True)
        # write_log(raw, self.contractPath + '/log.txt')
        private_key = self.privateKey
        if len(private_key) == 0:
            try:
                private_key = ethParam['private_key']
            except Exception as ex:
                print(str(ex))
                exit(0)
        credential = self.web3.eth.account.sign_transaction(raw, private_key=private_key)
        return credential.rawTransaction

    # 转账交易
    def transfer(self, froms, to, value):
        hashStr = ''
        try:
            raw = self.contract.functions.transfer(self.address(to), int(self.setValue(value))).build_transaction(self.createGas(froms))
            # 发起裸交易
            hashStr = self.web3.eth.send_raw_transaction(self.transactionData(raw, froms))
            hashStr = self.web3.toHex(hashStr)
        except Exception as ex:
            print(str(ex))
            exit(0)
        res = self.web3.eth.wait_for_transaction_receipt(hashStr)
        return self.web3.toHex(res.get('transactionHash', ''))
        # return hashStr
