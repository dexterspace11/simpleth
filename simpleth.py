import streamlit as st
from eth_account import Account
from web3 import Web3
import secrets

# --- CONFIGURATION ---
INFURA_URL = "https://sepolia.infura.io/v3/e0fcce634506410b87fc31064eed915a"
SIMPLETH_CONTRACT_ADDRESS = "0xe0271f5571AB60dD89EF11F1743866a213406542"
STETH_DECIMALS = 18

SIMPLETH_ABI = [
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

# --- WEB3 SETUP ---
w3 = Web3(Web3.HTTPProvider(INFURA_URL))

# --- SESSION STATE ---
if "wallet_db" not in st.session_state:
    st.session_state["wallet_db"] = {}
if "last_created_wallet" not in st.session_state:
    st.session_state["last_created_wallet"] = None
if "last_logged_in_wallet" not in st.session_state:
    st.session_state["last_logged_in_wallet"] = None

# --- APP UI ---
st.set_page_config(page_title="Simpleth Wallet", page_icon="🦊")
st.title("🦊 Simpleth Wallet")

st.markdown("""
Welcome to Simpleth!  
Generate your wallet and access code, or log in to view your stETH balance.
""")

# --- WALLET CREATION ---
with st.expander("Create a New Simpleth Wallet"):
    if st.button("Create Wallet"):
        acct = Account.create()
        wallet_address = acct.address
        private_key = acct.key.hex()
        access_code = secrets.token_urlsafe(8)
        # Store in wallet_db
        st.session_state["wallet_db"][wallet_address] = {
            "private_key": private_key,
            "access_code": access_code
        }
        st.session_state["last_created_wallet"] = wallet_address
        st.success("Wallet created!")
        st.write(f"**Wallet Address:** `{wallet_address}`")
        st.write(f"**Access Code:** `{access_code}`")
        st.info("Save your wallet address and access code securely. You will need them to access your wallet.")

# --- SHOW PRIVATE KEY FOR LAST CREATED WALLET ---
if st.session_state.get("last_created_wallet"):
    wallet_address = st.session_state["last_created_wallet"]
    wallet_info = st.session_state["wallet_db"].get(wallet_address)
    if wallet_info:
        with st.expander("Show Private Key for Last Created Wallet (for testing only)"):
            st.code(wallet_info["private_key"], language="text")

# --- LOGIN FORM ---
st.markdown("---")
st.subheader("Access Your Simpleth Wallet")
input_address = st.text_input("Wallet Address")
input_code = st.text_input("Access Code", type="password")

if st.button("Login"):
    wallet_db = st.session_state.get("wallet_db", {})
    wallet_info = wallet_db.get(input_address)
    if wallet_info and input_code == wallet_info["access_code"]:
        st.success("Access granted!")
        st.session_state["last_logged_in_wallet"] = input_address
        # Connect to Simpleth contract
        contract = w3.eth.contract(address=Web3.to_checksum_address(SIMPLETH_CONTRACT_ADDRESS), abi=SIMPLETH_ABI)
        # Get stETH balance from contract
        try:
            balance = contract.functions.balanceOf(input_address).call()
            st.write(f"**Your stETH balance in Simpleth:** {balance / 10**STETH_DECIMALS:.6f} stETH")
            st.info("If you have received a pre-deposit, it will show above.")
        except Exception as e:
            st.error(f"Error fetching balance: {e}")
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