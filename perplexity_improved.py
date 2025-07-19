#!/usr/bin/env python3
"""
Improved Perplexity CLI with Python 3.8+ compatibility and API key management
"""
import logging
import argparse
import os
import sys
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict, Any

try:
    import requests
except ImportError:
    print("Error: 'requests' module not found. Installing required dependencies...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

AVAILABLE_MODELS = [
    "sonar-reasoning-pro",
    "sonar-reasoning",
    "sonar-pro",
    "sonar"
]

logger = logging.getLogger(__name__)

# Default config directory
CONFIG_DIR = Path.home() / ".config" / "perplexity-cli"
CONFIG_FILE = CONFIG_DIR / "config.json"


class ApiKeyNotFoundException(Exception):
    pass


class InvalidSelectedModelException(Exception):
    pass


def display(
    message: str,
    color: str = "white",
    bold: bool = False,
    bg_color: str = "black",
):
    colors = {
        "red": "91m",
        "green": "92m",
        "yellow": "93m",
        "blue": "94m",
        "white": "97m",
    }
    bg_colors = {
        "black": "40",
        "red": "41",
        "green": "42",
        "yellow": "43",
        "blue": "44",
        "white": "47",
    }
    if bold:
        print(f"\033[1;{bg_colors[bg_color]};{colors[color]} {message}\033[0m")
    else:
        print(f"\033[{bg_colors[bg_color]};{colors[color]} {message}\033[0m")


@dataclass
class ApiConfig:
    api_url: str = "https://api.perplexity.ai/chat/completions"
    api_key: Optional[str] = None
    usage: bool = False
    citations: bool = False
    model: Optional[str] = None


class ConfigManager:
    """Manages saving and loading configuration including API keys"""
    
    @staticmethod
    def load_config() -> Dict[str, Any]:
        """Load configuration from file"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading config: {e}")
        return {}
    
    @staticmethod
    def save_config(config: Dict[str, Any]) -> None:
        """Save configuration to file"""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=2)
            # Set restrictive permissions on config file
            CONFIG_FILE.chmod(0o600)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    @staticmethod
    def get_api_key() -> Optional[str]:
        """Get API key from environment or config file"""
        # First check environment variable
        api_key = os.environ.get("PERPLEXITY_API_KEY")
        if api_key:
            return api_key
        
        # Then check config file
        config = ConfigManager.load_config()
        return config.get("api_key")
    
    @staticmethod
    def save_api_key(api_key: str) -> None:
        """Save API key to config file"""
        config = ConfigManager.load_config()
        config["api_key"] = api_key
        ConfigManager.save_config(config)
    
    @staticmethod
    def prompt_for_api_key() -> str:
        """Prompt user for API key"""
        display("No API key found. Please enter your Perplexity API key:", "yellow")
        display("You can get one from: https://docs.perplexity.ai", "blue")
        
        api_key = input("API Key: ").strip()
        
        if not api_key:
            display("API key cannot be empty!", "red")
            sys.exit(1)
        
        # Ask if user wants to save it
        save_choice = input("\nSave this API key for future use? (y/n): ").strip().lower()
        if save_choice == 'y':
            ConfigManager.save_api_key(api_key)
            display("API key saved successfully!", "green")
        
        return api_key


class ModelValidator:
    @staticmethod
    def validate(model: str) -> bool:
        return model in AVAILABLE_MODELS

    @staticmethod
    def get_available_models() -> List[str]:
        return AVAILABLE_MODELS


class Perplexity:
    def __init__(self, args) -> None:
        self.config = ApiConfig()
        
        if not ModelValidator.validate(args.model):
            raise InvalidSelectedModelException(
                f"Invalid model: {args.model}\n"
                f"Available models: {ModelValidator.get_available_models()}"
            )
        
        self.config.model = args.model
        self.config.usage = args.usage
        self.config.citations = args.citations
        self.use_glow = args.glow
        
        # Handle API key
        if args.api_key:
            self.config.api_key = args.api_key
        else:
            api_key = ConfigManager.get_api_key()
            if api_key is None:
                # Prompt for API key
                api_key = ConfigManager.prompt_for_api_key()
            self.config.api_key = api_key

    def get_response(self, message: str) -> None:
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}",
        }
        logger.debug(f"Headers: {headers}")
        
        query_data = {
            "model": self.config.model,
            "messages": [
                {"role": "system", "content": "Be precise and concise."},
                {"role": "user", "content": message},
            ],
        }
        logger.debug(f"Query data: {query_data}")

        try:
            response = requests.post(
                self.config.api_url, headers=headers, data=json.dumps(query_data)
            )
        except requests.exceptions.RequestException as e:
            display(f"Network error: {str(e)}", "red")
            sys.exit(1)

        if response.status_code == 200:
            result = response.json()
            
            # Handle citations if requested and present
            if self.config.citations and "citations" in result:
                self._show_citations(result["citations"], self.use_glow)
            
            # Handle usage if requested and present
            if self.config.usage and "usage" in result:
                self._show_usage(result["usage"], self.use_glow)
            
            # Show content
            if "choices" in result and result["choices"]:
                content = result["choices"][0]["message"]["content"]
                self._show_content(content)
            else:
                display("No response content received", "yellow")
                
        elif response.status_code == 401:
            display("Invalid API key! Please check your API key.", "red")
            # Ask if user wants to enter a new key
            retry = input("\nWould you like to enter a new API key? (y/n): ").strip().lower()
            if retry == 'y':
                new_key = ConfigManager.prompt_for_api_key()
                self.config.api_key = new_key
                # Retry the request
                self.get_response(message)
            else:
                sys.exit(1)
        else:
            display(f"Error {response.status_code}: {response.text}", "red")
            sys.exit(1)

    @staticmethod
    def _show_usage(result: Dict[str, Any], use_glow: bool) -> None:
        if use_glow:
            print("# Tokens")
        else:
            display("Tokens", "yellow", True, "blue")
        for token, value in result.items():
            print(f"- {token}: {value}")
        print()

    @staticmethod
    def _show_citations(result: List[str], use_glow: bool) -> None:
        if use_glow:
            print("# Citations")
        else:
            display("Citations", "yellow", True, "blue")
        for element in result:
            print(f"- {element}")
        print()

    def _show_content(self, result: str) -> None:
        if self.use_glow:
            print("# Content")
        else:
            display("Content", "yellow", True, "blue")
        print(result)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Perplexity CLI - Query Perplexity AI from your terminal"
    )
    parser.add_argument("query", type=str, nargs='?', help="The query to process")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug mode")
    parser.add_argument("-u", "--usage", action="store_true", help="Show token usage")
    parser.add_argument("-c", "--citations", action="store_true", help="Show citations")
    parser.add_argument("-g", "--glow", action="store_true", help="Use glow formatting")
    parser.add_argument(
        "-a",
        "--api-key",
        type=str,
        help="Perplexity API key (overrides saved/env key)",
        required=False,
    )
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        help=f"Model to use (default: sonar-pro). Available: {', '.join(AVAILABLE_MODELS)}",
        required=False,
        default="sonar-pro",
    )
    parser.add_argument(
        "--clear-config",
        action="store_true",
        help="Clear saved configuration"
    )
    
    args = parser.parse_args()
    
    # Handle config clearing
    if args.clear_config:
        if CONFIG_FILE.exists():
            CONFIG_FILE.unlink()
            display("Configuration cleared!", "green")
        else:
            display("No configuration to clear", "yellow")
        sys.exit(0)
    
    # Require query if not clearing config
    if not args.query:
        parser.error("Query is required unless using --clear-config")
    
    log_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger.debug(f"args: {args}")
    
    try:
        perplexity = Perplexity(args)
        perplexity.get_response(args.query)
    except KeyboardInterrupt:
        display("\nOperation cancelled by user", "yellow")
        sys.exit(0)
    except Exception as e:
        logger.debug(f"An error occurred: {str(e)}")
        display(f"Error: {str(e)}", "red")
        sys.exit(1)


if __name__ == "__main__":
    main()