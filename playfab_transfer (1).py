import requests
import time

# PlayFab Title ID (replace with your actual Title ID)
TITLE_ID = "YOUR_TITLE_ID"

# Existing session tickets for both accounts (replace with valid ones)
SOURCE_SESSION_TICKET = "SOURCE_ACCOUNT_SESSION_TICKET"
TARGET_SESSION_TICKET = "TARGET_ACCOUNT_SESSION_TICKET"

# PlayFab API Base URL
PLAYFAB_BASE_URL = f"https://{TITLE_ID}.playfabapi.com/Client"

def get_user_inventory(session_ticket):
    """Fetch the inventory of a user using their session ticket."""
    url = f"{PLAYFAB_BASE_URL}/GetUserInventory"
    headers = {"X-Authorization": session_ticket}
    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        inventory = response.json().get("data", {}).get("Inventory", [])
        return inventory
    else:
        print("Failed to get inventory:", response.json())
        return None

def open_trade(source_ticket, item_ids):
    """Creates a trade offer with the given item IDs."""
    url = f"{PLAYFAB_BASE_URL}/OpenTrade"
    headers = {"X-Authorization": source_ticket}
    payload = {
        "OfferedInventoryInstanceIds": item_ids,
        "RequestedCatalogItemIds": []  # Empty because the other player is just taking them
    }
    
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        trade_id = response.json().get("data", {}).get("TradeId")
        print(f"✅ Trade opened successfully! Trade ID: {trade_id}")
        return trade_id
    else:
        print("❌ Failed to open trade:", response.json())
        return None

def get_open_trades(target_ticket):
    """Fetches open trades for the target account."""
    url = f"{PLAYFAB_BASE_URL}/GetPlayerTrades"
    headers = {"X-Authorization": target_ticket}
    payload = {"StatusFilter": "Open"}  # Only fetch open trades

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        trades = response.json().get("data", {}).get("OpenTrades", [])
        return trades
    else:
        print("❌ Failed to get open trades:", response.json())
        return []

def accept_trade(target_ticket, trade_id):
    """Accepts the given trade offer."""
    url = f"{PLAYFAB_BASE_URL}/AcceptTrade"
    headers = {"X-Authorization": target_ticket}
    payload = {"TradeId": trade_id}
    
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        print("✅ Trade accepted successfully! Items transferred.")
        return True
    else:
        print("❌ Failed to accept trade:", response.json())
        return False

def transfer_inventory():
    """Transfers all items from the source account to the target account using PlayFab's trade system."""
    inventory = get_user_inventory(SOURCE_SESSION_TICKET)

    if not inventory:
        print("⚠️ No items to transfer.")
        return
    
    item_ids = [item["ItemInstanceId"] for item in inventory]
    print(f"🔄 Transferring {len(item_ids)} items via trade...")

    # Step 1: Open trade from source account
    trade_id = open_trade(SOURCE_SESSION_TICKET, item_ids)
    if not trade_id:
        print("❌ Failed to initiate trade.")
        return

    time.sleep(3)  # Wait for trade to be fully available

    # Step 2: Get the trade ID from the target account's perspective
    open_trades = get_open_trades(TARGET_SESSION_TICKET)
    matching_trade = next((trade for trade in open_trades if trade["TradeId"] == trade_id), None)

    if not matching_trade:
        print("❌ Target account couldn't find the trade. Aborting.")
        return

    # Step 3: Accept trade from target account
    success = accept_trade(TARGET_SESSION_TICKET, trade_id)
    if success:
        print("✅ All items transferred successfully!")
    else:
        print("❌ Trade transfer failed.")

# Run the transfer process
transfer_inventory()
