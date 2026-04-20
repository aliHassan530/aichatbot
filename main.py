
# ================================================
# VERCEL SERVERLESS SUPPORT (MUST BE AT THE BOTTOM)
# ================================================
# from mangum import Mangum

# This is what Vercel will call
# handler = Mangum(app)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import logging
import os

logger = logging.getLogger(__name__)

app = FastAPI(title="MetaSum POS AI Assistant")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================================
# OPTIMIZED SYSTEM PROMPT (With Play Store Links)
# ================================================
SYSTEM_PROMPT = """
You are the official AI Assistant for **Sum Cloud POS (MetaSum)**.

### STRICT RULES:
1. **Language Rule:**
   - If the user asks in **English**, reply in **English**.
   - If the user asks in **Urdu** or **Roman Urdu**, still reply in **clear and professional English**.

2. Only use the information given below. Never guess or add extra information.
3. If you don't know the answer, reply professionally: "Please contact our team for further assistance."

4. Always be friendly, helpful, and professional.

=== COMPANY INFO ===
Company: The Meta Sum
Website: https://app.themetasum.com
Owner: Kashif Rasheed
Mobile App Developer: Mesum Naqvi
Quality Assurance: Summya Naeem
Contact: +92 317 4088510 (Phone & WhatsApp)
Email: info@themetasum.com

=== DOWNLOAD OUR APPS ===
- **Sum Cloud POS App** (Main POS for counter & billing):  
  https://play.google.com/store/apps/details?id=com.themetasum.sumcloudpos

- **Table Time App** (Waiter App for restaurants):  
  https://play.google.com/store/apps/details?id=com.themetasum.tabletime

=== ABOUT SUM CLOUD POS ===
Sum Cloud POS is a modern cloud-based Point of Sale system for Pakistan and Saudi Arabia. 
Perfect for retail, grocery, restaurants, cafes, clothing, and electronics stores.

=== SUPPORTED PLATFORMS ===
- Web App: app.themetasum.com
- Android Apps (above links)
- iOS Apps on App Store
- Windows Desktop App (with offline support)

All platforms sync in real-time with one account.

=== FREE TRIAL ===
3 days free trial. Setup in 45 seconds. No credit card required.  
Register at: https://app.themetasum.com

=== KEY FEATURES ===
• Fast billing with barcode scanning & split payments  
• Real-time inventory & expiry tracking  
• Multi-branch support  
• Restaurant features: Table management, KDS, QR ordering  
• FBR (Pakistan) & ZATCA (Saudi Arabia) compliance  
• Offline mode with auto sync  
• Detailed reports & analytics

Answer only based on the above information. Keep responses clear and professional.
"""

# ================================================
# MODELS
# ================================================
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[Message] = []

class ChatResponse(BaseModel):
    reply: str
    status: str = "success"


def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY is missing in Vercel environment variables.",
        )

    try:
        from groq import Groq, RateLimitError
    except ImportError as exc:
        logger.exception("Groq SDK import failed")
        raise HTTPException(
            status_code=500,
            detail="Groq SDK is not installed on the server. Add 'groq' to requirements.txt.",
        ) from exc

    return Groq(api_key=api_key), RateLimitError

# ================================================
# CHAT ENDPOINT
# ================================================
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    client, rate_limit_error = get_groq_client()

    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Keep only last 8 messages to save tokens
        recent_history = request.history[-8:] if len(request.history) > 8 else request.history
        for msg in recent_history:
            messages.append({"role": msg.role, "content": msg.content})

        messages.append({"role": "user", "content": request.message})

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            max_tokens=800,
            temperature=0.6,
        )

        reply = response.choices[0].message.content.strip()
        return ChatResponse(reply=reply, status="success")

    except rate_limit_error:
        # ← Yeh professional message jab limit puri ho jay
        professional_message = (
            "We're sorry, the chatbot is currently busy due to high demand. "
            "Please contact our support team for immediate assistance:\n\n"
            "📞 WhatsApp / Phone: +92 317 4088510\n"
            "✉️ Email: info@themetasum.com"
        )
        return ChatResponse(
            reply=professional_message,
            status="rate_limit"
        )

    except HTTPException:
        raise

    except Exception:
        logger.exception("Unexpected chat error")
        raise HTTPException(status_code=500, detail="Something went wrong. Please try again.")

@app.get("/health")
async def health():
    return {"status": "running", "message": "MetaSum POS Chatbot is live!"}

# Run: uvicorn main:app --reload
