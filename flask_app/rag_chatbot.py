"""
RAG-powered conversational medical assistant with retrieval, history,
mental health detection, and provider fallback.
"""
import os
import threading

# Force transformers to use tf-keras (backwards-compatible) instead of Keras 3
os.environ["TF_USE_LEGACY_KERAS"] = "1"

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama

try:
    from langchain_groq import ChatGroq
except Exception:
    ChatGroq = None

# ─── Paths ────────────────────────────────────────────────────────────────────
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FAISS_PATH = os.path.join(_BASE_DIR, "medical-chatbot", "vectorstore", "db_faiss")

# ─── Prompts ──────────────────────────────────────────────────────────────────
MEDICAL_PROMPT_TEMPLATE = """You are MediBot, the conversational AI health assistant inside HealthTwin.

Your job:
- Answer the user's question clearly, naturally, and interactively.
- Use the retrieved medical context when it is relevant.
- If the user asks a follow-up question, continue the conversation coherently.
- If the answer is uncertain, say so plainly.
- Do not pretend to diagnose with certainty.
- Keep the tone calm, helpful, and human.
- Prefer short paragraphs and compact bullet points when useful.
- When the user shares health metrics, use them in the answer.
- Always end with: "⚠️ Consult a qualified healthcare professional for personal diagnosis or treatment."

User health profile:
{profile}

Recent conversation:
{history}

Retrieved medical context:
{context}

Latest user message:
{input}

MediBot response:"""

MENTAL_HEALTH_PROMPT_TEMPLATE = """You are MediBot, an empathetic conversational health assistant inside HealthTwin.

The user may be distressed. Your job:
- Start with empathy and validation.
- Be calm, supportive, and non-judgmental.
- Give grounded coping suggestions and relevant educational information.
- Encourage real-world support from a licensed professional.
- If the risk is high, clearly encourage urgent help and mention crisis support.
- Do not sound robotic or overly formal.
- Keep the response supportive but practical.

User health profile:
{profile}

Recent conversation:
{history}

Retrieved medical and psychological context:
{context}

Latest user message:
{input}

Compassionate MediBot response:"""

# ─── Mental Health Detection ───────────────────────────────────────────────────
_MH_HIGH = [
    "suicide", "suicidal", "kill myself", "end my life", "end it all",
    "self harm", "self-harm", "cutting myself", "hurt myself",
    "don't want to live", "no reason to live", "worthless", "hopeless",
    "can't go on", "want to die", "better off dead"
]
_MH_MEDIUM = [
    "depressed", "depression", "anxiety", "anxious", "panic attack",
    "panic", "breakdown", "mental breakdown", "overwhelming sadness",
    "can't sleep", "insomnia from stress", "crying all the time",
    "feel empty", "numb", "traumatized", "ptsd"
]
_MH_LOW = [
    "stressed", "stress", "worried", "sad", "feeling down", "lonely",
    "burnt out", "burnout", "exhausted mentally", "overwhelmed",
    "unmotivated", "mood swings", "irritable", "anxious feeling"
]

def detect_mental_health(message: str) -> dict:
    """Analyse message for mental health distress signals."""
    msg_lower = message.lower()

    for kw in _MH_HIGH:
        if kw in msg_lower:
            return {"detected": True, "severity": "high", "category": "crisis"}

    for kw in _MH_MEDIUM:
        if kw in msg_lower:
            return {"detected": True, "severity": "medium", "category": "mental_health"}

    for kw in _MH_LOW:
        if kw in msg_lower:
            return {"detected": True, "severity": "low", "category": "emotional_wellness"}

    return {"detected": False, "severity": None, "category": None}


# ─── Singleton RAG components (lazy-loaded, thread-safe) ──────────────────────
_lock = threading.Lock()
_vectorstore = None
_embedding_model = None
_llm = None


def _get_vectorstore():
    global _vectorstore, _embedding_model
    if _vectorstore is None:
        with _lock:
            if _vectorstore is None:
                _embedding_model = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2",
                    model_kwargs={"device": "cpu"}
                )
                _vectorstore = FAISS.load_local(
                    DB_FAISS_PATH,
                    _embedding_model,
                    allow_dangerous_deserialization=True
                )
    return _vectorstore


def _get_llm():
    global _llm
    if _llm is None:
        with _lock:
            if _llm is None:
                groq_key = os.environ.get("GROQ_API_KEY", "").strip()
                if groq_key and ChatGroq is not None:
                    _llm = ChatGroq(
                        api_key=groq_key,
                        model=os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant"),
                        temperature=0.3,
                        max_tokens=900,
                    )
                else:
                    _llm = ChatOllama(
                        model="llama3.2",
                        temperature=0.4,
                        num_predict=700,
                        num_gpu=0,
                    )
    return _llm


