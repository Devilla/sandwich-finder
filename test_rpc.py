#!/usr/bin/env python3
"""
Quick test to verify Alchemy RPC can access historical Ethereum data from 2022.
Block 13916166 is approximately Jan 1, 2022.
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load from .env file if it exists
load_dotenv()

# Load Alchemy API key from environment variable
ALCHEMY_KEY = os.environ.get("ALCHEMY_KEY")
if not ALCHEMY_KEY:
    print("ERROR: Please set the ALCHEMY_KEY environment variable")
    print("  Option 1: Create a .env file with: ALCHEMY_KEY=your_key_here")
    print("  Option 2: export ALCHEMY_KEY=your_key_here")
    exit(1)

ALCHEMY_URL = f"https://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_KEY}"

# First few blocks of 2022
TEST_BLOCKS = [13916166, 13916167, 13916168]

def rpc_call(method, params=None):
    """Make a JSON-RPC call to Alchemy"""
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": method,
        "params": params or []
    }
    response = requests.post(
        ALCHEMY_URL,
        headers={"Content-Type": "application/json"},
        json=payload
    )
    return response.json()

def main():
    # 1. Check current block number (verify connection)
    print("=" * 60)
    print("Testing Alchemy RPC Connection")
    print("=" * 60)
    
    result = rpc_call("eth_blockNumber")
    if "result" in result:
        current_block = int(result["result"], 16)
        print(f"✓ Connected! Current block: {current_block:,}")
    else:
        print(f"✗ Error: {result}")
        return
    
    # 2. Fetch historical blocks from early 2022
    print(f"\n--- Testing Historical Block Access (Jan 1, 2022) ---\n")
    
    for block_num in TEST_BLOCKS:
        block_hex = hex(block_num)
        result = rpc_call("eth_getBlockByNumber", [block_hex, True])  # True = include full txs
        
        if "result" in result and result["result"]:
            block = result["result"]
            tx_count = len(block.get("transactions", []))
            timestamp = int(block["timestamp"], 16)
            
            # Convert timestamp to readable date
            from datetime import datetime
            dt = datetime.utcfromtimestamp(timestamp)
            
            print(f"Block {block_num}:")
            print(f"  Timestamp: {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC")
            print(f"  Transactions: {tx_count}")
            print(f"  Gas Used: {int(block['gasUsed'], 16):,}")
            print()
        else:
            print(f"✗ Could not fetch block {block_num}")
            print(f"  Error: {result.get('error', 'Unknown error')}")
            return
    
    # 3. Test fetching logs (Swap events) for one block
    print("--- Testing Log Fetching (Uniswap V2 Swap Events) ---\n")
    
    # Uniswap V2 Swap event topic
    SWAP_TOPIC = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"
    
    result = rpc_call("eth_getLogs", [{
        "fromBlock": hex(TEST_BLOCKS[0]),
        "toBlock": hex(TEST_BLOCKS[0]),
        "topics": [SWAP_TOPIC]
    }])
    
    if "result" in result:
        logs = result["result"]
        print(f"✓ Found {len(logs)} Uniswap V2 Swap events in block {TEST_BLOCKS[0]}")
        
        if logs:
            print(f"\n  Sample swap event:")
            print(f"    Pair address: {logs[0]['address']}")
            print(f"    Tx hash: {logs[0]['transactionHash']}")
    else:
        print(f"✗ Error fetching logs: {result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 60)
    print("✓ Historical data access confirmed! Ready to build detector.")
    print("=" * 60)

if __name__ == "__main__":
    main()

