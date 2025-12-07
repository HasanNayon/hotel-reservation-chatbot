"""Rule-based dialogue policies and response rendering with context awareness."""
from __future__ import annotations

import random
from datetime import datetime
from typing import Dict, Optional

from .data_loader import HotelInfo
from .context_manager import ConversationContext


class DialogueManager:
    def __init__(self, hotel_info: HotelInfo, context: Optional[ConversationContext] = None) -> None:
        self.hotel_info = hotel_info
        self.responses = hotel_info.responses
        self.default_response = "I'm not sure I understood that. Could you rephrase?"
        self.context = context or ConversationContext(
            hotel_name=hotel_info.metadata.get("name", "Sunset Bay Hotel"),
            hotel_address=hotel_info.metadata.get("address", ""),
            hotel_phone=hotel_info.metadata.get("phone", ""),
            hotel_email=hotel_info.metadata.get("email", ""),
        )

    def respond(self, intent: str, entities: Dict[str, object]) -> str:
        # Update conversation context with new entities
        self.context.update_from_entities(entities)
        
        # Build response context using both current entities and remembered context
        template = self.responses.get(intent) or self.responses.get("unknown", self.default_response)
        response_context = self._build_context(intent, entities)
        
        try:
            response = template.format(**response_context)
            
            return response
        except KeyError:
            # Missing placeholder -> fall back to default response
            return self.default_response
    
    def _format_remembered_context(self) -> str:
        """Format remembered context for display."""
        parts = []
        if self.context.check_in:
            parts.append(f"Check-in: {self.context.check_in}")
        if self.context.check_out:
            parts.append(f"Check-out: {self.context.check_out}")
        if self.context.room_type:
            parts.append(f"Room: {self.context.room_type}")
        if self.context.adults:
            guest_text = f"{self.context.adults} adult{'s' if self.context.adults != 1 else ''}"
            if self.context.children:
                guest_text += f", {self.context.children} child{'ren' if self.context.children != 1 else ''}"
            parts.append(f"Guests: {guest_text}")
        return " | ".join(parts)

    def _build_context(self, intent: str, entities: Dict[str, object]) -> Dict[str, object]:
        # Use remembered context as fallback for missing entities
        hotel_name = self.hotel_info.metadata.get("name", "our hotel")
        
        # Use current entities or fall back to remembered context
        room_type = (
            entities.get("room_type") or 
            self._lookup_room_name(entities.get("room_code")) or
            self.context.room_type or
            "room"
        )
        room_code = entities.get("room_code") or self.context.room_code
        
        adults = entities.get("adults") or self.context.adults
        children = entities.get("children") or self.context.children
        check_in = entities.get("check_in") or self.context.check_in or "your arrival date"
        check_out = entities.get("check_out") or self.context.check_out or "your departure date"
        guests_total = entities.get("guests_total") or self.context.guests_total or adults or "your group"
        amenity = entities.get("amenity", "the amenity")
        price = self._estimate_price(room_code, check_in if check_in != "your arrival date" else None)
        reservation_id = entities.get("reservation_id") or self.context.reservation_id or "your reservation"
        
        children_txt = ""
        if isinstance(children, int) and children > 0:
            children_txt = f"and {children} children"

        context = {
            "hotel_name": hotel_name,
            "room_type": room_type,
            "check_in": check_in,
            "check_out": check_out,
            "nights": entities.get("nights", ""),
            "adults": adults or guests_total,
            "children": children,
            "children_txt": children_txt,
            "guests_total": guests_total,
            "amenity": amenity,
            "price": price or "our nightly rate",
            "reservation_id": reservation_id,
        }

        if intent == "inquire_price" and price is None:
            context["price"] = self._estimate_price("STD", datetime.now().date().isoformat()) or 150
        return context

    def _lookup_room_name(self, code: Optional[str]) -> Optional[str]:
        if not code:
            return None
        for room in self.hotel_info.room_types:
            if room.get("code") == code:
                return room.get("name")
        return None

    def _estimate_price(self, room_code: Optional[str], check_in: Optional[str]) -> Optional[float]:
        if not room_code:
            return None
        room = next((r for r in self.hotel_info.room_types if r.get("code") == room_code), None)
        if not room:
            return None
        base = room.get("base_price_weekday")
        weekend = room.get("base_price_weekend")
        if check_in:
            try:
                weekday = datetime.fromisoformat(str(check_in)).weekday()
                base_rate = weekend if weekday >= 4 else base
            except ValueError:
                base_rate = base
        else:
            base_rate = base
        if base_rate is None:
            return None
        surge = random.uniform(0.95, 1.15)
        price = round(float(base_rate) * surge, 2)
        return price
