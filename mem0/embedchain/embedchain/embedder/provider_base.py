import os
from typing import Optional

from embedchain.config.embedder.base import BaseEmbedderConfig
from embedchain.embedder.base import BaseEmbedder


class ApiKeyEmbedderBase(BaseEmbedder):
    """Common embedder superclass that handles API-key retrieval and validation.

    Children must set ``env_var_name`` to the environment variable expected by
    the provider. Subclasses can access the resolved key via ``self.api_key``
    inside ``_post_init_setup`` where they should create the embedding
    function and call ``self.set_embedding_fn`` / ``self.set_vector_dimension``.
    """

    env_var_name: str = ""

    def __init__(self, config: Optional[BaseEmbedderConfig] = None):
        super().__init__(config=config)
        if not self.env_var_name:
            raise ValueError("Subclasses of ApiKeyEmbedderBase must define env_var_name class attribute")

        self.api_key = self.config.api_key or os.getenv(self.env_var_name)
        if not self.api_key:
            raise ValueError(
                f"Please set the {self.env_var_name} environment variable or provide `api_key` in the config."
            )

        # Allow provider-specific additional configuration
        self._post_init_setup()

    # ------------------------------------------------------------------
    # Hook
    # ------------------------------------------------------------------

    def _post_init_setup(self):  # noqa: D401
        """Provider-specific initialisation. Must be implemented by subclass."""
        raise NotImplementedError