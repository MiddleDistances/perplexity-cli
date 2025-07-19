# Perplexity CLI (Improved)

A command-line interface for Perplexity AI with improved error handling, Python 3.8+ compatibility, and automatic API key management.

## Features

- ✅ Python 3.8+ compatibility (no more union type errors)
- ✅ Automatic API key prompting and secure storage
- ✅ Better error handling and recovery
- ✅ Automatic dependency installation
- ✅ Cross-platform shebang (`#!/usr/bin/env python3`)
- ✅ Easy pip installation

## Installation

### From PyPI (once published)
```bash
pip install perplexity-cli
```

### From source
```bash
# Clone the repository
git clone https://github.com/dawid-szewc/perplexity-cli.git
cd perplexity-cli

# Install in development mode
pip install -e .

# Or build and install the wheel
python -m build
pip install dist/perplexity_cli-*.whl
```

## Usage

### First time setup
The CLI will automatically prompt for your API key on first use:

```bash
perplexity "What is the meaning of life?"
# You'll be prompted to enter your API key and optionally save it
```

### Basic usage
```bash
# Ask a question
perplexity "Explain quantum computing in simple terms"

# Use a specific model
perplexity -m sonar-pro "What are the latest AI developments?"

# Show token usage
perplexity -u "How does photosynthesis work?"

# Show citations
perplexity -c "What are the health benefits of meditation?"
```

### Available options
```
perplexity [-h] [-v] [-u] [-c] [-g] [-a API_KEY] [-m MODEL] [--clear-config] query

positional arguments:
  query                 The query to process

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Enable debug mode
  -u, --usage           Show token usage
  -c, --citations       Show citations
  -g, --glow            Use glow formatting
  -a API_KEY, --api-key API_KEY
                        Perplexity API key (overrides saved/env key)
  -m MODEL, --model MODEL
                        Model to use (default: sonar-pro)
                        Available: sonar-reasoning-pro, sonar-reasoning, sonar-pro, sonar
  --clear-config        Clear saved configuration
```

## API Key Management

The CLI looks for your API key in the following order:
1. Command line argument (`-a` or `--api-key`)
2. Environment variable (`PERPLEXITY_API_KEY`)
3. Saved configuration file (`~/.config/perplexity-cli/config.json`)
4. Interactive prompt (with option to save)

### Setting via environment variable
```bash
export PERPLEXITY_API_KEY="your-api-key-here"
```

### Clearing saved configuration
```bash
perplexity --clear-config
```

## Development

### Building the wheel
```bash
# Install build dependencies
pip install -r requirements-dev.txt

# Build the wheel
python -m build

# The wheel will be in the dist/ directory
ls dist/
```

### Installing for development
```bash
pip install -e .
```

## Improvements over original

1. **Python compatibility**: Works with Python 3.8+ (removed Python 3.10+ union syntax)
2. **API key management**: Automatic prompting and secure storage
3. **Error recovery**: Better handling of missing dependencies and API errors
4. **Installation**: Proper pip packaging with entry points
5. **Cross-platform**: Uses `#!/usr/bin/env python3` for better compatibility

## License

MIT License (same as original)