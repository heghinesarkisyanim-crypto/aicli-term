# aicli

Natural language to Linux commands, powered by AI.
Type what you want in plain English or Armenian — aicli translates it to a shell command and runs it safely.

```
aicli run "show all files in this folder"
aicli run "ստеղgиr flask project called myapp"
aicli run "what does grep do"
aicli run --dry-run "delete old log files"
```

---

## Requirements

- Python 3.10 or higher
- `make` (optional but recommended)
- An API key from one of: **Groq**, Anthropic, OpenAI — or a local **Ollama** install

---

## Build

### Step 1 — Clone and enter the project

```bash
git clone https://github.com/yourorg/aicli
cd aicli
```

### Step 2 — Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows
```

### Step 3 — Install

```bash
# Production install
make install

# Development install (includes pytest + ruff linter)
make install-dev

# Without make:
pip install -e ".[dev]"
```

### Step 4 — Configure your API key

```bash
cp .env.example .env
```

Open `.env` and fill in your key:

```env
# Groq (fast, free tier available — recommended)
LLM_PROVIDER=groq
LLM_API_KEY=gsk_your_key_here
LLM_MODEL=llama-3.3-70b-versatile

# --- OR Anthropic ---
# ANTHROPIC_API_KEY=sk-ant-your_key_here

# --- OR OpenAI ---
# OPENAI_API_KEY=sk-your_key_here
```

Verify the install worked:

```bash
aicli --version
# aicli 0.1.0
```

---

## Run

### Basic usage

```bash
aicli run "show files in current directory"
aicli run "show disk usage"
aicli run "find all python files"
aicli run "how many lines are in main.py"
```

### Armenian input

```bash
aicli run "ֆaylery ycuyz tyr"
aicli run "inca e ls hramany"
```

### Preview without executing (dry-run)

```bash
aicli run --dry-run "delete all .pyc files"
# Shows: Dry-run: would execute: find . -name "*.pyc" -delete
```

### Ask what a command does (info)

```bash
aicli run "what does chmod do"
aicli run "explain the grep command"
```

### Scaffold a project

```bash
aicli run "create a flask project called myapp"
aicli run "create a python script project called myscript"
```

### Switch provider at runtime

```bash
aicli run --provider groq      "list processes"
aicli run --provider anthropic "list processes"
aicli run --provider openai    "list processes"
aicli run --provider ollama    "list processes"   # local, no internet
aicli run --provider mock      "list processes"   # offline demo, no key needed
```

### Other commands

```bash
aicli history           # show recent command history
aicli clear-history     # wipe history
aicli templates         # list available scaffold templates
aicli --help
aicli run --help
```

---

## Test

### Run all tests

```bash
make test

# Without make:
pytest tests/ -v
```

Expected output:

```
tests/test_executor.py::test_successful_command         PASSED
tests/test_executor.py::test_shell_injection_prevented  PASSED
tests/test_input_handler.py::test_armenian_detected     PASSED
tests/test_llm_engine.py::test_retries_on_bad_json      PASSED
tests/test_scaffolder.py::test_flask_basic_scaffold     PASSED
tests/test_scaffolder.py::test_rollback_on_failure      PASSED
tests/test_security_shield.py::test_rm_rf_root_blocked  PASSED
tests/test_security_shield.py::test_fork_bomb_blocked   PASSED
...
43 passed in ~6s
```

### Run tests with coverage

```bash
make test-cov
```

### Lint

```bash
make lint      # check
make format    # auto-fix
```

---

## Configuration

Edit `config/settings.yaml` to change defaults:

```yaml
llm:
  provider: "groq"                    # groq | anthropic | openai | ollama | mock
  model: "llama-3.3-70b-versatile"
  timeout: 15                         # seconds per API call
  max_retries: 3                      # retries on bad JSON / network errors

security:
  confirm_dangerous: true             # prompt before risky commands
  dry_run_default: false              # set true to always preview first

session:
  history_size: 100
  context_window: 5                   # past commands sent to LLM for context
  history_file: "~/.aicli/history.json"

ui:
  language: "en"                      # en | hy
  color_theme: "dark"                 # dark | light | no-color
```

Environment variables (`LLM_PROVIDER`, `LLM_MODEL`, `LLM_API_KEY`) override the YAML values.

---

## Providers

| Provider | Key env var | Recommended model |
|---|---|---|
| `groq` | `LLM_API_KEY` | `llama-3.3-70b-versatile` |
| `anthropic` | `ANTHROPIC_API_KEY` | `claude-haiku-4-5-20251001` |
| `openai` | `OPENAI_API_KEY` | `gpt-4o` |
| `ollama` | *(none)* | `llama3.2` — must run `ollama serve` first |
| `mock` | *(none)* | built-in — no key, no internet, for demos/testing |

---

## Scaffold Templates

```bash
aicli templates
```

| Template | What it creates |
|---|---|
| `flask-basic` | `app.py`, `templates/index.html`, `static/style.css`, `requirements.txt` |
| `flask-api` | `app.py`, `routes/`, `models.py`, `config.py` |
| `python-script` | `main.py`, `requirements.txt` |
| `venv-setup` | `setup.sh` — bootstraps a virtualenv |

---

## Security

aicli applies three layers of protection before any command runs:

1. **Keyword blocklist** — `rm -rf /`, fork bombs, disk formatters are hard-blocked, no bypass
2. **AI danger flag** — the LLM marks commands `is_dangerous: true`; user must type `y` to continue
3. **Critical path check** — commands touching `/etc`, `/boot`, `/sys`, `/proc`, `/dev` require confirmation

All commands run with `shell=False` + `shlex.split()` — shell injection is structurally impossible.

---

## Project Structure

```
aicli/
├── aicli/
│   ├── main.py                  # CLI entry point (typer)
│   ├── interfaces.py            # Shared dataclasses
│   ├── config.py                # YAML + .env loader
│   ├── core/
│   │   ├── pipeline.py          # Full request orchestration
│   │   ├── controller.py        # Intent routing
│   │   ├── executor.py          # subprocess.run (shell=False)
│   │   ├── input_handler.py     # Clean input + detect language
│   │   └── session.py           # History + context window
│   ├── llm/
│   │   ├── engine.py            # Retry logic + JSON extraction
│   │   ├── prompts.py           # System prompt + few-shot examples
│   │   ├── schema.py            # Pydantic response validation
│   │   └── providers/
│   │       ├── groq.py
│   │       ├── anthropic.py
│   │       ├── openai.py
│   │       ├── ollama.py
│   │       └── mock.py          # Offline provider for testing
│   ├── automation/
│   │   ├── scaffolder.py        # Template renderer + rollback
│   │   ├── registry.py          # Template name → path mapping
│   │   └── templates/           # Jinja2 templates
│   ├── security/
│   │   ├── shield.py            # 3-layer validation
│   │   └── patterns.py          # Blocked patterns + critical paths
│   └── ui/
│       ├── display.py           # Rich terminal output
│       ├── prompts.py           # Confirmation dialogs
│       └── themes.py            # dark / light / no-color
├── tests/                       # 43 unit tests
├── config/
│   └── settings.yaml
├── .env.example
├── pyproject.toml
└── Makefile
```

---

## Makefile reference

| Command | What it does |
|---|---|
| `make install` | Install aicli (production) |
| `make install-dev` | Install with pytest + ruff |
| `make run CMD="..."` | Run aicli with a command |
| `make test` | Run all 43 tests |
| `make test-cov` | Tests + coverage report |
| `make lint` | Check code style |
| `make format` | Auto-format code |
| `make clean` | Remove build artifacts |
