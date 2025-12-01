"""Conversation context manager for persistent memory."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class ConversationContext:
    """Stores conversation state and user preferences."""
    
    # Hotel information (always remembered)
    hotel_name: str = "Sunset Bay Hotel"
    hotel_address: str = "123 Seaside Ave, Bayview, CA 94000"
    hotel_phone: str = "+1-415-555-0130"
    hotel_email: str = "contact@sunsetbayhotel.example"
    
    # Current booking context (remembered during conversation)
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    room_type: Optional[str] = None
    room_code: Optional[str] = None
    adults: Optional[int] = None
    children: Optional[int] = None
    guests_total: Optional[int] = None
    
    # Reservation tracking
    reservation_id: Optional[str] = None
    confirmed: bool = False
    
    # Conversation history
    message_history: List[Dict[str, str]] = field(default_factory=list)
    last_intent: Optional[str] = None
    
    # User preferences (learned over time)
    preferred_room_type: Optional[str] = None
    special_requests: List[str] = field(default_factory=list)
    
    def update_from_entities(self, entities: Dict[str, object]) -> None:
        """Update context from extracted entities."""
        if entities.get("check_in"):
            self.check_in = str(entities["check_in"])
        if entities.get("check_out"):
            self.check_out = str(entities["check_out"])
        if entities.get("room_type"):
            self.room_type = str(entities["room_type"])
        if entities.get("room_code"):
            self.room_code = str(entities["room_code"])
        if entities.get("adults"):
            self.adults = int(entities["adults"])
        if entities.get("children"):
            self.children = int(entities["children"])
        if entities.get("guests_total"):
            self.guests_total = int(entities["guests_total"])
        if entities.get("reservation_id"):
            self.reservation_id = str(entities["reservation_id"])
    
    def add_message(self, role: str, content: str, intent: Optional[str] = None) -> None:
        """Add a message to conversation history."""
        self.message_history.append({
            "role": role,
            "content": content,
            "intent": intent or "unknown",
            "timestamp": datetime.now().isoformat(),
        })
        if intent:
            self.last_intent = intent
    
    def get_context_summary(self) -> str:
        """Generate a human-readable summary of current context."""
        parts = [f"Hotel: {self.hotel_name}"]
        
        if self.check_in and self.check_out:
            parts.append(f"Dates: {self.check_in} to {self.check_out}")
        elif self.check_in:
            parts.append(f"Check-in: {self.check_in}")
        
        if self.room_type:
            parts.append(f"Room: {self.room_type}")
        
        if self.adults or self.guests_total:
            guests = self.adults or self.guests_total
            guest_text = f"{guests} guest{'s' if guests != 1 else ''}"
            if self.children:
                guest_text += f" ({self.adults} adults, {self.children} children)"
            parts.append(f"Guests: {guest_text}")
        
        if self.reservation_id:
            status = "Confirmed" if self.confirmed else "Pending"
            parts.append(f"Reservation: {self.reservation_id} ({status})")
        
        return " | ".join(parts)
    
    def get_remembered_entities(self) -> Dict[str, object]:
        """Return all remembered entities as a dictionary."""
        return {
            "check_in": self.check_in,
            "check_out": self.check_out,
            "room_type": self.room_type,
            "room_code": self.room_code,
            "adults": self.adults,
            "children": self.children,
            "guests_total": self.guests_total,
            "reservation_id": self.reservation_id,
        }
    
    def clear_booking(self) -> None:
        """Clear current booking information."""
        self.check_in = None
        self.check_out = None
        self.room_type = None
        self.room_code = None
        self.adults = None
        self.children = None
        self.guests_total = None
        self.reservation_id = None
        self.confirmed = False
    
    def has_partial_booking(self) -> bool:
        """Check if user has started a booking process."""
        return any([
            self.check_in,
            self.check_out,
            self.room_type,
            self.adults,
            self.guests_total,
        ])
