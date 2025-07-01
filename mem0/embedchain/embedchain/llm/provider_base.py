import os
from typing import Optional
from embedchain.config import BaseLlmConfig
from embedchain.llm.base import BaseLlm


class ApiKeyLlmBase(BaseLlm):
    """Common helper for provider-specific LLM classes that rely on a single API key.

    Subclasses **must** set the class attributes:
      • ``env_var_name`` – name of the environment variable where the provider
        expects the API key (e.g. ``"GOOGLE_API_KEY"``).

    Optionally, subclasses may override:
      • ``_post_init_setup()`` – provider-specific SDK initialisation
      • ``_get_answer()`` – actual completion logic (mandatory unless subclass
        overrides ``get_llm_model_answer`` entirely).
    """

    env_var_name: str = ""  # to be defined by subclass

    def __init__(self, config: Optional[BaseLlmConfig] = None):
        super().__init__(config)
        if not self.env_var_name:
            raise ValueError("Subclasses of ApiKeyLlmBase must define env_var_name class attribute")

        if not self.config.api_key and self.env_var_name not in os.environ:
            raise ValueError(
                f"Please set the {self.env_var_name} environment variable or pass it in the config."
            )
        self.api_key = self.config.api_key or os.getenv(self.env_var_name)
        self._post_init_setup()

    # ------------------------------------------------------------------
    # Hook methods for subclasses
    # ------------------------------------------------------------------

    def _post_init_setup(self):  # noqa: D401  (simple override placeholder)
        """Optional extra provider setup executed after API key validation."""

    # ------------------------------------------------------------------
    # Common public entrypoint
    # ------------------------------------------------------------------

    def get_llm_model_answer(self, prompt):  # noqa: D401
        if self.config.system_prompt:
            raise ValueError(f"{self.__class__.__name__} does not support `system_prompt`")
        return self._get_answer(prompt)

    # ------------------------------------------------------------------
    # Provider-specific completion implementation
    # ------------------------------------------------------------------

    def _get_answer(self, prompt):  # pragma: no cover – must be implemented
        raise NotImplementedError