import importlib
import os
from typing import Optional

from langchain_community.llms.replicate import Replicate

from embedchain.config import BaseLlmConfig
from embedchain.helpers.json_serializable import register_deserializable
from .provider_base import ApiKeyLlmBase


@register_deserializable
class Llama2Llm(ApiKeyLlmBase):
    def __init__(self, config: Optional[BaseLlmConfig] = None):
        try:
            importlib.import_module("replicate")
        except ModuleNotFoundError:
            raise ModuleNotFoundError(
                "The required dependencies for Llama2 are not installed."
                'Please install with `pip install --upgrade "embedchain[llama2]"`'
            ) from None

        # Set default config values specific to this llm
        if not config:
            config = BaseLlmConfig()
            # Add variables to this block that have a default value in the parent class
            config.max_tokens = 500
            config.temperature = 0.75
        # Add variables that are `none` by default to this block.
        if not config.model:
            config.model = (
                "a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5"
            )

        # Initialise ApiKeyLlmBase (handles api_key retrieval/validation)
        super().__init__(config=config)

    env_var_name = "REPLICATE_API_TOKEN"

    def _get_answer(self, prompt):
        # TODO: Move the model and other inputs into config
        if self.config.system_prompt:
            raise ValueError("Llama2 does not support `system_prompt`")
        llm = Replicate(
            model=self.config.model,
            replicate_api_token=self.api_key,
            input={
                "temperature": self.config.temperature,
                "max_length": self.config.max_tokens,
                "top_p": self.config.top_p,
            },
        )
        return llm.invoke(prompt)
