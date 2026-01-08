# Jasper Architecture

## Overview

Jasper is a CLI-first autonomous financial research agent with explicit stages:

```
Planning → Execution → Validation → Synthesis
```

Each stage is independent and composable. The system is designed around these non-negotiable principles:

- **Validation blocks synthesis** — if validation fails, no answer is generated
- **Tool-grounded data only** — no hallucinated facts; all answers based on fetched data
- **Deterministic LLM usage** — temperature=0 for reproducible planning and entity extraction
- **Confidence is explicit** — every answer includes a confidence breakdown

## Core Components

### 1. Controller (`jasper/core/controller.py`)

The orchestrator that drives the full pipeline:

1. **Planning Phase**: Break user query into ordered research tasks
2. **Execution Phase**: Run tasks against financial data providers
3. **Validation Phase**: Check data completeness, quality, and consistency
4. **Synthesis Phase**: Generate final answer with confidence metrics

Key invariant: Synthesis only runs if validation passes.

### 2. State Management (`jasper/core/state.py`)

All data flows through `Jasperstate`:

```python
Jasperstate(
    query: str,                    # Original user question
    plan: List[Task],              # Ordered tasks to execute
    task_results: Dict[str, Any],  # Results from each task
    validation: validationresult,  # Validation result with confidence
    final_answer: str,             # Synthesized answer (if valid)
    error: str,                    # Error message if failed
    status: str,                   # "Planning" | "Executing" | "Validating" | "Synthesizing" | "Completed" | "Failed"
)
```

### 3. Planner (`jasper/agent/planner.py`)

Converts user questions into explicit research tasks.

**Input**: User query  
**Output**: List of `Task` objects with:
- Description: what data is needed
- Tool name: which tool to use (e.g., "income_statement")
- Tool args: parameters (e.g., ticker="AAPL")

**Constraints**:
- Uses LLM with temperature=0 (deterministic)
- Only creates tasks for available tools
- Extracts entities (companies, tickers) explicitly

### 4. Entity Extractor (`jasper/agent/entity_extractor.py`)

Identifies financial entities from user queries.

**Input**: User query  
**Output**: List of `Entity` objects (company names, tickers, indices)

**Constraints**:
- Uses LLM with temperature=0 (required for determinism)
- Returns `Entity` with name, type, and optional ticker
- Logs failures gracefully

### 5. Executor (`jasper/agent/executor.py`)

Runs tasks against financial data providers.

**For each task**:
1. Extract ticker from task args
2. Try provider 1, if empty/error, try provider 2, etc.
3. Validate data structure before storing
4. Retry up to max_retries on provider errors
5. Mark task complete or failed

**Constraints**:
- **Rejects empty responses** — None, empty list, or empty dict is a failure
- **No hallucination** — data must come from providers
- Validates financial data has required fields

### 6. Validator (`jasper/agent/validator.py`)

Checks that execution is sound before synthesis.

**Validation rules**:
1. All tasks completed (no pending or failed tasks)
2. No task has an error
3. All completed tasks have data in task_results
4. No task result is empty
5. (Future) Financial domain checks (ratios, anomalies)

**If validation fails**:
- Set `confidence = 0.0`
- Do NOT proceed to synthesis
- Return list of issues

**Confidence Breakdown**:
- `data_coverage`: % of required data fetched
- `data_quality`: provider reliability and data freshness
- `inference_strength`: how much reasoning was needed
- `overall`: weighted average (used to block low-confidence answers)

### 7. Synthesizer (`jasper/agent/synthesizer.py`)

Generates final answer from validated data.

**Input**:
- User query
- Task results (validated)
- Validation result with confidence

**Process**:
- Only runs if validation passed
- Uses LLM to summarize findings
- Returns natural language answer

**Constraints**:
- Uses only data from task_results
- Does not add external information
- Temperature=0 for reproducibility

### 8. Error Handling (`jasper/core/errors.py`)

Structured error types for user-friendly messages:

```python
JasperError (base)
├── ConfigError          # Missing API keys, setup issues
├── LLMError            # LLM service unavailable
├── DataProviderError   # Financial data provider failed
├── ValidationError     # Validation checks failed
└── QueryError          # User query unparseable
```

Each error includes:
- `message`: user-friendly description
- `suggestion`: actionable next step
- `debug_details`: technical info (shown with --debug flag)

## Data Flow

