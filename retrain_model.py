"""Retrain the chatbot model from scratch."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from bot import HotelChatbot

print("Retraining chatbot model from scratch...")
print("Loading training data...")

bot = HotelChatbot(auto_train=True, confidence_threshold=0.25)

print(f"✓ Model trained successfully!")
print(f"✓ Training data: {len(bot.state.training_rows)} rows")
print(f"✓ Model saved to: artifacts/intent_classifier.joblib")
print(f"✓ Vectorizer saved to: artifacts/tfidf_vectorizer.joblib")

# Quick validation
test_queries = [
    "Do you have rooms available?",
    "What types of rooms do you offer?",
    "what is the check in time",
    "Tell me a joke",
]

print("\nQuick validation:")
for query in test_queries:
    result = bot.respond(query)
    print(f"  '{query}' → {result['intent']} ({result['confidence']:.2f})")

print("\n✓ Retraining complete!")
