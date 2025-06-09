import streamlit as st
from eth_account import Account
from web3 import Web3
import secrets
import os
import json

# --- CONFIGURATION ---
INFURA_URL = "https://sepolia.infura.io/v3/e0fcce634506410b87fc31064eed915a"
SIMPLETH_CONTRACT_ADDRESS = "0xe0271f5571AB60dD89EF11F1743866a213406542"
STETH_CONTRACT_ADDRESS = "0xFD5d07334591C3eE2699639Bb670de279ea45f65"  # <-- Replace with your mock stETH address
WALLET_DB_FILE = "wallet_db.json"

# Use the correct ABI for stETH/mockStETH
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

# Use the same ABI for Simpleth if it matches
SIMPLETH_ABI = STETH_ABI

# --- WALLET DB PERSISTENCE ---
def load_wallet_db():
    if os.path.exists(WALLET_DB_FILE):
        with open(WALLET_DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_wallet_db(db):
    with open(WALLET_DB_FILE, "w") as f:
        json.dump(db, f)

# --- WEB3 SETUP ---
w3 = Web3(Web3.HTTPProvider(INFURA_URL))

# --- SESSION STATE ---
if "wallet_db" not in st.session_state:
    st.session_state["wallet_db"] = load_wallet_db()
if "last_created_wallet" not in st.session_state:
    st.session_state["last_created_wallet"] = None
if "last_logged_in_wallet" not in st.session_state:
    st.session_state["last_logged_in_wallet"] = None

# --- APP UI ---
st.set_page_config(page_title="Simpleth Wallet Admin", page_icon="🦊")
st.title("🦊 Simpleth Wallet Admin")

st.markdown("""
Welcome to Simpleth Admin!  
Generate wallets and access codes for your users, or log in to view wallet balances.
""")

# --- WALLET CREATION ---
with st.expander("Create a New Simpleth Wallet"):
    if st.button("Create Wallet"):
        acct = Account.create()
        wallet_address = Web3.to_checksum_address(acct.address)  # Always store as checksum!
        private_key = acct.key.hex()
        access_code = secrets.token_urlsafe(8)
        # Store in wallet_db
        st.session_state["wallet_db"][wallet_address] = {
            "private_key": private_key,
            "access_code": access_code
        }
        save_wallet_db(st.session_state["wallet_db"])
        st.session_state["last_created_wallet"] = wallet_address
        st.success("Wallet created!")
        st.write(f"**Wallet Address:** `{wallet_address}`")
        st.write(f"**Access Code:** `{access_code}`")
        st.info("Share this wallet address and access code with the user. They will need them to access their wallet.")

        # Show balances after creation
        try:
            steth_contract = w3.eth.contract(address=Web3.to_checksum_address(STETH_CONTRACT_ADDRESS), abi=STETH_ABI)
            steth_balance = steth_contract.functions.balanceOf(wallet_address).call()
            st.write(f"**stETH balance in wallet:** {steth_balance / 1e18} stETH")
        except Exception as e:
            st.error(f"Error fetching stETH wallet balance: {e}")
        try:
            simpleth_contract = w3.eth.contract(address=Web3.to_checksum_address(SIMPLETH_CONTRACT_ADDRESS), abi=SIMPLETH_ABI)
            balance = simpleth_contract.functions.balanceOf(wallet_address).call()
            st.write(f"**stETH balance in Simpleth:** {balance / 1e18} stETH")
        except Exception as e:
            st.error(f"Error fetching Simpleth balance: {e}")

# --- SHOW PRIVATE KEY FOR LAST CREATED WALLET ---
if st.session_state.get("last_created_wallet"):
    wallet_address = st.session_state["last_created_wallet"]
    wallet_info = st.session_state["wallet_db"].get(wallet_address)
    if wallet_info:
        with st.expander("Show Private Key for Last Created Wallet (for testing only)"):
            st.code(wallet_info["private_key"], language="text")

# --- LOGIN FORM ---
st.markdown("---")
st.subheader("Access Any Simpleth Wallet")
input_address = st.text_input("Wallet Address")
input_code = st.text_input("Access Code", type="password")

if st.button("Login"):
    wallet_db = load_wallet_db()  # Always load the latest db from disk
    try:
        input_address_checksum = Web3.to_checksum_address(input_address)
    except Exception:
        st.error("Invalid wallet address format.")
        st.stop()
    wallet_info = wallet_db.get(input_address_checksum)
    if wallet_info and input_code == wallet_info["access_code"]:
        st.success("Access granted!")
        st.session_state["last_logged_in_wallet"] = input_address_checksum
        # Show balances after login
        try:
            steth_contract = w3.eth.contract(address=Web3.to_checksum_address(STETH_CONTRACT_ADDRESS), abi=STETH_ABI)
            steth_balance = steth_contract.functions.balanceOf(input_address_checksum).call()
            st.write(f"**stETH balance in wallet:** {steth_balance / 1e18} stETH")
        except Exception as e:
            st.error(f"Error fetching stETH wallet balance: {e}")
        try:
            simpleth_contract = w3.eth.contract(address=Web3.to_checksum_address(SIMPLETH_CONTRACT_ADDRESS), abi=SIMPLETH_ABI)
            balance = simpleth_contract.functions.balanceOf(input_address_checksum).call()
            st.write(f"**stETH balance in Simpleth:** {balance / 1e18} stETH")
            st.info("If you have received a pre-deposit, it will show above.")
        except Exception as e:
            st.error(f"Error fetching Simpleth balance: {e}")
    else:
        st.error("Invalid wallet address or access code.")

# --- SHOW PRIVATE KEY FOR LAST LOGGED IN WALLET ---
if st.session_state.get("last_logged_in_wallet"):
    wallet_address = st.session_state["last_logged_in_wallet"]
    wallet_info = st.session_state["wallet_db"].get(wallet_address)
    if wallet_info:
        with st.expander("Show Private Key for Last Logged In Wallet (for testing only)"):
            st.code(wallet_info["private_key"], language="text")

# --- INSTRUCTIONS FOR ADMIN PRE-DEPOSIT ---
st.markdown("---")
st.markdown("""
**Admin Instructions:**  
To pre-deposit stETH (or mock stETH) for a user, send tokens to their wallet address, then have the user approve and deposit into Simpleth using your contract's functions.
""")