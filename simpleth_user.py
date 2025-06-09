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

ERC20_ABI = [
    {
        "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "address", "name": "recipient", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "nonpayable",
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
if "logged_in_wallet" not in st.session_state:
    st.session_state["logged_in_wallet"] = None

st.title("🦊 User Wallet Demo")

# --- WALLET CREATION ---
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
        st.success("Wallet created!")
        st.write(f"**Wallet Address:** `{wallet_address}`")
        st.write(f"**Access Code:** `{access_code}`")
        st.info("Save your wallet address and access code securely.")

# --- LOGIN FORM ---
st.markdown("---")
st.subheader("Access Your Wallet")
input_address = st.text_input("Wallet Address")
input_code = st.text_input("Access Code", type="password")

if st.button("Login"):
    wallet_db = load_wallet_db()
    # Always use checksum address for lookup
    try:
        input_address_checksum = Web3.to_checksum_address(input_address)
    except Exception:
        st.error("Invalid wallet address format.")
        st.stop()
    wallet_info = wallet_db.get(input_address_checksum)
    if wallet_info and input_code == wallet_info["access_code"]:
        st.success("Access granted!")
        st.session_state["logged_in_wallet"] = input_address_checksum
    else:
        st.error("Invalid wallet address or access code.")

# --- WALLET DASHBOARD ---
if st.session_state.get("logged_in_wallet"):
    wallet_address = st.session_state["logged_in_wallet"]
    wallet_info = st.session_state["wallet_db"].get(wallet_address)
    st.markdown(f"### Wallet: `{wallet_address}`")
    with st.expander("Show Private Key (for testing only)"):
        st.code(wallet_info["private_key"], language="text")

    # Show stETH balance
    try:
        steth_contract = w3.eth.contract(address=Web3.to_checksum_address(STETH_CONTRACT_ADDRESS), abi=ERC20_ABI)
        steth_balance = steth_contract.functions.balanceOf(wallet_address).call()
        st.write(f"**stETH balance:** {steth_balance / 1e18} stETH")
    except Exception as e:
        st.error(f"Error fetching stETH balance: {e}")

    # --- Deposit stETH (simulate transfer from another address) ---
    st.markdown("#### Deposit stETH")
    deposit_amount = st.number_input("Amount to deposit (stETH)", min_value=0.0, step=0.01)
    deposit_from = st.text_input("From address (must have stETH)")
    if st.button("Simulate Deposit"):
        try:
            # This is a simulation: in real dApps, user would send stETH from their wallet using MetaMask or similar
            st.info("In a real app, deposit would require a blockchain transaction from the sender's wallet.")
            st.success(f"Simulated deposit of {deposit_amount} stETH from {deposit_from} to {wallet_address}.")
        except Exception as e:
            st.error(f"Deposit failed: {e}")

    # --- Withdraw stETH (simulate transfer to another address) ---
    st.markdown("#### Withdraw stETH")
    withdraw_amount = st.number_input("Amount to withdraw (stETH)", min_value=0.0, step=0.01, key="withdraw")
    withdraw_to = st.text_input("Recipient address")
    if st.button("Simulate Withdraw"):
        try:
            # This is a simulation: in real dApps, user would sign and send a transaction
            st.info("In a real app, withdrawal would require a blockchain transaction signed by your wallet.")
            st.success(f"Simulated withdrawal of {withdraw_amount} stETH from {wallet_address} to {withdraw_to}.")
        except Exception as e:
            st.error(f"Withdraw failed: {e}")

    # --- Logout ---
    if st.button("Logout"):
        st.session_state["logged_in_wallet"] = None
        st.success("Logged out.")

st.markdown("---")
st.markdown("""
**Note:**  
- Deposits and withdrawals here are simulated for demo purposes.  
- Real transfers require blockchain transactions signed by the wallet's private key.
""")