from turtle import update
from solcx import (
    compile_standard,
    install_solc,
)
import json
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()
with open("./weth9.sol", "r") as file:
    wrapper = file.read()
install_solc("0.4.18")
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"weth9.sol": {"content": wrapper}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.4.18",
)
with open("compiled_wrapper.json", "w") as file:
    json.dump(compiled_sol, file)
bytecode = compiled_sol["contracts"]["weth9.sol"]["WETH9"]["evm"]["bytecode"]["object"]
abi = compiled_sol["contracts"]["weth9.sol"]["WETH9"]["abi"]

w3rinkeby = Web3(
    Web3.HTTPProvider("https://rinkeby.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161")
)

nonce = w3rinkeby.eth.getTransactionCount(os.getenv("ADDRESS"))
wrapper_onchain = w3rinkeby.eth.contract(
    address="0xc778417E063141139Fce010982780140Aa0cD5Ab", abi=abi
)
print(wrapper_onchain.functions.balanceOf(os.getenv("ADDRESS")).call())
balance_enough = wrapper_onchain.functions.balanceOf(os.getenv("ADDRESS")).call() > 0

if balance_enough is True:
    print("we got some cash")
    w3rinkeby.eth.wait_for_transaction_receipt(  # receipt, hash as input
        w3rinkeby.eth.send_raw_transaction(  # send tx, signed tx as input
            w3rinkeby.eth.account.sign_transaction(  # sign tx, tx and private key as inputs
                wrapper_onchain.functions.withdraw(
                    wrapper_onchain.functions.balanceOf(os.getenv("ADDRESS")).call()
                ).buildTransaction(  # creating tx
                    {
                        "chainId": int(os.getenv("RINKEBY_ID")),
                        "gasPrice": w3rinkeby.eth.gas_price,
                        "from": os.getenv("ADDRESS"),
                        "nonce": nonce,
                    }
                ),
                private_key=os.getenv("PRIVATE_KEY"),
            ).rawTransaction
        )
    )
if balance_enough is False:
    print("broke mf")

print(wrapper_onchain.functions.balanceOf(os.getenv("ADDRESS")).call())
