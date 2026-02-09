"""
LLM Service
Provider-agnostic interface for LLM interactions.
"""
from typing import Optional, List
from abc import ABC, abstractmethod

from utils.prompts import SYSTEM_PROMPT, build_rag_prompt


class BaseLLMProvider(ABC):
    """Base class for LLM providers."""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str) -> str:
        """Generate a response from the LLM."""
        pass


class OllamaProvider(BaseLLMProvider):
    """Ollama provider for local LLMs."""

    def __init__(self, model: str = "qwen2.5:14b"):
        self.model = model

    def generate(self, prompt: str, system_prompt: str) -> str:
        try:
            import ollama

            response = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                options={"num_ctx": 131072}
            )
            return response["message"]["content"]

        except ImportError:
            raise RuntimeError("Ollama package not installed. Run: pip install ollama")
        except Exception as e:
            if "connection" in str(e).lower():
                raise RuntimeError(
                    "Could not connect to Ollama. Make sure Ollama is running. "
                    "Start it with: ollama serve"
                )
            raise RuntimeError(f"Ollama error: {str(e)}")


class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider."""

    def __init__(self, model: str = "gpt-4o", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key

    def generate(self, prompt: str, system_prompt: str) -> str:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content

        except ImportError:
            raise RuntimeError("OpenAI package not installed. Run: pip install openai")
        except Exception as e:
            if "api_key" in str(e).lower():
                raise RuntimeError("Invalid OpenAI API key. Check your settings.")
            raise RuntimeError(f"OpenAI error: {str(e)}")


class AnthropicProvider(BaseLLMProvider):
    """Anthropic provider for Claude models."""

    def __init__(self, model: str = "claude-sonnet-4-20250514", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key

    def generate(self, prompt: str, system_prompt: str) -> str:
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self.api_key)

            response = client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text

        except ImportError:
            raise RuntimeError("Anthropic package not installed. Run: pip install anthropic")
        except Exception as e:
            if "api_key" in str(e).lower():
                raise RuntimeError("Invalid Anthropic API key. Check your settings.")
            raise RuntimeError(f"Anthropic error: {str(e)}")


class LLMService:
    """
    Main LLM service that handles provider selection and RAG queries.
    """

    def __init__(
        self,
        provider: str = "ollama",
        model: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize LLM service.

        Args:
            provider: LLM provider ("ollama", "openai", "anthropic")
            model: Model name (provider-specific)
            api_key: API key for paid providers
        """
        self.provider_name = provider

        # Set default models
        default_models = {
            "ollama": "qwen2.5:14b",
            "openai": "gpt-4o",
            "anthropic": "claude-sonnet-4-20250514"
        }
        self.model = model or default_models.get(provider, "llama3.2")

        # Initialize provider
        if provider == "ollama":
            self.provider = OllamaProvider(model=self.model)
        elif provider == "openai":
            self.provider = OpenAIProvider(model=self.model, api_key=api_key)
        elif provider == "anthropic":
            self.provider = AnthropicProvider(model=self.model, api_key=api_key)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def query(self, question: str, context: str) -> str:
        """
        Query the LLM with RAG context.

        Args:
            question: User's question
            context: Retrieved context from documents

        Returns:
            LLM response grounded in the provided context
        """
        prompt = build_rag_prompt(question, context)
        return self.provider.generate(prompt, SYSTEM_PROMPT)

    def generate_with_system(self, prompt: str, system_prompt: str) -> str:
        """
        Generate a response with a custom system prompt.
        Used for chapter-level analysis where the strict RAG system prompt
        is not appropriate.

        Args:
            prompt: User prompt (e.g. chapter summary request with full chapter text)
            system_prompt: Custom system prompt for this analysis type

        Returns:
            LLM response
        """
        return self.provider.generate(prompt, system_prompt)

    def generate_raw(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate a raw response without RAG formatting.

        Args:
            prompt: User prompt
            system_prompt: Optional custom system prompt

        Returns:
            LLM response
        """
        return self.provider.generate(prompt, system_prompt or SYSTEM_PROMPT)
