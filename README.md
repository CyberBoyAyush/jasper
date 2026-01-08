# Jasper 🤖

# Jasper 🤖

**Jasper is a CLI-first autonomous financial research agent.** It breaks down complex financial questions into explicit research tasks, executes them with real data, validates results, and synthesizes answers with confidence metrics.

> **Status**: v0.1.0 Alpha. Stable architecture, core functionality complete. APIs may change before v1.0.

![Jasper banner](assets/screenshot.png)

## What is Jasper?

Jasper is for financial professionals who distrust black boxes. Instead of a chatbot that might hallucinate numbers, Jasper:

1. **Plans explicitly** — breaks your question into ordered research tasks
2. **Executes grounded** — fetches real data from providers (Alpha Vantage, yfinance)
3. **Validates strictly** — rejects answers if data is incomplete or quality is low
4. **Synthesizes transparently** — shows confidence breakdown alongside results

### Core Principles

- **Validation blocks synthesis** — no answer if data is insufficient
- **Tool-grounded data only** — every fact comes from a provider, no hallucinations
- **Deterministic LLM usage** — temperature=0 for reproducible planning
- **Explicit confidence** — every answer includes a detailed confidence breakdown

### What Jasper is NOT

- A stock picker (doesn't give buy/sell advice)
- A replacement for Bloomberg Terminal (doesn't have that much data)
- A multi-user SaaS (single-user CLI tool)
- A magical data oracle (limited to available providers)

## Quick Start

### Prerequisites

- **Python 3.9+**
- **OpenRouter API key** (free tier available: https://openrouter.ai/keys)

### Installation

```bash
# Install via pip
pip install jasper

# Or via uv (recommended)
uv pip install jasper
```

### Setup (First Run)

```bash
# 1. Get your API keys
#    - OpenRouter (LLM): https://openrouter.ai/keys (required)
#    - Alpha Vantage (data): https://www.alphavantage.co/api/ (optional)

# 2. Create .env file in your working directory
cat > .env << EOF
OPENROUTER_API_KEY=sk_...
EOF

# 3. Run Jasper
jasper "What is Apple's revenue?"
```

### Example Queries

```bash
# Simple, single-company analysis
jasper "What is Tesla's net income trend over the last 3 years?"

# Comparative analysis
jasper "Compare AAPL vs MSFT revenue growth"

# Specific time period
jasper "What was Amazon's operating expense in 2023?"

# Interactive mode (REPL)
jasper
# Prompts you for queries until you type 'exit'
```

### Output Example

```
JASPER: Researching... Planning → Executing → Validating → Synthesizing

[Task Board shows progress]

ANSWER:
Apple's revenue has grown from $365.8B (2021) to $394.3B (2023), 
a 7.8% increase over 2 years.

CONFIDENCE BREAKDOWN:
  Data Coverage: 1.00    (100% of required data fetched)
  Data Quality: 0.89     (89% from reliable providers)
  Inference Strength: 0.90 (straightforward metric)
  Overall Confidence: 0.93 (HIGH)
```

## How Jasper Works

```
User Query
    ↓
[PLANNING] — Break into research tasks
    ↓
[EXECUTION] — Fetch financial data from providers
    ↓
[VALIDATION] — Check data completeness & quality
    ├─ If INVALID → Return error, confidence=0.0, NO synthesis
    └─ If VALID → Continue
    ↓
[SYNTHESIS] — Generate answer with confidence metrics
    ↓
Final Answer
```

### The Four Stages

1. **Planning**: LLM breaks down query into explicit tasks (e.g., "Fetch AAPL income statement")
2. **Execution**: Execute tasks against financial data providers, retry on failure
3. **Validation**: Check that all data is present, non-empty, and structurally sound
4. **Synthesis**: Only if validation passes, generate natural language answer

**Key invariant**: Validation BLOCKS synthesis. If validation fails, Jasper returns the issues and confidence=0.0, rather than guessing.

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed system design, component breakdown, and extension points.

**High-level structure**:

```
jasper/
  cli/                    # User-facing command-line interface
  core/                   # State management, errors, LLM factory
  agent/                  # Planner, Executor, Validator, Synthesizer
  tools/                  # Financial data providers (Alpha Vantage, yfinance)
  observability/          # Session logging
```

## Supported Data

### Financial Metrics (v0.1.0)

Currently supported:
- ✅ **Income Statement** — Revenue, operating expense, net income
- ✅ **Tickers** — US stocks (AAPL, MSFT, etc.) and Indian stocks (RELIANCE.NS, etc.)

Coming in v0.2.0:
- 🔲 Balance Sheet (assets, liabilities, equity)
- 🔲 Cash Flow Statement
- 🔲 Stock Price & Volume
- 🔲 Key Metrics (PE ratio, market cap, etc.)

### Supported Markets

- 🇺🇸 **US Stocks** — via yfinance (free, no API key needed)
- 🇮🇳 **Indian Stocks** — via yfinance (format: RELIANCE.NS, INFY.NS, etc.)
- Other markets via Alpha Vantage (set `ALPHA_VANTAGE_API_KEY`)

## Configuration

Create `.env` in your working directory. See `.env.example`:

```bash
# REQUIRED
OPENROUTER_API_KEY=sk_...

# OPTIONAL
ALPHA_VANTAGE_API_KEY=your_key        # Financial data (free tier available)
OPENROUTER_MODEL=xiaomi/mimo-v2-flash:free  # LLM model
ENV=dev                                # Environment (dev or prod)
```

**Getting API keys**:
- **OpenRouter** (LLM, required): https://openrouter.ai/keys (free tier)
- **Alpha Vantage** (financial data, optional): https://www.alphavantage.co/api/ (free tier)

## Command Line

```bash
# Single query
jasper "Your question here"

# Interactive mode (REPL)
jasper

# Show help
jasper --help

# Debug mode (show stack traces)
jasper "query" --debug
```

### CLI Flags

- `--debug` — Show Python stack traces and detailed error info (for troubleshooting)
- `--help` — Show usage and examples

## Validation & Confidence

Every answer includes a **confidence breakdown**:

```
Data Coverage: 0.95       (95% of required data fetched)
Data Quality: 0.88        (88% from reliable providers)
Inference Strength: 0.90  (high-confidence logic)
Overall Confidence: 0.91  (HIGH)
```

If validation fails, synthesis is **blocked**:

```
🔴 Validation failed: Incomplete task
  • Task "Fetch AAPL income" did not complete
  Confidence: 0.0 (too low to synthesize)
```

## Troubleshooting

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for common issues:

- "OPENROUTER_API_KEY not set" → Setup instructions
- "All providers failed" → Invalid ticker or rate-limited
- "Validation failed" → Data quality issues
- And more...

## Testing

Run the minimal test suite:

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

Tests cover:
- Config validation (friendly errors, no tracebacks)
- Validation blocking synthesis (empty data → confidence=0.0)
- CLI smoke tests (--help works, --debug shows traces)

## Performance

Typical query latency:
- **Planning** ~1-2s (LLM call)
- **Execution** ~3-5s per task (provider fetch)
- **Validation** <100ms
- **Synthesis** ~2-3s (LLM call)
- **Total** ~10-15s for 2-task research

Limited by LLM API latency, not Jasper code.

## Contributing

Jasper is open-source. Contributions welcome:

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make small, focused changes
4. Add tests if possible
5. Open a PR with a clear description

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design and extension points.

## Roadmap

**v0.1.0** (now)
- ✅ Core pipeline (Planning → Execution → Validation → Synthesis)
- ✅ Income statement support
- ✅ Validation blocks synthesis
- ✅ CLI with error handling

**v0.2.0** (next)
- 🔲 Balance sheet & cash flow statements
- 🔲 Domain-specific validation (ratio checks, anomaly detection)
- 🔲 Test suite ≥70% coverage
- 🔲 Multi-turn conversations

**v0.3.0+** (future)
- 🔲 Pluggable LLM backends (Ollama, Claude, Gemini)
- 🔲 Custom tool registration (user-provided providers)
- 🔲 Report export (PDF, markdown)
- 🔲 Caching (1-hour TTL)
- 🔲 Web API (read-only HTTP interface)

## License

MIT License. See [LICENSE](LICENSE) for details.

## Versioning

Jasper uses semantic versioning. Until v1.0.0:
- Minor version bump = breaking change (config, CLI, API)
- Patch version bump = bug fix or backward-compatible feature

After v1.0.0, strict semver applies.

## FAQ

**Q: Is Jasper free?**  
A: Yes, open-source MIT license. You only pay for API usage (OpenRouter LLM calls, Alpha Vantage if used).

**Q: Can I use Jasper for production trading?**  
A: Not recommended. Jasper is designed for research and analysis, not automated trading. Always verify with other sources before making financial decisions.

**Q: Why does it take 10-15 seconds per query?**  
A: Most time is in LLM calls (planning and synthesis). Jasper prioritizes accuracy over speed.

**Q: What if data is missing for a stock?**  
A: Jasper will validate fail and show which data is missing. Try a different ticker or check provider coverage.

**Q: Can I add my own data sources?**  
A: v0.2.0 will support pluggable providers. For now, see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

**Want to learn more?**
- [Architecture Guide](docs/ARCHITECTURE.md) — How Jasper works internally
- [Troubleshooting](docs/TROUBLESHOOTING.md) — Common issues and fixes
- [GitHub Issues](https://github.com/jasper-ai/jasper/issues) — Ask questions or report bugs

