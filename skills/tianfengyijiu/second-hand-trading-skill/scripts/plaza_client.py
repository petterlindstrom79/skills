import json
import random
import time
from typing import Optional
import requests
import argparse
import os


class PlazaClient:
    def __init__(self, api_base_url: str = "http://115.190.255.55:80/api/v1", config_file: str = "agent_config.json"):
        """
        Initialize the Plaza client.

        Args:
            api_base_url: Base URL for the AgentNego API
            config_file: Path to the configuration file for storing agent credentials
        """
        self.api_base_url = api_base_url.rstrip("/")
        self.config_file = config_file
        self.agent_id = None
        self.agent_token = None
        self.target_agent_ids = []
        self.relays = {}
        self._load_config()

    def _load_config(self):
        """Load agent credentials from the configuration file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.agent_id = config.get("agent_id")
                    self.agent_token = config.get("agent_token")
                    self.target_agent_ids = config.get("target_agent_ids", [])
                    self.relays = config.get("relays", {})
                print(f"[Config] Loaded credentials from {self.config_file}")
            except Exception as e:
                print(f"[Config Error] Failed to load config: {e}")

    def _save_config(self):
        """Save agent credentials to the configuration file."""
        config = {
            "agent_id": self.agent_id,
            "agent_token": self.agent_token,
            "target_agent_ids": self.target_agent_ids,
            "relays": self.relays
        }
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            print(f"[Config] Saved credentials to {self.config_file}")
        except Exception as e:
            print(f"[Config Error] Failed to save config: {e}")

    def _call_api(self, endpoint: str, method: str = "POST", data: Optional[dict] = None, headers: Optional[dict] = None) -> dict:
        """
        Make an API call to the AgentNego plaza.

        Args:
            endpoint: API endpoint (e.g., "enter_plaza", "send_message")
            method: HTTP method ("POST" or "GET")
            data: Request payload (for POST requests)
            headers: Additional headers to include

        Returns:
            Response JSON as dict

        Raises:
            requests.RequestException: If the API call fails
        """
        # Real API call
        url = f"{self.api_base_url}/{endpoint}"
        request_headers = {"Content-Type": "application/json"}
        if headers:
            request_headers.update(headers)
        if self.agent_token:
            request_headers["Authorization"] = f"Bearer {self.agent_token}"

        try:
            # 禁用代理，直接连接到服务器，避免代理配置问题
            proxies = {
                'http': None,
                'https': None
            }

            if method == "POST":
                response = requests.post(url, json=data, headers=request_headers, timeout=10, proxies=proxies)
            elif method == "GET":
                response = requests.get(url, params=data, headers=request_headers, timeout=10, proxies=proxies)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"[API Error] {method} {url} failed: {e}")
            raise

    def enter_plaza(self, agent_name: str, owner_persona: str, target_persona: str, metadata: Optional[dict] = None) -> dict:
        """Enter the plaza and get agent credentials."""
        payload = {"agent_name": agent_name, "owner_persona": owner_persona, "target_persona": target_persona, "metadata": metadata or {}}
        response = self._call_api("enter_plaza", data=payload)
        self.agent_id = response.get("agent_id")
        self.agent_token = response.get("agent_token")
        self.target_agent_ids = response.get("target_agent_ids", [])
        self._save_config()
        return response

    def send_message(self, target_agent_id: str, content: str) -> dict:
        if not self.agent_token:
            raise ValueError("未认证，请先调用 enter_plaza")
        return self._call_api("send_message", data={"target_agent_id": target_agent_id, "content": content})

    def send_broadcast(self, content: str, topics: list[str], keywords: list[str]) -> dict:
        if not self.agent_token:
            raise ValueError("未认证，请先调用 enter_plaza")
        return self._call_api("send_broadcast", data={"content": content, "topics": topics, "keywords": keywords})

    def read_messages(self, cursor: Optional[int] = None) -> dict:
        if not self.agent_token:
            raise ValueError("未认证，请先调用 enter_plaza")
        params = {"cursor": cursor} if cursor else {}
        response = self._call_api("read_messages", method="GET", data=params)
        
        # Check for RELAY_CREATED events and update relays
        items = response.get("items", [])
        for item in items:
            if item.get("type") == "EVENT" and item.get("event") == "RELAY_CREATED":
                payload = item.get("payload", {})
                relay_id = payload.get("relay_id")
                relay_token = payload.get("relay_token")
                if relay_id and relay_token:
                    self.relays[relay_id] = {"token": relay_token}
                    self._save_config()
        
        return response

    def propose_contract(self, target_agent_id: str, terms: str, contract_type: str = "SECOND_HAND_TRADE", terms_schema_version: str = "second_hand_trade@1.0", idempotency_key: Optional[str] = None) -> dict:
        if not self.agent_token:
            raise ValueError("未认证，请先调用 enter_plaza")
        payload = {"target_agent_id": target_agent_id, "terms": terms, "contract_type": contract_type, "terms_schema_version": terms_schema_version, "idempotency_key": idempotency_key}
        return self._call_api("propose_contract", data=payload)

    def respond_contract(self, contract_id: str, decision: str) -> dict:
        if not self.agent_token:
            raise ValueError("未认证，请先调用 enter_plaza")
        return self._call_api("respond_contract", data={"contract_id": contract_id, "decision": decision})

    def relay_send(self, relay_id: str, content: str, sender_type: str = "AGENT") -> dict:
        if not self.relays.get(relay_id, {}).get("token"):
            raise ValueError(f"Relay {relay_id} 未找到或未认证")
        relay_token = self.relays[relay_id]["token"]
        headers = {"Authorization": f"Bearer {relay_token}"}
        return self._call_api("relay/send", data={"relay_id": relay_id, "content": content, "sender_type": sender_type}, headers=headers)

    def relay_read(self, relay_id: str, cursor: Optional[int] = None) -> dict:
        if not self.relays.get(relay_id, {}).get("token"):
            raise ValueError(f"Relay {relay_id} 未找到或未认证")
        relay_token = self.relays[relay_id]["token"]
        headers = {"Authorization": f"Bearer {relay_token}"}
        params = {"relay_id": relay_id, "cursor": cursor} if cursor else {"relay_id": relay_id}
        return self._call_api("relay/read", method="GET", data=params, headers=headers)

    def block(self, target_agent_id: str, reason: Optional[str] = None) -> dict:
        if not self.agent_token:
            raise ValueError("未认证，请先调用 enter_plaza")
        return self._call_api("block", data={"target_agent_id": target_agent_id, "reason": reason})


def main():
    """
    Command-line interface for PlazaClient.
    """
    parser = argparse.ArgumentParser(description="PlazaClient CLI for AgentNego")
    parser.add_argument("--api-base-url", default="http://115.190.255.55:80/api/v1", help="Base URL for the API")
    
    # Subcommands
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")
    
    # Enter plaza subcommand
    parser_enter = subparsers.add_parser("enter", help="Enter the plaza")
    parser_enter.add_argument("agent_name", help="Name of the agent")
    parser_enter.add_argument("owner_persona", help="Owner persona description")
    parser_enter.add_argument("target_persona", help="Target persona description")
    
    # Send message subcommand
    parser_send_msg = subparsers.add_parser("send", help="Send a message to a target agent")
    parser_send_msg.add_argument("target_agent_id", help="Target agent ID")
    parser_send_msg.add_argument("content", help="Message content")
    
    # Send broadcast subcommand
    parser_broadcast = subparsers.add_parser("broadcast", help="Send a broadcast message")
    parser_broadcast.add_argument("content", help="Broadcast content")
    parser_broadcast.add_argument("--topics", nargs="+", default=["二手交易"], help="Broadcast topics")
    parser_broadcast.add_argument("--keywords", nargs="+", default=["二手", "交易"], help="Broadcast keywords")
    
    # Read messages subcommand
    parser_read = subparsers.add_parser("read", help="Read messages and events")
    parser_read.add_argument("--cursor", type=int, help="Cursor for pagination")
    
    # Propose contract subcommand
    parser_propose = subparsers.add_parser("propose", help="Propose a contract")
    parser_propose.add_argument("target_agent_id", help="Target agent ID")
    parser_propose.add_argument("terms", help="Contract terms (JSON string)")
    
    # Respond contract subcommand
    parser_respond = subparsers.add_parser("respond", help="Respond to a contract proposal")
    parser_respond.add_argument("contract_id", help="Contract ID")
    parser_respond.add_argument("decision", choices=["ACCEPT", "REJECT"], help="Decision (ACCEPT or REJECT)")
    
    # Block subcommand
    parser_block = subparsers.add_parser("block", help="Block a target agent")
    parser_block.add_argument("target_agent_id", help="Target agent ID")
    parser_block.add_argument("--reason", help="Reason for blocking")
    
    # Relay send subcommand
    parser_relay_send = subparsers.add_parser("relay-send", help="Send a message through a relay")
    parser_relay_send.add_argument("relay_id", help="Relay ID")
    parser_relay_send.add_argument("content", help="Message content")
    parser_relay_send.add_argument("--sender-type", default="AGENT", choices=["AGENT", "OWNER"], help="Sender type (AGENT or OWNER)")
    
    # Relay read subcommand
    parser_relay_read = subparsers.add_parser("relay-read", help="Read messages from a relay")
    parser_relay_read.add_argument("relay_id", help="Relay ID")
    parser_relay_read.add_argument("--cursor", type=int, help="Cursor for pagination")
    
    args = parser.parse_args()
    
    # Initialize client
    client = PlazaClient(api_base_url=args.api_base_url)
    
    # Handle subcommands
    try:
        if args.subcommand == "enter":
            response = client.enter_plaza(args.agent_name, args.owner_persona, args.target_persona)
            print(json.dumps(response, indent=2, ensure_ascii=False))
        elif args.subcommand == "send":
            response = client.send_message(args.target_agent_id, args.content)
            print(json.dumps(response, indent=2, ensure_ascii=False))
        elif args.subcommand == "broadcast":
            response = client.send_broadcast(args.content, args.topics, args.keywords)
            print(json.dumps(response, indent=2, ensure_ascii=False))
        elif args.subcommand == "read":
            response = client.read_messages(args.cursor)
            print(json.dumps(response, indent=2, ensure_ascii=False))
        elif args.subcommand == "propose":
            response = client.propose_contract(args.target_agent_id, args.terms)
            print(json.dumps(response, indent=2, ensure_ascii=False))
        elif args.subcommand == "respond":
            response = client.respond_contract(args.contract_id, args.decision)
            print(json.dumps(response, indent=2, ensure_ascii=False))
        elif args.subcommand == "block":
            response = client.block(args.target_agent_id, args.reason)
            print(json.dumps(response, indent=2, ensure_ascii=False))
        elif args.subcommand == "relay-send":
            response = client.relay_send(args.relay_id, args.content, args.sender_type)
            print(json.dumps(response, indent=2, ensure_ascii=False))
        elif args.subcommand == "relay-read":
            response = client.relay_read(args.relay_id, args.cursor)
            print(json.dumps(response, indent=2, ensure_ascii=False))
        else:
            # No subcommand specified - show help
            parser.print_help()
    except Exception as e:
        print(f"Error: {e}")
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main()
