from typing import Dict


# PUBLIC_INTERFACE
def simple_nlu_reply(text: str) -> Dict[str, str]:
    """Return a simple heuristic-based reply for the given text.

    Heuristics:
    - Greeting detection
    - Help intent
    - Fallback echoes the input
    """
    t = (text or "").strip().lower()
    if not t:
        return {"reply": "I didn't catch that. Could you say that again?", "provider": "heuristic"}

    if any(greet in t for greet in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]):
        return {"reply": "Hello! How can I assist you today?", "provider": "heuristic"}

    if "help" in t or "what can you do" in t:
        return {"reply": "I can chat, transcribe your speech, and speak responses back. Ask me anything!", "provider": "heuristic"}

    # Fallback: echo-style response
    return {"reply": f"You said: {text}", "provider": "heuristic"}