```
User Query
    ↓
[Planning] → extract entities → create tasks
    ↓
[Execution] → task.tool → provider.fetch_data → validate → store
    ↓
[Validation] → check completeness, quality → is_valid, confidence
    ↓
Is Valid? ────NO──→ Return error, confidence=0.0
    ↓ YES
[Synthesis] → summarize results → final answer
    ↓
Return answer + confidence breakdown
```

## Tool Integration

Tools are data providers:

```
FinancialDataRouter (abstraction layer)
    ├── AlphaVantageClient
    │   └── fetch: income_statement(ticker)
    └── YFinanceClient
        └── fetch: income_statement(ticker)
```

**How it works**:
1. Router tries provider 1
2. If provider 1 returns empty/error, try provider 2
3. First non-empty result wins
4. If all fail, raise DataProviderError

**Adding new tools**:
1. Implement provider with async methods
2. Register in FinancialDataRouter
3. Update Planner to support new AVAILABLE_TOOLS
4. Add test cases

## LLM Dependency

All LLM calls go through `get_llm()` factory with `temperature=0`:

```python
from jasper.core.llm import get_llm

llm = get_llm(temperature=0)  # Enforces determinism
response = await llm.agenerate([prompt])
```

**Why temperature=0?**
- Reproducible planning (same query → same plan)
- Reproducible entity extraction (same query → same entities)
- Safe synthesis (no random hallucinations)

**LLM service** (configurable):
- Default: OpenRouter (https://openrouter.ai)
- Model: xiaomi/mimo-v2-flash:free (cost-effective)
- Can override: OPENROUTER_MODEL env var

## CLI Interface

Entry point: `jasper/cli/main.py`

**Commands**:
- `jasper "query"` — single query, exit
- `jasper` — interactive REPL mode
- `jasper --help` — show help
- `jasper --debug` — show stack traces

**Error Handling**:
1. Preflight check for required API keys
2. If missing, show setup instructions (NO traceback)
3. If --debug flag, show full traceback
4. All JasperError exceptions have user-friendly messages

## Testing Strategy

Minimal test suite at `tests/test_v0_1_0.py`:

1. **Config Tests**: Missing API keys → friendly error
2. **Validation Tests**: Empty data, failed tasks → validation fails, confidence=0.0
3. **Provider Tests**: Empty responses → rejected
4. **CLI Tests**: --help works, missing config → friendly error

Run:
```bash
pytest tests/ -v
```

## Future Extensions

**Not in v0.1.0, but designed for**:

- **More tools**: balance sheet, cash flow, stock prices, macro indicators
- **Domain validation**: negative revenue flags, ratio checks, anomaly detection
- **Multi-turn**: session memory, refinement queries
- **Pluggable LLMs**: Ollama, Anthropic Claude, Google Gemini
- **Report export**: PDF, markdown, JSON
- **Web API**: read-only HTTP interface
- **Caching**: 1-hour TTL on repeated queries
- **Observability**: structured logging, OpenTelemetry traces

**Not designed for**:
- Database persistence (stateless CLI)
- Multi-user authentication (single-user tool)
- Horizontal scaling (single-process CLI)
- Real-time streaming (batch queries)

## Configuration

See `.env.example` for all configurable options:

```bash
cp .env.example .env
# Edit .env with your API keys
```

**Required**:
- `OPENROUTER_API_KEY` — LLM access

**Optional**:
- `ALPHA_VANTAGE_API_KEY` — Financial data (defaults to demo)
- `OPENROUTER_MODEL` — LLM model (defaults to xiaomi/mimo-v2-flash:free)
- `ENV` — Environment (dev or prod)

## Performance Characteristics

- **Planning**: ~1-2s (single LLM call)
- **Execution**: ~3-5s per task (provider fetch + validation)
- **Validation**: <100ms (in-memory checks)
- **Synthesis**: ~2-3s (single LLM call)
- **Total**: ~10-15s for typical 2-task research

Limited by LLM API latency, not Jasper code.

## Known Limitations (v0.1.0)

1. **Income statement only** — balance sheet, cash flow coming later
2. **Simple validation** — no domain-specific financial checks yet
3. **No caching** — every query hits providers fresh
4. **US/IN stocks only** — yfinance + Alpha Vantage coverage
5. **No multi-turn memory** — each query is independent
6. **No export** — results to stdout only

These are deliberate constraints to keep v0.1.0 minimal and stable.
