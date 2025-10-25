"""
Agent Conversation Logger
Real-time logging of multi-agent conversations for dashboard display
"""

from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass
import json

@dataclass
class ConversationMessage:
    """A single message in agent conversation"""
    timestamp: datetime
    agent: str  # "Trading Agent", "Risk Agent", "Payment Agent", "System"
    message_type: str  # "thought", "action", "tool_call", "result", "decision"
    content: str
    metadata: Optional[Dict] = None

class AgentConversationLogger:
    """Logger for multi-agent conversations"""
    
    def __init__(self):
        self.messages: List[ConversationMessage] = []
        self.current_cycle_id = None
        
    def start_cycle(self, cycle_id: str):
        """Start a new trading cycle"""
        self.current_cycle_id = cycle_id
        self.log_system(f"🚀 Starting Trading Cycle: {cycle_id}")
    
    def log_system(self, message: str, metadata: Optional[Dict] = None):
        """Log system message"""
        self.messages.append(ConversationMessage(
            timestamp=datetime.now(),
            agent="System",
            message_type="info",
            content=message,
            metadata=metadata
        ))
    
    def log_trading_agent_thought(self, thought: str, metadata: Optional[Dict] = None):
        """Log Trading Agent's reasoning"""
        self.messages.append(ConversationMessage(
            timestamp=datetime.now(),
            agent="Trading Agent (James Simons)",
            message_type="thought",
            content=thought,
            metadata=metadata
        ))
    
    def log_trading_agent_tool_call(self, tool_name: str, arguments: Dict):
        """Log Trading Agent calling a strategy tool"""
        self.messages.append(ConversationMessage(
            timestamp=datetime.now(),
            agent="Trading Agent (James Simons)",
            message_type="tool_call",
            content=f"📊 Calling strategy: {tool_name}",
            metadata={"tool": tool_name, "arguments": arguments}
        ))
    
    def log_tool_result(self, tool_name: str, result: Dict):
        """Log strategy tool result"""
        action = result.get('action', 'HOLD')
        confidence = result.get('confidence', 0)
        self.messages.append(ConversationMessage(
            timestamp=datetime.now(),
            agent=f"Strategy Tool: {tool_name}",
            message_type="result",
            content=f"✅ Result: {action} (confidence: {confidence:.2f})",
            metadata=result
        ))
    
    def log_trading_agent_decision(self, decision: str, portfolio: List[Dict]):
        """Log Trading Agent's final portfolio decision"""
        self.messages.append(ConversationMessage(
            timestamp=datetime.now(),
            agent="Trading Agent (James Simons)",
            message_type="decision",
            content=f"💡 Portfolio Decision: {decision}",
            metadata={"portfolio": portfolio}
        ))
    
    def log_risk_agent_thought(self, thought: str, metadata: Optional[Dict] = None):
        """Log Risk Agent's analysis"""
        self.messages.append(ConversationMessage(
            timestamp=datetime.now(),
            agent="Risk Agent",
            message_type="thought",
            content=thought,
            metadata=metadata
        ))
    
    def log_risk_agent_decision(self, approved: bool, reason: str, risk_score: float):
        """Log Risk Agent's approval/rejection"""
        status = "✅ APPROVED" if approved else "❌ REJECTED"
        self.messages.append(ConversationMessage(
            timestamp=datetime.now(),
            agent="Risk Agent",
            message_type="decision",
            content=f"{status}: {reason} (Risk Score: {risk_score:.2f}/10)",
            metadata={"approved": approved, "risk_score": risk_score}
        ))
    
    def log_payment_agent_action(self, action: str, metadata: Optional[Dict] = None):
        """Log Payment Agent's execution plan"""
        self.messages.append(ConversationMessage(
            timestamp=datetime.now(),
            agent="Payment Agent",
            message_type="action",
            content=action,
            metadata=metadata
        ))
    
    def get_conversation_log(self) -> List[Dict]:
        """Get all messages as dict list for display"""
        return [
            {
                "timestamp": msg.timestamp.strftime("%H:%M:%S"),
                "agent": msg.agent,
                "type": msg.message_type,
                "content": msg.content,
                "metadata": msg.metadata or {}
            }
            for msg in self.messages
        ]
    
    def get_latest_messages(self, n: int = 10) -> List[Dict]:
        """Get latest N messages"""
        return self.get_conversation_log()[-n:]
    
    def clear(self):
        """Clear all messages"""
        self.messages = []
        self.current_cycle_id = None
    
    def export_to_json(self) -> str:
        """Export conversation to JSON"""
        return json.dumps(self.get_conversation_log(), indent=2)

# Global logger instance
_global_logger = AgentConversationLogger()

def get_conversation_logger() -> AgentConversationLogger:
    """Get the global conversation logger"""
    return _global_logger

