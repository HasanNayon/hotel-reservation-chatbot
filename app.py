"""Streamlit web interface for the hotel reservation chatbot."""
from __future__ import annotations

import streamlit as st
from bot import HotelChatbot


def init_bot():
    """Initialize chatbot once and cache in session state."""
    if "bot" not in st.session_state:
        with st.spinner("Training chatbot model with keyword matching..."):
            st.session_state.bot = HotelChatbot(
                auto_train=True, 
                confidence_threshold=0.25,
                use_keyword_fallback=True
            )
        st.session_state.messages = []


def main():
    st.set_page_config(page_title="Hotel Chatbot", page_icon="🏨", layout="centered")
    
    st.title("🏨 Sunset Bay Hotel Chatbot")
    st.markdown("**Ask me anything about reservations, rooms, amenities, and policies!**")
    
    init_bot()
    
    # Sidebar with info
    with st.sidebar:
        st.header("About")
        st.info(
            "This chatbot handles hotel reservations without using LLMs. "
            "It uses **keyword-based matching** + ML intent classification "
            "and **remembers your booking details** throughout the conversation."
        )
        st.success(
            "✅ **Features**:\n"
            "- Understands paraphrased questions\n"
            "- Remembers hotel information\n"
            "- Tracks your booking context\n"
            "- Keyword + ML hybrid approach"
        )
        st.warning(
            "⚠️ **Scope**: This bot only answers hotel-related questions. "
            "Off-topic queries will be politely redirected."
        )
        st.markdown("---")
        st.subheader("Quick Examples")
        examples = [
            "Do you have rooms from 2025-12-10 to 2025-12-12?",
            "How much is a deluxe room?",
            "Book a suite for 2 adults",
            "What's your cancellation policy?",
            "Do you have parking?",
            "What time is check-in?",
        ]
        for ex in examples:
            if st.button(ex, key=f"ex_{ex[:20]}"):
                st.session_state.user_input = ex
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear Chat"):
                st.session_state.messages = []
                st.rerun()
        with col2:
            if st.button("🔄 Reset Context"):
                st.session_state.bot.reset_context()
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Conversation context cleared. How can I help you?",
                    "metadata": {"intent": "system", "confidence": 1.0, "entities": {}}
                })
                st.rerun()
        
        # Show current context
        if st.session_state.bot:
            context_summary = st.session_state.bot.get_context().get_context_summary()
            st.markdown("---")
            st.subheader("💭 Current Context")
            st.text(context_summary)
    
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and "metadata" in msg:
                with st.expander("🔍 Analysis"):
                    st.json(msg["metadata"])
    
    # Chat input
    user_input = st.chat_input("Type your message here...")
    
    # Handle sidebar example clicks
    if "user_input" in st.session_state:
        user_input = st.session_state.user_input
        del st.session_state.user_input
    
    if user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Get bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = st.session_state.bot.respond(user_input)
            
            response_text = result["response"]
            st.markdown(response_text)
            
            # Show analysis in expander
            metadata = {
                "intent": result["intent"],
                "confidence": round(result["confidence"], 3),
                "entities": {k: v for k, v in result["entities"].items() if v is not None and k != "raw_text"},
                "context": result.get("context", ""),
            }
            
            # Add validation info if input was invalid
            if result["intent"] == "invalid_input" and "validation" in result:
                metadata["validation"] = result["validation"]
            
            with st.expander("🔍 Analysis"):
                st.json(metadata)
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text,
                "metadata": metadata,
            })
        
        st.rerun()


if __name__ == "__main__":
    main()
