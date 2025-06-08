import streamlit as st
from web3 import Web3

# Set up Sepolia RPC
SEPOLIA_RPC = "https://sepolia.infura.io/v3/e0fcce634506410b87fc31064eed915a"
w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC))

# Contract addresses
SIMPLETH_ADDRESS = "0xe0271f5571AB60dD89EF11F1743866a213406542"
STETH_ADDRESS = "0xFD5d07334591C3eE2699639Bb670de279ea45f65"

# MockStETH ABI (from your prompt)
STETH_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "account", "type": "address"}
        ],
        "name": "balanceOf",
        "outputs": [
            {"internalType": "uint256", "name": "", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "recipient", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [
            {"internalType": "bool", "name": "", "type": "bool"}
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "sender", "type": "address"},
            {"internalType": "address", "name": "recipient", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "transferFrom",
        "outputs": [
            {"internalType": "bool", "name": "", "type": "bool"}
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# Instantiate the MockStETH contract
steth = w3.eth.contract(address=STETH_ADDRESS, abi=STETH_ABI)

# Address generation and persistence
if "user_account" not in st.session_state:
    acct = w3.eth.account.create()
    st.session_state["user_account"] = acct.address
    st.session_state["user_private_key"] = acct.key.hex()

st.write(f"Your wallet address: `{st.session_state['user_account']}`")

# Show user's MockStETH balance
steth_balance = steth.functions.balanceOf(st.session_state["user_account"]).call()
st.write(f"Your MockStETH balance: {w3.fromWei(steth_balance, 'ether')} stETH")

# ...existing code for Simpleth contract and UI...