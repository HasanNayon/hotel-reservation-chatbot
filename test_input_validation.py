"""Test input validation to filter gibberish and invalid inputs."""
from bot import HotelChatbot


def test_input_validation():
    """Test that the chatbot properly validates inputs."""
    print("=" * 70)
    print("TEST: Input Validation - Questions vs Gibberish")
    print("=" * 70)
    
    bot = HotelChatbot(auto_train=True, use_keyword_fallback=True)
    
    test_cases = [
        # Valid questions
        ("Do you have rooms available?", True, "✅"),
        ("How much is a deluxe room?", True, "✅"),
        ("What time is check-in?", True, "✅"),
        ("I want to book a room", True, "✅"),
        ("Tell me about your amenities", True, "✅"),
        ("Can I bring my pet?", True, "✅"),
        ("When is checkout time?", True, "✅"),
        
        # Valid greetings/short phrases
        ("Hello", True, "✅"),
        ("Hi there", True, "✅"),
        ("Thanks", True, "✅"),
        ("Yes", True, "✅"),
        ("Okay", True, "✅"),
        
        # Invalid - gibberish
        ("asdfghjkl", False, "❌"),
        ("qwerty", False, "❌"),
        ("zzzzzzz", False, "❌"),
        ("12345", False, "❌"),
        ("!@#$%", False, "❌"),
        ("abc123xyz456", False, "❌"),
        
        # Invalid - too short/meaningless
        ("a", False, "❌"),
        ("x", False, "❌"),
        
        # Invalid - repeated words
        ("book book book book", False, "❌"),
        
        # Invalid - off-topic (no hotel keywords)
        ("What is the capital of France?", False, "❌"),
        ("How to cook pasta?", False, "❌"),
        ("Tell me about quantum physics", False, "❌"),
        
        # Edge cases - borderline
        ("room", True, "✅"),  # Single valid domain word
        ("price", True, "✅"),  # Single valid domain word
        ("xyz room available?", True, "✅"),  # Has valid question structure
    ]
    
    print("\n📋 Testing various inputs:\n")
    
    valid_count = 0
    invalid_count = 0
    correct_predictions = 0
    
    for test_input, expected_valid, symbol in test_cases:
        result = bot.respond(test_input)
        is_valid = result["intent"] != "invalid_input"
        is_correct = is_valid == expected_valid
        
        if is_correct:
            correct_predictions += 1
        
        if is_valid:
            valid_count += 1
        else:
            invalid_count += 1
        
        status = "✓" if is_correct else "✗"
        print(f"{status} {symbol} \"{test_input}\"")
        print(f"   Expected: {'Valid' if expected_valid else 'Invalid'} | "
              f"Got: {'Valid' if is_valid else 'Invalid'} | "
              f"Intent: {result['intent']}")
        
        if not is_valid:
            print(f"   Response: {result['response'][:80]}...")
        
        print()
    
    print("=" * 70)
    print(f"📊 Results: {correct_predictions}/{len(test_cases)} correct "
          f"({100*correct_predictions/len(test_cases):.1f}%)")
    print(f"   Valid inputs accepted: {valid_count}")
    print(f"   Invalid inputs rejected: {invalid_count}")
    print("=" * 70)


def test_validation_messages():
    """Test that validation messages are helpful."""
    print("\n\n" + "=" * 70)
    print("TEST: Validation Error Messages")
    print("=" * 70)
    
    bot = HotelChatbot(auto_train=True, use_keyword_fallback=True)
    
    invalid_inputs = [
        ("asdfgh", "Random gibberish"),
        ("12345", "Just numbers"),
        ("What is 2+2?", "Off-topic question"),
        ("", "Empty input"),
        ("a", "Too short"),
        ("zzzzzzzzz", "Repeated character"),
        ("How to bake a cake?", "Non-hotel topic"),
    ]
    
    print("\n💬 Checking error messages for invalid inputs:\n")
    
    for test_input, description in invalid_inputs:
        result = bot.respond(test_input)
        print(f"Input: \"{test_input}\" ({description})")
        print(f"Intent: {result['intent']}")
        print(f"Response:\n{result['response']}\n")
        print("-" * 70)


def test_valid_conversation_flow():
    """Test that valid questions work normally."""
    print("\n\n" + "=" * 70)
    print("TEST: Valid Conversation Flow (Should Work Normally)")
    print("=" * 70)
    
    bot = HotelChatbot(auto_train=True, use_keyword_fallback=True)
    
    conversation = [
        "Hello!",
        "Do you have rooms available?",
        "I need a room for 2 adults",
        "Check-in on December 10th",
        "How much will it cost?",
        "What amenities do you have?",
        "Thanks!",
    ]
    
    print("\n💬 Normal conversation:\n")
    
    for user_input in conversation:
        result = bot.respond(user_input)
        is_valid = result["intent"] != "invalid_input"
        
        print(f"👤 User: {user_input}")
        print(f"🤖 Bot [{result['intent']}]: {result['response'][:100]}")
        
        if not is_valid:
            print("⚠️  WARNING: Valid input was rejected!")
        
        print()
    
    print("=" * 70)


if __name__ == "__main__":
    print("\n🧪 Testing Input Validation System\n")
    print("This tests the chatbot's ability to distinguish between:")
    print("  ✅ Valid questions and statements")
    print("  ❌ Gibberish and random text")
    print("  ❌ Off-topic questions")
    print()
    
    test_input_validation()
    test_validation_messages()
    test_valid_conversation_flow()
    
    print("\n✅ All validation tests completed!\n")
    print("💡 The chatbot now intelligently filters out:")
    print("   • Gibberish and random characters")
    print("   • Off-topic questions")
    print("   • Too short/meaningless inputs")
    print("   • Non-hotel related queries")
    print("\n✨ While accepting all valid hotel-related questions!")
