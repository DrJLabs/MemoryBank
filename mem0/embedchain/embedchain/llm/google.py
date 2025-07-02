import logging
import os
from collections.abc import Generator
from typing import Any, Optional, Union

try:
    import google.generativeai as genai
except ImportError:
    raise ImportError("GoogleLlm requires extra dependencies. Install with `pip install google-generativeai`") from None

from embedchain.config import BaseLlmConfig
from embedchain.helpers.json_serializable import register_deserializable
from .provider_base import ApiKeyLlmBase

logger = logging.getLogger(__name__)


@register_deserializable
class GoogleLlm(ApiKeyLlmBase):
    """Google Gemini/PaLM-based LLM wrapper."""

    env_var_name = "GOOGLE_API_KEY"

    def _post_init_setup(self):
        # Configure Google generative AI client with resolved API key.
        genai.configure(api_key=self.api_key)

    def _get_answer(self, prompt: str) -> Union[str, Generator[Any, Any, None]]:
        model_name = self.config.model or "gemini-pro"
        logger.info(f"Using Google LLM model: {model_name}")
        model = genai.GenerativeModel(model_name=model_name)

        generation_config_params = {
            "candidate_count": 1,
            "max_output_tokens": self.config.max_tokens,
            "temperature": self.config.temperature or 0.5,
        }

        if 0.0 <= self.config.top_p <= 1.0:
            generation_config_params["top_p"] = self.config.top_p
        else:
            raise ValueError("`top_p` must be > 0.0 and < 1.0")

        generation_config = genai.types.GenerationConfig(**generation_config_params)

        response = model.generate_content(
            prompt,
            generation_config=generation_config,
            stream=self.config.stream,
        )
        if self.config.stream:
            # TODO: Implement streaming
            response.resolve()
            return response.text
        else:
            return response.text