def _format_history(history):
    if not history:
        return "No earlier conversation."

    turns = []
    for item in history[-6:]:
        role = item.get("role", "user")
        content = (item.get("content") or "").strip()
        if not content:
            continue
        speaker = "User" if role == "user" else "MediBot"
        turns.append(f"{speaker}: {content}")
    return "\n".join(turns) if turns else "No earlier conversation."


def _format_profile(user_profile):
    if not user_profile:
        return "No health profile provided."

    fields = [
        ("Age", user_profile.get("age")),
        ("Gender", user_profile.get("gender")),
        ("Weight (kg)", user_profile.get("weight")),
        ("Height (cm)", user_profile.get("height")),
        ("BMI", user_profile.get("bmi")),
        ("Sleep (hours)", user_profile.get("sleep")),
        ("Steps", user_profile.get("steps")),
        ("Water (L)", user_profile.get("water")),
        ("Heart rate", user_profile.get("heart_rate")),
        ("Health score", user_profile.get("health_score")),
        ("Obesity risk", user_profile.get("obesity_risk")),
        ("Fatigue risk", user_profile.get("fatigue_risk")),
    ]
    lines = [f"{label}: {value}" for label, value in fields if value not in (None, "", [])]
    return "\n".join(lines) if lines else "No health profile provided."


def _retrieve_context(user_message):
    try:
        docs = _get_vectorstore().similarity_search(user_message, k=4)
        context = "\n\n".join((doc.page_content or "").strip() for doc in docs if doc.page_content)
        return docs, context or "No matching medical context found.", None
    except Exception as exc:
        return [], "Medical knowledge base is temporarily unavailable.", str(exc)


def _build_prompt(prompt_template, user_message, history, user_profile, context):
    return prompt_template.format(
        profile=_format_profile(user_profile),
        history=_format_history(history),
        context=context,
        input=user_message,
    )


def chat(user_message: str, history=None, user_profile=None) -> dict:
    """
    Main entry point for the chatbot.
    Returns:
        {
            "answer": str,
            "mental_health": { detected, severity, category },
            "sources": [ { "source": str, "snippet": str } ]
        }
    """
    mh = detect_mental_health(user_message)

    history = history or []
    user_profile = user_profile or {}

    if mh["detected"] and mh["severity"] in ("high", "medium"):
        prompt_template = MENTAL_HEALTH_PROMPT_TEMPLATE
    else:
        prompt_template = MEDICAL_PROMPT_TEMPLATE

    try:
        docs, context, retrieval_error = _retrieve_context(user_message)
        prompt = _build_prompt(prompt_template, user_message, history, user_profile, context)
        llm = _get_llm()
        llm_result = llm.invoke(prompt)
        answer = getattr(llm_result, "content", str(llm_result)).strip()
        if retrieval_error:
            answer += (
                "\n\nNote: I answered without the local medical knowledge base because it could not be loaded on this device."
            )

        # Extract source citations
        sources = []
        seen = set()
        for doc in docs:
            src = doc.metadata.get("source", "Medical Reference")
            # Shorten to filename
            src_name = os.path.basename(src) if src else "Medical Reference"
            snippet = doc.page_content[:180].replace("\n", " ").strip() + "..."
            key = src_name + snippet[:40]
            if key not in seen:
                seen.add(key)
                sources.append({"source": src_name, "snippet": snippet})

        return {
            "answer": answer,
            "mental_health": mh,
            "sources": sources[:3]
        }

    except Exception as e:
        error_msg = str(e)
        # Friendly error messages for known failure modes
        if "connection" in error_msg.lower() or "refused" in error_msg.lower():
            answer = (
                "⚠️ **MediBot is offline.** No AI provider is responding right now. "
                "If you're using Ollama, start it with `ollama serve`. "
                "If you want cloud AI, make sure `GROQ_API_KEY` is loaded from your `.env` file."
            )
        elif "cuda" in error_msg.lower() or "terminated" in error_msg.lower():
            answer = (
                "⚠️ **GPU error detected.** The model crashed due to a CUDA/VRAM issue. "
                "Please restart Ollama (`ollama serve`) and try again. "
                "If the issue persists, the model is now configured to use CPU instead of GPU."
            )
        else:
            answer = f"⚠️ An error occurred: {error_msg}"

        return {
            "answer": answer,
            "mental_health": mh,
            "sources": []
        }
