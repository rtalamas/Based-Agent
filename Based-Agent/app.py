import streamlit as st
from swarm import Swarm
from agents import based_agent
from agents import agent_wallet

import os
from dotenv import load_dotenv

load_dotenv()

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "swarm_client" not in st.session_state:
        st.session_state.swarm_client = Swarm()
    if "agent_address" not in st.session_state:
        # Get the wallet address from based_agent
        st.session_state.agent_address = agent_wallet.default_address.address_id

def process_agent_response(response):
    """Process streaming response from the agent"""
    content = ""
    last_sender = ""
    
    # Create placeholder for streaming response
    message_placeholder = st.empty()
    
    for chunk in response:
        # Handle sender information
        if "sender" in chunk:
            last_sender = chunk["sender"]
            
        # Handle content
        if "content" in chunk and chunk["content"] is not None:
            if not content and last_sender:
                # Start new message with sender
                content = chunk["content"]
                message_placeholder.markdown(f"🤖 **{last_sender}**: {content}")
            else:
                content += chunk["content"]
                message_placeholder.markdown(f"🤖 **{last_sender}**: {content}")

        # Handle tool calls
        if "tool_calls" in chunk and chunk["tool_calls"] is not None:
            for tool_call in chunk["tool_calls"]:
                f = tool_call["function"]
                name = f["name"]
                if not name:
                    continue
                tool_call_msg = f"🛠️ **{last_sender}**: `{name}()`"
                st.markdown(tool_call_msg)

        # Handle end of message delimiter
        if "delim" in chunk and chunk["delim"] == "end" and content:
            content = ""  # Reset content for next message
            message_placeholder = st.empty()  # Create new placeholder for next message

        # Return response object when complete
        if "response" in chunk:
            return chunk["response"]
    
    return None

def main():
    st.title("Based Agent Chat Interface")
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar Configuration
    st.sidebar.markdown("### 🤖 Based Agent Dashboard")
    
    # Display agent's wallet address in sidebar
    if "agent_address" in st.session_state:
        st.sidebar.markdown("**Wallet Address (Sepolia):**")
        st.sidebar.code(st.session_state.agent_address)
    
    st.sidebar.markdown("---")
    
    # Move capabilities section to sidebar
    st.sidebar.markdown("### 🛠️ Available Actions")
    
    # Token Operations in sidebar
    with st.sidebar.expander("🪙 Token Operations", expanded=False):
        st.markdown("""
        * **Create ERC-20 Tokens**
            * Deploy your own token with custom name and symbol
            * Set initial supply and distribution
        
        * **Transfer Assets**
            * Send ETH or other tokens to any address
            * Handle USDC and other ERC-20 transfers
            
        * **Check Balances**
            * View your wallet's asset balances
            * Track token holdings
        """)
    
    # NFT Operations in sidebar
    with st.sidebar.expander("🎨 NFT Operations", expanded=False):
        st.markdown("""
        * **Deploy NFT Contracts**
            * Create ERC-721 collections
            * Set custom name, symbol, and base URI
        
        * **Mint NFTs**
            * Mint new NFTs to any address
            * Manage existing NFT collections
        """)
    
    # Utility Operations in sidebar
    with st.sidebar.expander("⚡ Utility Features", expanded=False):
        st.markdown("""
        * **Faucet Access**
            * Request test ETH from Base Sepolia faucet
            * Get started with zero-cost testing
        
        * **Name Services**
            * Register custom .base.eth names
            * Manage blockchain identities
            
        * **Asset Swaps**
            * Swap between different tokens
            * Access Base Mainnet trading features
        """)
    
    st.sidebar.markdown("---")
    
    # Clear chat button in sidebar
    if st.sidebar.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
    
    # Main chat interface
    st.markdown("""
    ### 💬 Welcome to Based Agent!
    I'm your blockchain assistant on the Base network. Check out my capabilities in the sidebar menu and let's build something cool together!
    """)
    
    # Display chat messages from history
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"👤 **You**: {message['content']}")
        else:
            st.markdown(f"🤖 **Based Agent**: {message['content']}")
    
    # Chat input
    if prompt := st.chat_input("What would you like to do on Base?"):
        # Add user message to state and display
        st.markdown(f"👤 **You**: {prompt}")
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get agent response
        response = st.session_state.swarm_client.run(
            agent=based_agent,
            messages=st.session_state.messages,
            stream=True
        )
        
        # Process and display agent response
        response_obj = process_agent_response(response)
        
        if response_obj and response_obj.messages:
            # Add agent messages to session state
            st.session_state.messages.extend(response_obj.messages)

if __name__ == "__main__":
    main() 