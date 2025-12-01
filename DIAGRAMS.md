# Hotel Chatbot System Diagrams

To view these diagrams visually:
1. Open this file in VS Code.
2. Press `Ctrl+Shift+V` (or `Cmd+Shift+V` on Mac) to open the **Markdown Preview**.

## 1. High-Level System Architecture
This diagram shows how the different Python modules interact with each other.

```mermaid
graph TD
    User((User)) <--> UI[Streamlit UI<br>app.py]
    UI <--> Bot[HotelBot Orchestrator<br>bot/bot.py]
    
    subgraph "Core Logic"
        Bot --> Validator[Input Validator<br>bot/input_validator.py]
        Bot --> Context[Context Manager<br>bot/context_manager.py]
        Bot --> Hybrid[Hybrid Classifier]
        Bot --> DM[Dialogue Manager<br>bot/dialogue_manager.py]
    end
    
    subgraph "NLU Engine"
        Hybrid --> ML[ML Intent Classifier<br>bot/intent_classifier.py]
        Hybrid --> KW[Keyword Matcher<br>bot/keyword_matcher.py]
        Hybrid --> NER[Entity Extractor<br>bot/entity_extractor.py]
    end
    
    subgraph "Data Layer"
        DM --> DL[Data Loader<br>bot/data_loader.py]
        DL --> CSV[(CSV Files)]
    end
```

## 2. Message Processing Sequence
This sequence diagram illustrates the step-by-step flow of a single user message.

```mermaid
sequenceDiagram
    actor User
    participant UI as Streamlit App
    participant Bot as HotelBot
    participant Val as InputValidator
    participant Ctx as ContextManager
    participant NLU as Classifier/Matcher
    participant DM as DialogueManager

    User->>UI: Sends Message
    UI->>Bot: process_message(text)
    
    %% Validation Step
    Bot->>Val: validate_input(text)
    alt Input Invalid
        Val-->>Bot: False, Reason
        Bot-->>UI: Error Response
    else Input Valid
        Val-->>Bot: True
        
        %% Context Update
        Bot->>Ctx: update_history(user_msg)
        
        %% Intent Classification
        Bot->>NLU: predict_intent(text)
        NLU-->>Bot: intent, confidence, entities
        
        %% Response Generation
        Bot->>DM: get_response(intent, entities, context)
        DM-->>Bot: response_text
        
        %% Finalize
        Bot->>Ctx: update_history(bot_msg)
        Bot-->>UI: response_text
    end
    UI->>User: Displays Response
```

## 3. Hybrid Intent Logic
This flowchart details how the bot decides between Machine Learning and Keyword Matching.

```mermaid
flowchart TD
    Start([User Input]) --> ML[ML Model Prediction]
    ML --> Check{Confidence > 0.65?}
    
    Check -- Yes --> MLIntent[Use ML Intent]
    
    Check -- No --> KW[Check Keyword Matcher]
    KW --> KWCheck{Keyword Found?}
    
    KWCheck -- Yes --> KWIntent[Use Keyword Intent]
    KWCheck -- No --> Fallback[Fallback / Unknown]
    
    MLIntent --> Final([Final Intent])
    KWIntent --> Final
    Fallback --> Final
```

## 4. Input Validation Logic
The decision tree used to filter out bad inputs before processing.

```mermaid
graph TD
    Input([Raw Input]) --> Empty{Is Empty?}
    Empty -- Yes --> Reject[Reject: Empty]
    Empty -- No --> Gibberish{Is Gibberish?<br>(Random chars)}
    
    Gibberish -- Yes --> Reject2[Reject: Gibberish]
    Gibberish -- No --> Identity{Is Identity Q?<br>'Who are you?'}
    
    Identity -- Yes --> Accept[Accept]
    Identity -- No --> OffTopic{Is Off-Topic?<br>(Politics/Insults)}
    
    OffTopic -- Yes --> Reject3[Reject: Off-Topic]
    OffTopic -- No --> Accept
```

## 5. Class Structure
The object-oriented structure of the codebase.

```mermaid
classDiagram
    class HotelBot {
        +process_message(text)
        +load_components()
    }
    
    class InputValidator {
        +validate_input(text)
        -_check_gibberish(text)
        -_check_off_topic(text)
    }
    
    class ConversationContext {
        +history: list
        +current_intent: str
        +booking_state: dict
    }
    
    class IntentClassifier {
        +predict(text)
        +train(data)
    }
    
    class KeywordMatcher {
        +match(text)
        +keywords: dict
    }
    
    HotelBot *-- InputValidator
    HotelBot *-- ConversationContext
    HotelBot *-- IntentClassifier
    HotelBot *-- KeywordMatcher
```
