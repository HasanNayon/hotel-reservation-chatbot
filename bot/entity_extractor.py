"""Lightweight rule-based entity extraction."""
from __future__ import annotations

import re
from typing import Dict, List, Optional

from .data_loader import HotelInfo

DATE_PATTERN = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
NIGHTS_PATTERN = re.compile(r"(\d+)\s+nights?")
ADULT_PATTERN = re.compile(r"(\d+)\s+(?:adult|adults)")
CHILD_PATTERN = re.compile(r"(\d+)\s+(?:child|children|kid|kids)")
TOTAL_GUEST_PATTERN = re.compile(r"(\d+)\s+(?:guest|guests|people)")
RESERVATION_PATTERN = re.compile(r"\b[a-f0-9]{8}\b")
TIME_PATTERN = re.compile(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)")


class EntityExtractor:
    """Deterministic entity extraction tailored for the hotel domain."""

    def __init__(self, hotel_info: HotelInfo) -> None:
        self.hotel_info = hotel_info
        self.room_synonyms = self._build_room_synonyms()
        self.amenity_keywords = {k.lower(): k for k in hotel_info.amenity_faq.keys()}

    def _build_room_synonyms(self) -> Dict[str, Dict[str, str]]:
        synonyms: Dict[str, Dict[str, str]] = {}
        manual_synonyms = {
            "standard room": "STD",
            "standard": "STD",
            "queen room": "STD",
            "queen": "STD",
            "deluxe room": "DLX",
            "deluxe": "DLX",
            "king room": "DLX",
            "king": "DLX",
            "twin room": "DLX",
            "twin": "DLX",
            "family suite": "FAM",
            "family room": "FAM",
            "family": "FAM",
            "ocean suite": "STE",
            "ocean view suite": "STE",
            "suite": "STE",
            "ocean": "STE",
        }
        for label, code in manual_synonyms.items():
            synonyms[label] = {"room_code": code, "room_type": self._get_room_name(code)}

        for room in self.hotel_info.room_types:
            code = room.get("code")
            name = room.get("name", "")
            if not code:
                continue
            entries: List[str] = [
                code.lower(),
                name.lower(),
                name.replace("Room", "").replace("Suite", "").strip().lower()
            ]
            beds = room.get("beds", "")
            if beds:
                entries.append(beds.lower())
            for entry in entries:
                label = entry.strip()
                if not label or len(label) < 2:
                    continue
                synonyms[label] = {"room_code": code, "room_type": name}
        return synonyms
    
    def _get_room_name(self, code: str) -> str:
        for room in self.hotel_info.room_types:
            if room.get("code") == code:
                return room.get("name", code)
        return code

    def extract(self, utterance: str) -> Dict[str, object]:
        text = utterance.lower()
        entities: Dict[str, object] = {
            "raw_text": utterance,
        }

        dates = DATE_PATTERN.findall(utterance)
        if dates:
            entities["check_in"] = dates[0]
        if len(dates) >= 2:
            entities["check_out"] = dates[1]
        nights_match = NIGHTS_PATTERN.search(text)
        if nights_match:
            entities["nights"] = int(nights_match.group(1))

        adults_match = ADULT_PATTERN.search(text)
        if adults_match:
            entities["adults"] = int(adults_match.group(1))
        children_match = CHILD_PATTERN.search(text)
        if children_match:
            entities["children"] = int(children_match.group(1))
        total_match = TOTAL_GUEST_PATTERN.search(text)
        if total_match:
            entities["guests_total"] = int(total_match.group(1))

        res_match = RESERVATION_PATTERN.search(text)
        if res_match:
            entities["reservation_id"] = res_match.group(0)

        time_match = TIME_PATTERN.search(text)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2) or 0)
            meridiem = time_match.group(3)
            entities["time_request"] = f"{hour:02d}:{minute:02d} {meridiem}"

        for keyword, amenity in self.amenity_keywords.items():
            if keyword in text:
                entities["amenity"] = amenity
                break

        # Sort room synonyms by length (longest first) to match "ocean suite" before "ocean"
        sorted_synonyms = sorted(self.room_synonyms.items(), key=lambda x: len(x[0]), reverse=True)
        for label, payload in sorted_synonyms:
            if label and label in text:
                entities.update(payload)
                break

        return entities
