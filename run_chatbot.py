"""Simple CLI interface for the hotel chatbot."""
from __future__ import annotations

import argparse
from pathlib import Path

from bot import HotelChatbot


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Interact with the hotel reservation chatbot.")
    parser.add_argument("--no-train", action="store_true", help="Skip model training and load existing artifacts")
    parser.add_argument("--data", type=Path, default=None, help="Custom training_data.csv path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    bot = HotelChatbot(training_data_path=args.data, auto_train=not args.no_train)
    print("🏨 Hotel chatbot ready with keyword-based matching and conversation memory!")
    print("Type 'quit' to exit, 'reset' to clear conversation context.\n")
    
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in {"quit", "exit"}:
            print("Bot: Goodbye!")
            break
        if user_input.lower() == "reset":
            bot.reset_context()
            print("Bot: Conversation context cleared. How can I help you?\n")
            continue
        
        result = bot.respond(user_input)
        print(f"Bot ({result['intent']} @ {result['confidence']:.2f}): {result['response']}")
        
        # Show context if available
        if result.get('context') and result['context'] != f"Hotel: {bot.state.hotel_info.metadata.get('name', 'Sunset Bay Hotel')}":
            print(f"💭 Context: {result['context']}")
        print()


if __name__ == "__main__":
    main()
