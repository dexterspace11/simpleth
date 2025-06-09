import streamlit as st
from eth_account import Account
from web3 import Web3
import secrets
import os
import json

# --- CONFIGURATION ---
INFURA_URL = "https://sepolia.infura.io/v3/e0fcce634506410b87fc31064eed915a"
STETH_CONTRACT_ADDRESS = "0xFD5d07334591C3eE2699639Bb670de279ea45f65"  # Replace with your stETH/mockStETH address
WALLET_DB_FILE = "wallet_db.json"

STETH_ABI = [
    {
        "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

def load_wallet_db():
    if os.path.exists(WALLET_DB_FILE):
        with open(WALLET_DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_wallet_db(db):
    with open(WALLET_DB_FILE, "w") as f:
        json.dump(db, f)

w3 = Web3(Web3.HTTPProvider(INFURA_URL))

if "wallet_db" not in st.session_state:
    st.session_state["wallet_db"] = load_wallet_db()
if "last_wallet" not in st.session_state:
    st.session_state["last_wallet"] = None

st.title("🦊 User Wallet Demo")

with st.expander("Create a New Wallet"):
    if st.button("Create Wallet"):
        acct = Account.create()
        wallet_address = acct.address
        private_key = acct.key.hex()
        access_code = secrets.token_urlsafe(8)
        st.session_state["wallet_db"][wallet_address] = {
            "private_key": private_key,
            "access_code": access_code
        }
        save_wallet_db(st.session_state["wallet_db"])
        st.session_state["last_wallet"] = wallet_address
        st.success("Wallet created!")
        st.write(f"**Wallet Address:** `{wallet_address}`")
        st.write(f"**Access Code:** `{access_code}`")
        st.info("Save your wallet address and access code securely.")

        # Show stETH balance
        try:
            steth_contract = w3.eth.contract(address=Web3.to_checksum_address(STETH_CONTRACT_ADDRESS), abi=STETH_ABI)
            steth_balance = steth_contract.functions.balanceOf(Web3.to_checksum_address(wallet_address)).call()
            st.write(f"**stETH balance:** {steth_balance / 1e18} stETH")
        except Exception as e:
            st.error(f"Error fetching stETH balance: {e}")

if st.session_state.get("last_wallet"):
    wallet_address = st.session_state["last_wallet"]
    wallet_info = st.session_state["wallet_db"].get(wallet_address)
    if wallet_info:
        with st.expander("Show Private Key (for testing only)"):
            st.code(wallet_info["private_key"], language="text")

st.markdown("---")
st.subheader("Access Existing Wallet")
input_address = st.text_input("Wallet Address")
input_code = st.text_input("Access Code", type="password")

if st.button("Login"):
    wallet_db = load_wallet_db()
    wallet_info = wallet_db.get(input_address)
    if wallet_info and input_code == wallet_info["access_code"]:
        st.success("Access granted!")
        st.session_state["last_wallet"] = input_address
        try:
            steth_contract = w3.eth.contract(address=Web3.to_checksum_address(STETH_CONTRACT_ADDRESS), abi=STETH_ABI)
            steth_balance = steth_contract.functions.balanceOf(Web3.to_checksum_address(input_address)).call()
            st.write(f"**stETH balance:** {steth_balance / 1e18} stETH")
        except Exception as e:
            st.error(f"Error fetching stETH balance: {e}")
    else:
        st.error("Invalid wallet address or access code.")