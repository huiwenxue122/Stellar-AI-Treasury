"""
Agent Conversation UI Component for Dashboard
Real-time display of multi-agent conversations
"""

import streamlit as st
from agents.agent_conversation_logger import get_conversation_logger
from datetime import datetime

def render_agent_conversation():
    """Render the agent conversation panel"""
    
    st.markdown("### 🤖 Multi-Agent Conversation")
    st.markdown("Watch AI agents communicate in real-time during trading")
    
    logger = get_conversation_logger()
    messages = logger.get_conversation_log()
    
    if not messages:
        st.info("💬 No active conversations yet. Click 'Run Trading Cycle' to see agents in action!")
        return
    
    # Agent color mapping
    agent_colors = {
        "System": "#888888",
        "Trading Agent (James Simons)": "#667eea",
        "Risk Agent": "#f6ad55",
        "Payment Agent": "#48bb78",
    }
    
    # Message type icons
    type_icons = {
        "info": "ℹ️",
        "thought": "💭",
        "tool_call": "🔧",
        "result": "📊",
        "decision": "💡",
        "action": "⚡"
    }
    
    # Display messages in a chat-like interface
    for msg in messages:
        agent = msg['agent']
        msg_type = msg['type']
        content = msg['content']
        timestamp = msg['timestamp']
        
        # Get agent color (with fallback)
        color = agent_colors.get(agent, "#888888")
        if "Strategy Tool" in agent:
            color = "#9f7aea"  # Purple for strategy tools
        
        # Get type icon
        icon = type_icons.get(msg_type, "💬")
        
        # Create message container
        with st.container():
            # Agent header
            st.markdown(
                f'<div style="color: {color}; font-weight: bold; font-size: 0.9em; margin-top: 10px;">'
                f'{icon} {agent} <span style="color: #888; font-size: 0.8em;">({timestamp})</span>'
                f'</div>',
                unsafe_allow_html=True
            )
            
            # Message content
            if msg_type == "tool_call":
                # Highlight tool calls
                st.markdown(
                    f'<div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin: 5px 0; border-left: 3px solid {color};">'
                    f'{content}'
                    f'</div>',
                    unsafe_allow_html=True
                )
            elif msg_type == "decision":
                # Highlight decisions
                st.markdown(
                    f'<div style="background-color: #fffaf0; padding: 10px; border-radius: 5px; margin: 5px 0; border-left: 3px solid {color};">'
                    f'<strong>{content}</strong>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            else:
                # Regular message
                st.markdown(
                    f'<div style="padding: 5px 10px; margin: 5px 0;">'
                    f'{content}'
                    f'</div>',
                    unsafe_allow_html=True
                )
    
    # Auto-scroll to bottom (simulated with expander)
    with st.expander("📜 View Full Conversation Log", expanded=False):
        st.json(messages)
    
    # Clear button
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("🗑️ Clear Log"):
            logger.clear()
            st.rerun()

def render_compact_agent_status():
    """Render a compact agent status indicator"""
    
    logger = get_conversation_logger()
    messages = logger.get_conversation_log()
    
    if not messages:
        st.markdown("💤 **Agents:** Idle")
        return
    
    # Get latest message
    latest = messages[-1]
    agent = latest['agent']
    
    # Show active agent
    if "Trading Agent" in agent:
        st.markdown("🔵 **Active:** Trading Agent analyzing...")
    elif "Risk Agent" in agent:
        st.markdown("🟠 **Active:** Risk Agent evaluating...")
    elif "Payment Agent" in agent:
        st.markdown("🟢 **Active:** Payment Agent executing...")
    else:
        st.markdown(f"⚪ **Active:** {agent}")
    
    # Show message count
    st.caption(f"💬 {len(messages)} messages in current cycle")

