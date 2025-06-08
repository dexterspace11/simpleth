import streamlit as st
from eth_account import Account
from web3 import Web3
import secrets

# --- CONFIGURATION ---
INFURA_URL = "https://sepolia.infura.io/v3/e0fcce634506410b87fc31064eed915a"  # Replace with your Infura/Alchemy endpoint
SIMPLETH_CONTRACT_ADDRESS = "0x5c8101593DC2b71579581b145bC1Eb6c16Ee1a64"         # Replace with your deployed Simpleth contract address
STETH_DECIMALS = 18

# --- ABI from your prompt ---
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
if "user_wallet" not in st.session_state:
    st.session_state["user_wallet"] = None
if "access_code" not in st.session_state:
    st.session_state["access_code"] = None

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
        st.session_state["user_wallet"] = {
            "address": wallet_address,
            "private_key": private_key
        }
        st.session_state["access_code"] = access_code
        st.success("Wallet created!")
        st.write(f"**Wallet Address:** `{wallet_address}`")
        st.write(f"**Access Code:** `{access_code}`")
        st.info("Save your wallet address and access code securely. You will need them to access your wallet.")

# --- SHOW PRIVATE KEY (for testing only, not for production) ---
if (
    st.session_state.get("user_wallet")
    and st.session_state.get("access_code")
):
    with st.expander("Show Private Key (for testing only)"):
        st.code(st.session_state["user_wallet"]["private_key"], language="text")

# --- LOGIN FORM ---
st.markdown("---")
st.subheader("Access Your Simpleth Wallet")
input_address = st.text_input("Wallet Address")
input_code = st.text_input("Access Code", type="password")

if st.button("Login"):
    # In production, validate against your user database
    if (
        st.session_state.get("user_wallet") and
        st.session_state.get("access_code") and
        input_address == st.session_state["user_wallet"]["address"] and
        input_code == st.session_state["access_code"]
    ):
        st.success("Access granted!")
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

# --- INSTRUCTIONS FOR ADMIN PRE-DEPOSIT ---
st.markdown("---")
st.markdown("""
**Admin Instructions:**  
To pre-deposit stETH (or mock stETH) for a user, send tokens to their wallet address, then have the user approve and deposit into Simpleth using your contract's functions.
""")