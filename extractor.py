
from typing import Type

from google import genai
from google.genai import types
from pydantic import BaseModel, ValidationError

SYSTEM_PROMPT = """
You are a precise information extraction engine.
Extract only information explicitly present in the input text.
Never invent missing personal, educational, employment, or financial details.
Use null for missing optional fields and empty lists for missing arrays.
Preserve names, dates, identifiers, and currency accurately.
For invoice items, extract quantity, unit price, and line total separately.
Return valid JSON matching the requested structure.
"""


class ExtractionError(Exception):
    """User-readable extraction error."""


def friendly_error(exc: Exception) -> str:
    message = str(exc)
    lower = message.lower()

    if "429" in message or "quota" in lower or "resource_exhausted" in lower:
        return "Gemini API quota or rate limit reached. Check your API quota."
    if "401" in message or "unauthenticated" in lower:
        return "Authentication failed. Check your Gemini API key."
    if "403" in message or "permission_denied" in lower:
        return "Gemini access denied. Check API permissions and quota."
    if "404" in message or "not_found" in lower:
        return "Gemini model not found. Check your GEMINI_MODEL setting."
    if "503" in message or "unavailable" in lower:
        return "Gemini is temporarily unavailable. Please retry."
    if "timeout" in lower or "deadline" in lower:
        return "Request timed out. Try shorter input text."

    return f"Extraction failed: {message[:400]}"


def extract(
    api_key: str,
    text: str,
    schema: Type[BaseModel],
    model: str = "gemini-3.8-flash",
) -> BaseModel:

    if not api_key or not api_key.strip():
        raise ExtractionError("Gemini API key is missing.")

    if not text or not text.strip():
        raise ExtractionError("Input text cannot be empty.")

    try:
        client = genai.Client(api_key=api_key.strip())

        # Build a JSON schema compatible with Gemini's API.
        json_schema = schema.model_json_schema()
        json_schema.pop("additionalProperties", None)

        # Remove Pydantic's unsupported additionalProperties
        # wherever it appears inside nested schema objects.
        def clean_schema(obj):
            if isinstance(obj, dict):
                obj.pop("additionalProperties", None)
                for value in obj.values():
                    clean_schema(value)
            elif isinstance(obj, list):
                for value in obj:
                    clean_schema(value)

        clean_schema(json_schema)

        response = client.models.generate_content(
            model=model.strip(),
            contents=text.strip(),
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=json_schema,
                temperature=0.1,
            ),
        )

    except Exception as exc:
        raise ExtractionError(friendly_error(exc)) from exc

    raw_text = getattr(response, "text", None)

    if not raw_text:
        raise ExtractionError(
            "Gemini returned an empty response. Please retry."
        )

    try:
        # Pydantic validates the final result locally.
        return schema.model_validate_json(raw_text)
    except ValidationError as exc:
        raise ExtractionError(
            "Gemini returned JSON that does not match the expected schema. "
            "Try again or simplify the input."
        ) from exc
