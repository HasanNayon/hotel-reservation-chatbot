"""Interactive demo of input validation."""
from bot import HotelChatbot


def main():
    print("=" * 70)
    print("🏨 Hotel Chatbot with Input Validation")
    print("=" * 70)
    print("\n✨ This chatbot now analyzes your input BEFORE processing!")
    print("\nIt will reject:")
    print("  ❌ Gibberish (asdfgh, 12345, !!!)")
    print("  ❌ Off-topic questions (about weather, cooking, math, etc.)")
    print("  ❌ Too short/meaningless inputs (single letters)")
    print("  ❌ Repeated nonsense (book book book book)")
    
    print("\nIt will accept:")
    print("  ✅ Valid hotel questions")
    print("  ✅ Booking requests")
    print("  ✅ Greetings and polite phrases")
    
    print("\n" + "=" * 70)
    print("\nTry these examples:")
    print("  • Valid: 'Do you have rooms available?'")
    print("  • Valid: 'How much is a deluxe room?'")
    print("  • Invalid: 'asdfghjkl' (gibberish)")
    print("  • Invalid: 'What is the capital of France?' (off-topic)")
    print("\nType 'quit' to exit, 'reset' to clear context\n")
    
    bot = HotelChatbot(auto_train=True, use_keyword_fallback=True)
    
    while True:
        user_input = input("You: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() in {"quit", "exit"}:
            print("Bot: Goodbye!")
            break
        
        if user_input.lower() == "reset":
            bot.reset_context()
            print("Bot: Context cleared. How can I help you?\n")
            continue
        
        result = bot.respond(user_input)
        
        # Show if input was rejected
        if result["intent"] == "invalid_input":
            print(f"\n⚠️  INPUT REJECTED")
            print(f"Reason: {result.get('validation', {}).get('reason', 'invalid')}")
            print(f"\n🤖 Bot: {result['response']}\n")
        else:
            print(f"✅ INPUT ACCEPTED")
            print(f"🤖 Bot ({result['intent']} @ {result['confidence']:.2f}): {result['response']}")
            
            if result.get('context') and result['context'] != f"Hotel: {bot.state.hotel_info.metadata.get('name', 'Sunset Bay Hotel')}":
                print(f"💭 Context: {result['context']}")
            print()


if __name__ == "__main__":
    main()
