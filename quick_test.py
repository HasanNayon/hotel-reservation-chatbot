"""Quick test for the fix."""
from bot import HotelChatbot

bot = HotelChatbot(auto_train=True)

print("=" * 60)
print("Testing Fixed Validation")
print("=" * 60)

test_cases = [
    "who are you?",
    "what are you?",
    "tell me about you",
    "your name",
    "aklsdfhasdihf",
    "12345",
    "zzzzz",
    "Do you have rooms?",
]

for query in test_cases:
    result = bot.respond(query)
    status = "✅" if result["intent"] != "invalid_input" else "❌"
    print(f"\n{status} Query: '{query}'")
    print(f"   Intent: {result['intent']}")
    print(f"   Response: {result['response'][:80]}...")
