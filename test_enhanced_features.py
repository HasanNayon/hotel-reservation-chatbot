"""Test script to demonstrate keyword matching and conversation memory."""
from bot import HotelChatbot


def test_keyword_matching():
    """Test keyword-based paraphrase handling."""
    print("=" * 60)
    print("TEST 1: Keyword-Based Paraphrase Handling")
    print("=" * 60)
    
    bot = HotelChatbot(auto_train=True, use_keyword_fallback=True)
    
    test_queries = [
        # Different ways to ask about availability
        "Do you have any rooms available?",
        "Are there vacant rooms?",
        "Can I check availability?",
        
        # Different ways to ask about price
        "How much does it cost?",
        "What's the rate?",
        "Tell me the price",
        
        # Different ways to ask about check-in
        "When can I check in?",
        "What time is arrival?",
        "Check-in hour?",
        
        # Different ways to greet
        "Hi there!",
        "Good morning",
        "Hello",
    ]
    
    for query in test_queries:
        result = bot.respond(query)
        print(f"\n📝 Query: {query}")
        print(f"✅ Intent: {result['intent']} (confidence: {result['confidence']:.2f})")
        print(f"💬 Response: {result['response']}")
    
    print("\n" + "=" * 60)


def test_conversation_memory():
    """Test conversation memory and context tracking."""
    print("\n\n" + "=" * 60)
    print("TEST 2: Conversation Memory & Context Tracking")
    print("=" * 60)
    
    bot = HotelChatbot(auto_train=True, use_keyword_fallback=True)
    
    conversation = [
        "I want to book a room for 2 adults",
        "Check-in on 2025-12-10",
        "And check-out on 2025-12-12",
        "I prefer a deluxe room",
        "How much will it cost?",  # Should remember all previous info
        "What about availability?",  # Should still remember dates and guests
    ]
    
    for turn in conversation:
        result = bot.respond(turn)
        print(f"\n👤 User: {turn}")
        print(f"🤖 Bot ({result['intent']}): {result['response']}")
        if result.get('context'):
            print(f"💭 Context: {result['context']}")
    
    print("\n📊 Final Context Summary:")
    context = bot.get_context()
    print(f"  - Hotel: {context.hotel_name}")
    print(f"  - Check-in: {context.check_in}")
    print(f"  - Check-out: {context.check_out}")
    print(f"  - Room Type: {context.room_type}")
    print(f"  - Adults: {context.adults}")
    print(f"  - Message History: {len(context.message_history)} messages")
    
    print("\n" + "=" * 60)


def test_hotel_info_persistence():
    """Test that hotel information is always remembered."""
    print("\n\n" + "=" * 60)
    print("TEST 3: Hotel Information Persistence")
    print("=" * 60)
    
    bot = HotelChatbot(auto_train=True, use_keyword_fallback=True)
    
    queries = [
        "What's your hotel name?",
        "Where are you located?",
        "How can I contact you?",
        "What's your phone number?",
    ]
    
    for query in queries:
        result = bot.respond(query)
        print(f"\n👤 User: {query}")
        print(f"🤖 Bot: {result['response']}")
    
    context = bot.get_context()
    print(f"\n🏨 Hotel Info (Always Available):")
    print(f"  - Name: {context.hotel_name}")
    print(f"  - Address: {context.hotel_address}")
    print(f"  - Phone: {context.hotel_phone}")
    print(f"  - Email: {context.hotel_email}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    print("\n🚀 Testing Enhanced Hotel Chatbot\n")
    print("Features being tested:")
    print("  ✓ Keyword-based paraphrase handling")
    print("  ✓ Conversation memory and context tracking")
    print("  ✓ Persistent hotel information")
    print()
    
    test_keyword_matching()
    test_conversation_memory()
    test_hotel_info_persistence()
    
    print("\n✅ All tests completed!")
    print("\n💡 Try the interactive chatbot with: python run_chatbot.py")
    print("💡 Or launch the web interface with: streamlit run app.py")
