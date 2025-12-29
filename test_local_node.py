#!/usr/bin/env python3
"""
Test script to check if your local Ethereum node has historical data.
"""

import requests
import json
from datetime import datetime

LOCAL_NODE = "http://192.168.68.62:8545"

def rpc_call(method, params=None):
    """Make a JSON-RPC call to the local node"""
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": method,
        "params": params or []
    }
    
    try:
        response = requests.post(
            LOCAL_NODE,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=10
        )
        result = response.json()
        if "error" in result:
            return {"error": result["error"]}
        return result
    except requests.exceptions.ConnectionError:
        return {"error": "Connection refused - is the node running?"}
    except Exception as e:
        return {"error": str(e)}

def main():
    print("=" * 60)
    print("🔍 Testing Local Ethereum Node")
    print(f"   Endpoint: {LOCAL_NODE}")
    print("=" * 60)
    
    # Test 1: Get latest block
    print("\n📡 Test 1: Get latest block number...")
    result = rpc_call("eth_blockNumber")
    
    if "error" in result:
        print(f"   ❌ FAILED: {result['error']}")
        print("\n   Make sure your node is running and accessible.")
        return
    
    latest_block = int(result["result"], 16)
    print(f"   ✅ Connected! Latest block: {latest_block:,}")
    
    # Test 2: Get latest block details
    print("\n📡 Test 2: Get latest block details...")
    result = rpc_call("eth_getBlockByNumber", [hex(latest_block), False])
    
    if "error" in result or not result.get("result"):
        print(f"   ❌ FAILED: Could not fetch block details")
    else:
        block = result["result"]
        ts = int(block["timestamp"], 16)
        dt = datetime.utcfromtimestamp(ts)
        print(f"   ✅ Block {latest_block:,}")
        print(f"      Timestamp: {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print(f"      Transactions: {len(block.get('transactions', []))}")
    
    # Test 3: Get a 2022 block (archive node test)
    print("\n📡 Test 3: Get historical block from Jan 1, 2022...")
    block_2022 = 13916166  # Jan 1, 2022
    result = rpc_call("eth_getBlockByNumber", [hex(block_2022), False])
    
    if "error" in result:
        print(f"   ❌ FAILED: {result['error']}")
        print("   Your node may not be an archive node.")
    elif not result.get("result"):
        print(f"   ❌ FAILED: Block {block_2022:,} not found")
        print("   Your node may not have historical data (not an archive node).")
    else:
        block = result["result"]
        ts = int(block["timestamp"], 16)
        dt = datetime.utcfromtimestamp(ts)
        print(f"   ✅ Block {block_2022:,} found!")
        print(f"      Timestamp: {dt.strftime('%Y-%m-%d %H:%M:%S')} UTC")
        print(f"      Transactions: {len(block.get('transactions', []))}")
    
    # Test 4: Get swap logs from 2022
    print("\n📡 Test 4: Fetch Uniswap V2 Swap events from 2022...")
    SWAP_TOPIC = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"
    
    result = rpc_call("eth_getLogs", [{
        "fromBlock": hex(block_2022),
        "toBlock": hex(block_2022),
        "topics": [SWAP_TOPIC]
    }])
    
    if "error" in result:
        print(f"   ❌ FAILED: {result['error']}")
        print("   Your node may not support eth_getLogs for historical blocks.")
    elif not result.get("result"):
        print(f"   ⚠️  No swap events in block {block_2022:,} (this is normal)")
    else:
        logs = result["result"]
        print(f"   ✅ Found {len(logs)} Swap events in block {block_2022:,}!")
        if logs:
            print(f"      First event tx: {logs[0]['transactionHash']}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    
    if "error" not in result and result.get("result") is not None:
        print("✅ Your local node appears to be an ARCHIVE NODE!")
        print("   It has historical data from 2022 and can be used for sandwich detection.")
        print(f"\n   To use it, update find_sandwiches.py:")
        print(f'   ALCHEMY_URL = "{LOCAL_NODE}"')
    else:
        print("⚠️  Your local node may be a FULL NODE (not archive).")
        print("   Full nodes typically only keep recent state (~128 blocks).")
        print("   You'll need an archive node for historical data from 2022.")

if __name__ == "__main__":
    main()

