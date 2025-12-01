# Hotel Reservation Chatbot

A self-contained, non-LLM hotel reservation assistant trained on the synthetic dataset in `data/`. It classifies user intents with a traditional ML model, extracts structured entities with rules, and renders responses via deterministic templates.

## UI Screenshots
<p align="center">
  <img src="image/ui_1.png" width="30%" alt="Chatbot UI 1">
  <img src="image/ui_2.png" width="30%" alt="Chatbot UI 2">
  <img src="image/ui_3.png" width="30%" alt="Chatbot UI 3">
</p>

## Features

✨ **Core Capabilities**
- 🤖 **Intent Classification**: ML-powered intent recognition using scikit-learn
- 📝 **Entity Extraction**: Rule-based extraction of dates, guest counts, room types, and amenities
- 💬 **Context Management**: Maintains conversation state across multiple interactions
- 🎯 **Keyword Fallback**: Hybrid approach combining ML and keyword matching
- ✅ **Input Validation**: Detects and handles gibberish, off-topic queries
- 🌐 **Web Interface**: Beautiful Streamlit UI with chat history and context display
- 💻 **CLI Interface**: Terminal-based interactive chatbot

🏨 **Hotel Management**
- Room availability checking
- Multi-room type support (Standard, Deluxe, Suite, Family)
- Dynamic price calculation
- Amenity information (WiFi, parking, pets, gym, pool)
- Policy inquiries (cancellation, check-in/out times)
- Reservation management

## Tech Stack

- **Python 3.12+**
- **Machine Learning**: scikit-learn (TF-IDF + Logistic Regression)
- **Web Framework**: Streamlit
- **Data Processing**: pandas, numpy
- **Serialization**: joblib

## Architecture at a Glance
- **Intent classification**: `scikit-learn` TF-IDF + Logistic Regression pipeline trained on `data/training_data.csv`.
- **Entity extraction**: Rule-based parser in `bot/entity_extractor.py` detects dates, guest counts, reservation IDs, room types, and amenities.
- **Knowledge layer**: `data_loader.py` loads hotel metadata, room inventory, amenity FAQ, and response templates.
- **Dialogue policy**: `dialogue_manager.py` fills templates with hotel facts and extracted slots, including price estimation logic.
- **Orchestration**: `HotelChatbot` stitches everything together and powers the CLI in `run_chatbot.py`.

## Setup
```powershell
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# Windows:
.\.venv\Scripts\Activate.ps1
# Linux/Mac:
# source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

## Train & Run the Bot
```powershell
# Run the CLI chatbot
python run_chatbot.py

# Run the Streamlit Web UI
streamlit run app.py
```
- The script trains a fresh intent model (≈10s) and launches an interactive prompt.
- Use `--no-train` to reuse the last saved model in `artifacts/`.

## Quick Analysis Helper
Inside Python:
```python
from bot import HotelChatbot
bot = HotelChatbot(auto_train=True)
bot.analyze("book a suite for 2 adults 2025-12-10")
```
Returns top intents plus extracted entities for debugging.

## Tests
```powershell
python -m unittest discover -s tests
```

## Project Structure

```
hotel-reservation-chatbot/
├── bot/                          # Core chatbot modules
│   ├── bot.py                   # Main chatbot orchestrator
│   ├── intent_classifier.py     # ML intent classification
│   ├── entity_extractor.py      # Rule-based entity extraction
│   ├── dialogue_manager.py      # Response generation
│   ├── context_manager.py       # Conversation state management
│   ├── input_validator.py       # Input validation & filtering
│   ├── keyword_matcher.py       # Fallback keyword matching
│   ├── data_loader.py           # CSV data loading
│   └── config.py                # Configuration constants
├── data/                         # Training data & knowledge base
│   ├── training_data.csv        # Intent training samples
│   ├── hotel_info.csv           # Hotel metadata
│   ├── room_types.csv           # Room inventory
│   ├── amenity_faq.csv          # Amenity information
│   └── response_templates.csv   # Response templates
├── artifacts/                    # Trained models
│   └── intent_classifier.joblib # Serialized ML model
├── tests/                        # Unit tests
│   └── test_bot.py              # Integration tests
├── image/                        # Documentation images
├── app.py                        # Streamlit web interface
├── run_chatbot.py               # CLI interface
└── requirements.txt             # Python dependencies
```

## Customization Tips
1. Update `data/*.csv` with new hotel facts or paraphrased utterances, then rerun `generate_dataset.py` if needed.
2. Extend `EntityExtractor` with new regex patterns for loyalty IDs, promo codes, etc.
3. Adjust `confidence_threshold` in `HotelChatbot` to tune fallback behavior.
4. Bring your own UI (web, SMS, IVR) by importing `HotelChatbot` and wiring the `respond()` output into your channel.

## How It Works

1. **User Input** → Input validation checks for gibberish/off-topic
2. **Intent Classification** → ML model predicts user intent with confidence score
3. **Keyword Fallback** → If confidence is low, keyword matcher provides fallback
4. **Entity Extraction** → Regex patterns extract structured data (dates, counts, etc.)
5. **Context Management** → Conversation state is updated with extracted entities
6. **Response Generation** → Templates are filled with hotel data and entities
7. **Output** → Formatted response with intent, confidence, and context

## Contributing

Contributions are welcome! Feel free to:
- Report bugs or request features via GitHub Issues
- Submit pull requests for improvements
- Extend the training data with more paraphrases
- Add support for new intents or entities

## License

This project is open source and available under the MIT License.

## Author

**Hasan Nayon**  
GitHub: [@HasanNayon](https://github.com/HasanNayon)

---

⭐ If you find this project helpful, please give it a star!
