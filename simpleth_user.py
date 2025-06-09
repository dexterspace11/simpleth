import streamlit as st
from web3 import Web3
import os
import json

# --- CONFIGURATION ---
INFURA_URL = "https://sepolia.infura.io/v3/e0fcce634506410b87fc31064eed915a"
STETH_CONTRACT_ADDRESS = "0xFD5d07334591C3eE2699639Bb670de279ea45f65"  # Same as admin app
WALLET_DB_FILE = "wallet_db.json"

STETH_ABI = [
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

w3 = Web3(Web3.HTTPProvider(INFURA_URL))

if "logged_in_wallet" not in st.session_state:
    st.session_state["logged_in_wallet"] = None

st.set_page_config(page_title="Simpleth User Wallet", page_icon="🦊")
st.title("🦊 Simpleth User Wallet")

st.markdown("""
Welcome!  
Log in with your wallet address and access code (provided by the admin).
""")

# --- USER LOGIN ---
input_address = st.text_input("Wallet Address")
input_code = st.text_input("Access Code", type="password")

if st.button("Login"):
    wallet_db = load_wallet_db()
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
    wallet_db = load_wallet_db()
    wallet_info = wallet_db.get(wallet_address)
    st.markdown(f"### Wallet: `{wallet_address}`")

    # Show stETH balance
    try:
        steth_contract = w3.eth.contract(address=Web3.to_checksum_address(STETH_CONTRACT_ADDRESS), abi=STETH_ABI)
        steth_balance = steth_contract.functions.balanceOf(wallet_address).call()
        st.write(f"**stETH balance:** {steth_balance / 1e18} stETH")
    except Exception as e:
        st.error(f"Error fetching stETH balance: {e}")

    # --- Deposit (Simulation) ---
    st.markdown("#### Deposit stETH (Simulation)")
    st.info("To deposit real stETH, send tokens to your wallet address using your preferred wallet (e.g., MetaMask).")
    st.code(wallet_address, language="text")

    # --- Withdraw (Simulation) ---
    st.markdown("#### Withdraw stETH (Simulation)")
    withdraw_to = st.text_input("Recipient address")
    withdraw_amount = st.number_input("Amount to withdraw (stETH)", min_value=0.0, step=0.01)
    if st.button("Simulate Withdraw"):
        st.info("In a real app, withdrawal would require a blockchain transaction signed by your wallet's private key.")
        st.success(f"Simulated withdrawal of {withdraw_amount} stETH to {withdraw_to}.")

    # --- Show Private Key (Optional, for testing only) ---
    with st.expander("Show Private Key (for testing only)"):
        st.code(wallet_info["private_key"], language="text")

    if st.button("Logout"):
        st.session_state["logged_in_wallet"] = None
        st.success("Logged out.")

st.markdown("---")
st.markdown("""
**Note:**  
- Deposits and withdrawals here are simulated for demo purposes.  
- Real transfers require blockchain transactions signed by your wallet's private key.
""")