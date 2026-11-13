"""
KRISHIVA AI — Google GenAI SDK Provider Integration
Interfaces with Google Gemini (gemini-2.5-flash) for reasoning, structured extraction,
multimodal crop symptom explanation, and farmer-language query interpretation.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel
from backend.config.settings import settings
from backend.core.logging import get_logger

logger = get_logger("google_ai_provider")


class GeminiExplanationRequest(BaseModel):
    farmer_query: str
    crop: str
    diagnostics_summary: str
    preferred_language: str = "en"  # "en", "te", "hi"


class GeminiExplanationResponse(BaseModel):
    explanation_text: str
    farmer_action_summary: str
    safety_reminder: str
    model_used: str
    is_live_genai: bool


class GoogleAIProvider:
    """Provides secure, structured access to Google Gemini models."""

    def __init__(self):
        self.api_key = settings.GOOGLE_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self._client = None
        self._init_client()

    def _init_client(self):
        if self.api_key and self.api_key != "your_google_gemini_api_key_here":
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
                logger.info(f"Initialized Google GenAI client with model {self.model_name}")
            except Exception as e:
                logger.warning(f"Could not initialize Google GenAI SDK ({e}). Fallback mode active.")
                self._client = None
        else:
            logger.info("Google API Key not set; operating in structured deterministic explanation mode.")

    def explain_advisory_to_farmer(self, req: GeminiExplanationRequest) -> GeminiExplanationResponse:
        """Synthesizes technical diagnostic and market data into trusted, farmer-friendly guidance."""
        if self._client:
            try:
                prompt = f"""
You are KRISHIVA AI's Senior Agricultural Agronomist communicating with an Indian farmer.
Crop: {req.crop}
Farmer's Reported Issue: {req.farmer_query}
Diagnostic and Agronomic Assessment: {req.diagnostics_summary}
Language Code: {req.preferred_language}

Explain clearly:
1. What is happening in their field in simple, respectful agronomic terms.
2. Immediate practical actions they should take today.
3. Crucial safety warnings regarding spray timing and harvest waiting period (PHI).
Do NOT invent chemical names or unapproved dosages. Rely solely on the provided diagnostic assessment.
"""
                response = self._client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                text = response.text if hasattr(response, "text") else str(response)
                return GeminiExplanationResponse(
                    explanation_text=text,
                    farmer_action_summary="Follow the step-by-step guidance above carefully.",
                    safety_reminder="Always wear protective masks during application and observe statutory pre-harvest intervals.",
                    model_used=self.model_name,
                    is_live_genai=True
                )
            except Exception as e:
                logger.error(f"Live Gemini invocation failed: {e}. Falling back to domain template.")

        # High-rigor domain-expert template fallback
        if req.preferred_language == "te":
            explanation = (
                f"నమస్కారం రైతు సోదరులారా. మీ {req.crop} పంటలో గమనించిన లక్షణాలు విశ్లేషించబడ్డాయి. "
                f"వివరణ: {req.diagnostics_summary}. "
                f"సూచన: మొదటిగా పాడైన ఆకులను తీసివేసి పొలం బయట కాల్చివేయండి. సిఫార్సు చేసిన మోతాదులో మాత్రమే స్ప్రే చేయండి."
            )
            action = "పాడైన ఆకులను తొలగించండి, డ్రిప్ లేదా మట్టిలో తేమను క్రమబద్ధీకరించండి."
            safety = "మందు పిచికారీ చేసేటప్పుడు రక్షణ ముసుగు మరియు చేతి తొడుగులు ధరించండి. కోతకు ముందు నిర్దేశించిన వ్యవధిని పాటించండి."
        elif req.preferred_language == "hi":
            explanation = (
                f"किसान भाई, आपकी {req.crop} की फसल में बताए गए लक्षणों का वैज्ञानिक परीक्षण किया गया है। "
                f"आकलन: {req.diagnostics_summary}। "
                f"अनुशंसा: रोगग्रस्त पत्तियों को तुरंत खेत से दूर नष्ट करें और अनुमोदित मात्रा का ही उपयोग करें।"
            )
            action = "संक्रमित भागों को हटाएं और जल निकासी सुनिश्चित करें।"
            safety = "छिड़काव के समय मास्क और दस्ताने पहनें। तुड़ाई से पहले अनिवार्य प्रतीक्षा अवधि (PHI) का ध्यान रखें।"
        else:
            explanation = (
                f"Agronomic evaluation for your {req.crop} crop has been completed based on verified field evidence: "
                f"{req.diagnostics_summary}. "
                f"Recommended immediate action: Practice field hygiene by roguing severely diseased lower leaves, "
                f"ensure canopy aeration, and strictly adhere to the verified regulatory dosage."
            )
            action = "Prune lower infected foliage, regulate irrigation to keep canopy dry, apply verified input."
            safety = "Strictly adhere to CIB&RC approved pre-harvest waiting periods (PHI) to prevent residue contamination."

        return GeminiExplanationResponse(
            explanation_text=explanation,
            farmer_action_summary=action,
            safety_reminder=safety,
            model_used="domain-agronomic-synthesizer",
            is_live_genai=False
        )
