"""Utility helpers for loading CSV assets."""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence


@dataclass(frozen=True)
class TrainingRow:
    utterance: str
    intent: str
    entities: Dict[str, object]
    context: str
    language: str
    channel: str
    sentiment: str


@dataclass(frozen=True)
class HotelInfo:
    metadata: Dict[str, str]
    room_types: Sequence[Dict[str, object]]
    amenity_faq: Dict[str, str]
    responses: Dict[str, str]


def _read_csv(path: Path) -> Iterable[Dict[str, str]]:
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            yield row


def load_training_rows(path: Path) -> List[TrainingRow]:
    rows: List[TrainingRow] = []
    for row in _read_csv(path):
        try:
            entities = json.loads(row.get("entities", "{}"))
        except json.JSONDecodeError:
            entities = {}
        rows.append(
            TrainingRow(
                utterance=row.get("utterance", ""),
                intent=row.get("intent", "unknown"),
                entities=entities,
                context=row.get("context", "general"),
                language=row.get("language", "en"),
                channel=row.get("channel", "web"),
                sentiment=row.get("sentiment", "neutral"),
            )
        )
    return rows


def load_hotel_info(
    info_path: Path,
    rooms_path: Path,
    faq_path: Path,
    responses_path: Path,
) -> HotelInfo:
    info_rows = list(_read_csv(info_path))
    metadata = info_rows[0] if info_rows else {}

    room_rows = list(_read_csv(rooms_path))
    for room in room_rows:
        room["view_options"] = [v.strip() for v in room.get("view_options", "").split(",") if v]
        room["amenities"] = [v.strip() for v in room.get("amenities", "").split(",") if v]

    amenity_faq = {row["amenity"]: row["answer"] for row in _read_csv(faq_path)}

    response_rows = {row["intent"]: row["template"] for row in _read_csv(responses_path)}

    return HotelInfo(metadata=metadata, room_types=room_rows, amenity_faq=amenity_faq, responses=response_rows)
