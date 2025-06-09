import streamlit as st
from web3 import Web3
import os

# --- CONFIGURATION ---
INFURA_URL = "https://sepolia.infura.io/v3/e0fcce634506410b87fc31064eed915a"
VAULT_ADDRESS = "0xYourVaultAddressHere"  # <-- Replace with your deployed KinetixVault address
STETH_ADDRESS = "0xYourStETHAddressHere"  # <-- Replace with your stETH/mockstETH address

# --- ABIs ---
KINETIX_VAULT_ABI = [
    {
        "inputs": [],
        "name": "beneficiary",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "donor", "type": "address"}],
        "name": "principalOf",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "vaultBalance",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "stakingRewards",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "amount", "type": "uint256"}],
        "name": "deposit",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "amount", "type": "uint256"}],
        "name": "withdraw",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "donateRewards",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    }
]

ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "success", "type": "bool"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    }
]

# --- WEB3 SETUP ---
w3 = Web3(Web3.HTTPProvider(INFURA_URL))
vault = w3.eth.contract(address=Web3.to_checksum_address(VAULT_ADDRESS), abi=KINETIX_VAULT_ABI)
steth = w3.eth.contract(address=Web3.to_checksum_address(STETH_ADDRESS), abi=ERC20_ABI)

st.set_page_config(page_title="Kinetix Giving Vault", page_icon="💧")
st.title("💧 Kinetix Giving Vault")

st.markdown("""
Interact with the KinetixVault contract as a donor.
""")

donor_address = st.text_input("Your Wallet Address")

if donor_address:
    try:
        donor = Web3.to_checksum_address(donor_address)
    except Exception:
        st.error("Invalid address format.")
        st.stop()

    # Fetch balances
    steth_decimals = steth.functions.decimals().call()
    divisor = 10 ** steth_decimals

    steth_balance = steth.functions.balanceOf(donor).call() / divisor
    kntx_balance = vault.functions.balanceOf(donor).call() / divisor
    principal = vault.functions.principalOf(donor).call() / divisor
    vault_balance = vault.functions.vaultBalance().call() / divisor
    rewards = vault.functions.stakingRewards().call() / divisor
    beneficiary = vault.functions.beneficiary().call()

    st.subheader("Your Balances")
    st.write(f"stETH in your wallet: **{steth_balance}**")
    st.write(f"KNTX (receipt tokens): **{kntx_balance}**")
    st.write(f"Principal (your deposit): **{principal}**")

    st.subheader("Vault Info")
    st.write(f"Vault stETH balance: **{vault_balance}**")
    st.write(f"Staking rewards (available to donate): **{rewards}**")
    st.write(f"Beneficiary address: `{beneficiary}`")

    st.markdown("---")
    st.subheader("How to Deposit")
    st.markdown(f"""
    1. **Approve** the vault to spend your stETH:
       - Call `approve` on stETH contract:<br>
         `approve({VAULT_ADDRESS}, amount)`
    2. **Deposit** stETH:
       - Call `deposit(amount)` on the vault contract.
    """)

    st.info("You must use MetaMask, Etherscan, or a web3 wallet to perform real transactions. This app only reads data and simulates actions.")

    st.markdown("---")
    st.subheader("Simulate Actions (Read-Only)")

    deposit_amount = st.number_input("Amount to deposit (stETH)", min_value=0.0, step=0.01)
    if st.button("Simulate Deposit"):
        st.success(f"Simulated deposit of {deposit_amount} stETH. (Use your wallet to perform the real transaction.)")

    withdraw_amount = st.number_input("Amount to withdraw (stETH)", min_value=0.0, step=0.01)
    if st.button("Simulate Withdraw"):
        if withdraw_amount > principal:
            st.error("Cannot withdraw more than your principal.")
        else:
            st.success(f"Simulated withdrawal of {withdraw_amount} stETH. (Use your wallet to perform the real transaction.)")

    if st.button("Simulate Donate Rewards"):
        if rewards > 0:
            st.success(f"Simulated donation of {rewards} stETH to beneficiary. (Use your wallet to perform the real transaction.)")
        else:
            st.info("No rewards available to donate.")

else:
    st.info("Enter your wallet address to view your balances and vault info.")

st.markdown("---")
st.markdown("""
**Note:**  
- This app is for viewing and simulation only.  
- Use MetaMask, Etherscan, or your preferred wallet to interact with the contract for real transactions.
""")