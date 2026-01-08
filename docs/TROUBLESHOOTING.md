# Jasper Troubleshooting Guide

## Common Issues & Solutions

### Setup & Installation

#### "OPENROUTER_API_KEY not set"

**Error**: 
```
🔴 Setup required

OPENROUTER_API_KEY not set
```

**Solution**:
1. Get a free API key: https://openrouter.ai/keys
2. Create `.env` file in your working directory:
   ```bash
   cat > .env << EOF
   OPENROUTER_API_KEY=sk_...
   EOF
   ```
3. Run Jasper again

#### "ModuleNotFoundError: No module named 'jasper'"

**Cause**: Jasper not installed

**Solution**:
```bash
# Install from PyPI
pip install jasper

# Or install in editable mode from source
cd jasper
pip install -e .
```

#### "pip install fails with dependency conflict"

**Cause**: Version conflict with existing packages

**Solution**:
```bash
# Create fresh virtual environment
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate
pip install jasper
```

### Execution Issues

#### "All providers failed to fetch income statement for AAPL"

**Cause**: Invalid ticker symbol or API rate-limited

**Solution**:
1. Verify ticker is correct (e.g., AAPL for Apple, MSFT for Microsoft)
2. For Indian stocks, use format: RELIANCE.NS, INFY.NS
3. If rate-limited, wait a few minutes and try again
4. Set `ALPHA_VANTAGE_API_KEY` to use premium API:
   ```bash
   # In .env
   ALPHA_VANTAGE_API_KEY=your_key_here
   ```

#### "Empty response from provider"

**Cause**: Provider returned no data for that ticker

**Solution**:
1. Verify ticker exists: search https://finance.yahoo.com
2. Try a different ticker
3. Some stocks may not have historical income statements available

#### "Validation failed: Incomplete task"

**Cause**: Task execution failed, data was not fetched

**Solution**:
1. Check the ticker symbol is valid
2. Check your internet connection
3. Try again (temporary provider outage)
4. Run with `--debug` to see detailed error:
   ```bash
   jasper "query" --debug
   ```

### Answer & Synthesis

#### "Validation failed: ... too low to synthesize"

**Cause**: Confidence score below threshold, validation blocked synthesis

**What this means**:
- Jasper found issues with the data or execution
- The answer cannot be generated with confidence
- Rather than guess, Jasper stops and reports the issue

**Solution**:
1. Check the reported validation issues
2. Verify ticker symbols are correct
3. Try a simpler query:
   ```bash
   jasper "What is Apple's revenue?"  # Better: explicit company
   # vs
   jasper "Compare tech stocks"       # Too vague
   ```

#### "Answer synthesis failed"

**Cause**: LLM service error while generating answer

**Solution**:
1. Check your OpenRouter API key in `.env`
2. Verify you have quota remaining: https://openrouter.ai
3. Try again (temporary service issue)
4. Run with `--debug`:
   ```bash
   jasper "query" --debug
   ```

### LLM & API Issues

#### "LLM Authentication Error"

**Error**:
```
⚠ LLM Authentication Error
Your OPENROUTER_API_KEY may be invalid or expired.
```

**Solution**:
1. Verify your API key in `.env`:
   ```bash
   cat .env | grep OPENROUTER_API_KEY
   ```
2. Get a fresh key: https://openrouter.ai/keys
3. Update `.env` with correct key
4. Make sure there are no extra spaces or quotes:
   ```bash
   # Correct
   OPENROUTER_API_KEY=sk_abc123

   # Wrong (has quotes)
   OPENROUTER_API_KEY="sk_abc123"
   ```

#### "LLM Service Error (code 524)"

**Error**:
```
⚠ LLM Service Error
The AI model (OpenRouter) is temporarily unavailable or rate-limited.
```

**Solution**:
1. Wait 30 seconds and try again
2. Check OpenRouter status: https://status.openrouter.io
3. Check your quota: https://openrouter.ai/usage
4. Consider using a different model:
   ```bash
   # In .env
   OPENROUTER_MODEL=meta-llama/llama-2-70b-chat:free
   ```

#### "LLM Timeout"

**Error**:
```
⚠ LLM Timeout
The request to the AI model took too long.
```

**Solution**:
1. Try a simpler query
2. Wait and retry
3. Check your internet connection

### Data Quality Issues

#### "Data Quality is low"

**Confidence breakdown shows low data_quality**:
```
Data Quality: 0.33 (too low)
```

**Causes**:
- Provider returned partial data (less than 3 years)
- Some fields are missing from response
- Data format is unexpected

**Solution**:
1. Try a different ticker
2. Try different time periods:
   ```bash
   jasper "Apple's 2023 revenue"  # Specific year
   ```
3. Check provider data: https://www.yfinance.com or https://www.alphavantage.co

### Debug Mode

For detailed technical information, use `--debug` flag:

```bash
jasper "query" --debug
```

This will:
1. Show full Python stack traces
2. Print all logging events
3. Reveal provider error details

**Example**:
```bash
$ jasper "Apple revenue" --debug
[Full traceback if error occurs]
```

### Getting Help

**Before asking for help, collect**:
1. Your command: `jasper "query"`
2. The full error message
3. Your `.env` file (WITHOUT the actual API keys):
   ```bash
   grep -v "=sk_\|=your_" .env
   ```
4. Output with `--debug`:
   ```bash
   jasper "query" --debug > jasper_debug.log 2>&1
   cat jasper_debug.log
   ```

**Then report**:
- Issue: https://github.com/your-repo/jasper/issues
- Include: command, error message, environment

### Interactive Mode Issues

#### REPL mode not responding

**Solution**:
```bash
# Press Ctrl+C to exit
jasper
# (Prompt frozen)
^C  # Ctrl+C
# (Back to shell)
```

#### Previous context not working in REPL

**What's happening**: Jasper keeps history across queries in the same session.

**If history seems wrong**:
- Exit and restart REPL: `exit` then `jasper`
- Each restart clears history

### Performance

#### Jasper is slow (10-15s per query)

**This is normal**. Jasper takes time because:
1. **Planning** (~2s): LLM breaks down query
2. **Execution** (~5-8s): Fetch data from providers, validate
3. **Validation** (<1s): Check data quality
4. **Synthesis** (~2-3s): LLM generates answer

**To improve**:
1. Use paid OpenRouter plan for faster LLM access
2. Set `ALPHA_VANTAGE_API_KEY` for faster financial data
3. Use simpler, more specific queries

### Feature Requests

v0.1.0 limitations:
- Income statement only (balance sheet coming later)
- Single-turn queries (multi-turn planning in v0.2.0)
- CLI only (web UI in future)

See [docs/ROADMAP.md](../ROADMAP.md) for planned features.

## Still Stuck?

1. **Check the logs**: Run with `--debug` to see detailed error
2. **Read the docs**: [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)
3. **Try the examples**: See [README.md](../README.md#examples)
4. **Open an issue**: Include debug output and your setup

---

**Questions?** File an issue: https://github.com/your-repo/jasper/issues
