from __future__ import annotations

import time
import tomllib

import boto3
import jinja2
import yaml
from cloudflare import Cloudflare
from markupsafe import Markup
from openai import Client
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings
from pydantic_settings.main import SettingsConfigDict

from app._enums import Models
from app._exceptions import ClientInitializationError, SystemPromptError, logger


class Settings(BaseSettings):
    """
    Configuration settings for the application, using Pydantic for validation.
    """

    name: str = Field(default="JSON-ld", alias="APP_NAME")
    service_start_time: float = Field(default_factory=time.time, exclude=True)
    model_names: list[Models] = [Models.GPT_4_1_MINI, Models.GPT_4_1_MINI]
    model_base_url: str | None = Field(
        default=None,
        alias="MODEL_BASE_URL",
        description="Base URL for the model API.",
    )
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    system_prompts: dict[str, str] = Field(
        default_factory=dict,
        description="A dictionary of available system prompt templates, keyed by name.",
    )
    resend_api_key: str | None = Field(
        default=None,
        alias="RESEND_API_KEY",
        description="API key for Resend service, used for sending emails.",
    )
    llm_client: Client | None = Field(
        default=None,
        description="The LLM client instance used for generating completions.",
    )
    bucket_service: str | None = Field(
        default="s3",
        alias="BUCKET_SERVICE",
        description="Service for storing files.",
    )
    r2_account_id: str | None = Field(
        default=None,
        alias="R2_ACCOUNT_ID",
        description="R2 bucket ID for storing files.",
    )
    r2_access_key_id: str | None = Field(
        default=None,
        alias="R2_ACCESS_KEY_ID",
        description="R2 access key for authentication.",
    )
    r2_secret_access_key: str | None = Field(
        default=None,
        alias="R2_SECRET_ACCESS_KEY",
        description="R2 secret key for authentication.",
    )
    r2_client: object | None = None
    version: str = Field(default="0.0.0")
    cloudflare_api_token: str | None = Field(default=None, alias="CLOUDFLARE_API_TOKEN")
    cloudflare_db_id: str | None = Field(default=None, alias="CLOUDFLARE_DB_ID")
    cloudflare_account_id: str | None = Field(
        default=None, alias="CLOUDFLARE_ACCOUNT_ID"
    )
    cloudflare_client: Cloudflare | None = None

    @model_validator(mode="before")
    @classmethod
    def initialize_version(cls, values: dict) -> dict:
        """
        Loads and injects the application version from pyproject.toml into the settings.

        This validator runs before other validation steps. It attempts to read the version from the [project] section of pyproject.toml and sets it in the values dictionary. If the file is missing, malformed, or the version key is absent, it logs a warning and defaults to "0.0.0".

        Args:
            values (dict): Dictionary of field values passed to the model.

        Returns:
            dict: The updated values dictionary with the version set.

        Edge Cases:
            - If pyproject.toml is missing, unreadable, or lacks a version, the version is set to "0.0.0".
            - All errors are logged for traceability.

        Integration:
            - Ensures that the application version is always available in the settings, supporting versioned APIs,
              logging, and monitoring.

        Example:
            ```
            settings = Settings()
            print(settings.version)  # e.g., "1.2.3"
            ```
        """
        try:
            with open("pyproject.toml", "rb") as f:
                pyproject = tomllib.load(f)
            values["version"] = pyproject["project"]["version"]

        except FileNotFoundError:
            logger.warning("pyproject.toml not found. Setting version to 0.0.0")
        except tomllib.TOMLDecodeError:
            logger.warning("Failed to decode pyproject.toml. Setting version to 0.0.0")
        except KeyError:
            logger.warning(
                "Version key not found in pyproject.toml. Setting version to 0.0.0"
            )
        except TypeError:
            logger.warning("Invalid type in pyproject.toml. Setting version to 0.0.0")
        except Exception:
            values["version"] = "0.0.0"

        return values

    @model_validator(mode="before")
    @classmethod
    def initialize_system_prompts(cls, values: dict) -> dict:
        """
        Loads and parses system prompt templates from a YAML file into the settings.

        This validator runs before other validation steps. It uses Jinja2 to locate and read 'system.yaml' from the app/prompts directory, parses it as YAML, and injects the resulting dictionary into the values under 'system_prompts'. If the file is missing or malformed, a SystemPromptError is raised.

        Args:
            values (dict): Dictionary of field values passed to the model.

        Returns:
            dict: The updated values dictionary with system prompts loaded.

        Raises:
            SystemPromptError: If the system prompt file cannot be found, read, or parsed.

        Edge Cases:
            - If the template filename is None or the YAML is invalid, a detailed error is logged and raised.
            - If 'system_prompts' is already present in values, it is not overwritten.

        Integration:
            - Ensures all system prompts are centrally loaded and available for runtime rendering.

        Example:
            ```
            settings = Settings()
            print(settings.system_prompts.keys())  # e.g., dict_keys(['default', 'admin'])
            ```
        """
        try:
            env = jinja2.Environment(
                loader=jinja2.FileSystemLoader("app/prompts"), autoescape=True
            )
            template = env.get_template("system.yaml")
            if template.filename is None:
                logger.error(
                    "Jinja2 template filename is None, cannot load system.yaml."
                )
                raise SystemPromptError(details="Jinja2 template filename is None.")

            with open(template.filename, encoding="utf-8") as f:
                yaml_content = f.read()

            prompts_data = yaml.safe_load(yaml_content)

            if "system_prompts" not in values:
                values["system_prompts"] = prompts_data

        except FileNotFoundError as exc:
            logger.error("system.yaml not found in app/prompts/")
            raise SystemPromptError(details="system.yaml not found.") from exc
        except yaml.YAMLError as e:
            logger.error(f"Error parsing system.yaml: {e}")
            raise SystemPromptError(details=f"Error parsing system.yaml: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error initializing system prompts: {e}")
            raise SystemPromptError(
                details=f"Unexpected error initializing system prompts: {str(e)}",
            ) from e

        return values

    def get_rendered_prompt(self, prompt_name: str, context: dict | None = None) -> str:
        """
        Retrieves and renders a named system prompt template with the provided context.

        Looks up the prompt template by name from the loaded system prompts, then uses Jinja2 to render it with the supplied context dictionary. If the prompt is not found or rendering fails, a SystemPromptError is raised with detailed context.

        Args:
            prompt_name (str): The name of the prompt template to retrieve and render.
            context (dict | None): Dictionary of values to inject into the prompt template (optional).

        Returns:
            str: The rendered system prompt string.

        Raises:
            SystemPromptError: If the prompt is not found or rendering fails.

        Edge Cases:
            - If the prompt_name is missing, a detailed error is logged and raised.
            - If the context contains HTML or special types, Markup is used for safe rendering.

        Integration:
            - Enables dynamic, context-aware prompt generation for LLM calls and system messages.

        Example:
            ```
            rendered = settings.get_rendered_prompt("default", {"user": "Alice"})
            print(rendered)
            ```
        """
        if prompt_name not in self.system_prompts:
            logger.error(
                f"System prompt '{prompt_name}' not found. Available: {list(self.system_prompts.keys())}"
            )
            raise SystemPromptError(details=f"Prompt '{prompt_name}' not found.")

        prompt_template_str = self.system_prompts[prompt_name]

        try:
            env = jinja2.Environment(loader=jinja2.BaseLoader(), autoescape=True)
            template = env.from_string(prompt_template_str)

            safe_context = dict(context or {})
            if "types" in safe_context:
                safe_context["types"] = Markup(safe_context["types"])
            return template.render(safe_context)
        except jinja2.exceptions.TemplateError as e:
            logger.error(f"Error rendering prompt template '{prompt_name}': {e}")
            raise SystemPromptError(
                details=f"Error rendering prompt template '{prompt_name}': {e}"
            ) from e
        except Exception as e:
            logger.error(
                f"Unexpected error while rendering prompt '{prompt_name}': {e}"
            )
            raise SystemPromptError(
                details=f"Unexpected error rendering prompt '{prompt_name}': {e}"
            ) from e

    @model_validator(mode="after")
    def initialize_llm_client(self) -> Settings:
        """
        Initializes the model client for the whole application.
        This method creates a Client instance for OpenAI or Gemini based on the provided API keys and base URL.

        Returns:
            ModelRegistry: The initialized model registry instance.

        Raises:
            SystemPromptError: If neither OpenAI nor Gemini API keys are provided.
        """
        if self.openai_api_key:
            self.llm_client = Client(
                api_key=self.openai_api_key,
            )
        else:
            raise ClientInitializationError(
                details="No OpenAI key provided. Cannot initialize LLM client."
            )

        return self

    @model_validator(mode="after")
    def initialize_cloudflare_client(self) -> Settings:
        """
        Initializes the Cloudflare client for database operations using provided credentials.

        This validator runs after model initialization. If all required Cloudflare credentials are present, it creates a Cloudflare client instance and stores it in the cloudflare_client attribute.

        Returns:
            Settings: The updated Settings instance with the Cloudflare client initialized (if credentials are present).

        Edge Cases:
            - If any credential is missing, the client is not initialized and cloudflare_client remains None.
            - The client is used for database operations in the application.

        Integration:
            - Enables interaction with Cloudflare's D1 database service.

        Example:
            ```
            settings = Settings()
            if settings.cloudflare_client:
                # Use the client for database operations
                pass
            ```
        """
        if self.cloudflare_api_token:
            self.cloudflare_client = Cloudflare(
                api_token=self.cloudflare_api_token,
            )
        return self

    @model_validator(mode="after")
    def initialize_r2_client(self) -> Settings:
        """
        Initializes the R2 client for AWS S3-compatible storage using provided credentials.

        This validator runs after model initialization. If all required R2 credentials are present, it creates a boto3 client for the specified bucket service and stores it in the r2_client attribute.

        Returns:
            Settings: The updated Settings instance with the R2 client initialized (if credentials are present).

        Edge Cases:
            - If any credential is missing, the client is not initialized and r2_client remains None.
            - The endpoint URL is constructed using the R2 account ID.

        Integration:
            - Enables file storage and retrieval via Cloudflare R2 or compatible S3 services.

        Example:
            ```
            settings = Settings()
            if settings.r2_client:
                # Use the client for file operations
                pass
            ```
        """
        if self.r2_account_id and self.r2_access_key_id and self.r2_secret_access_key:
            self.r2_client = boto3.client(
                service_name=self.bucket_service,
                endpoint_url=f"https://{self.r2_account_id}.r2.cloudflarestorage.com",
                aws_access_key_id=self.r2_access_key_id,
                aws_secret_access_key=self.r2_secret_access_key,
            )
        return self

    model_config = SettingsConfigDict(env_file=".env")


# Initialize the settings object globally
settings = Settings()
