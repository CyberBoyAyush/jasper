"""
Minimal smoke tests for Jasper v0.1.0.

Test Coverage:
1. CLI smoke test (--help works)
2. Config missing test (friendly error, no traceback)
3. Validation failure test (empty data blocks synthesis)
"""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from jasper.core.errors import ConfigError, DataProviderError, ValidationError
from jasper.core.state import Task, Jasperstate, validationresult, ConfidenceBreakdown
from jasper.agent.validator import validator


class TestConfigErrors:
    """Test that missing config produces friendly errors, not stack traces."""
    
    def test_missing_llm_api_key(self):
        """Test that missing OPENROUTER_API_KEY raises ConfigError with helpful message."""
        from jasper.core.config import get_llm_api_key
        
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ConfigError) as exc_info:
                get_llm_api_key()
            
            # Verify error has user-friendly attributes
            assert "OPENROUTER_API_KEY" in str(exc_info.value.message)
            assert exc_info.value.suggestion is not None
            # Should NOT be a raw KeyError or ValueError
            assert isinstance(exc_info.value, ConfigError)


class TestValidationBlocking:
    """Test that validation failures block synthesis."""
    
    def test_validation_rejects_incomplete_tasks(self):
        """Test that incomplete tasks fail validation."""
        val = validator()
        
        state = Jasperstate(query="test")
        task = Task(id="task1", description="Fetch data", status="pending")
        state.plan = [task]
        
        result = val.validate(state)
        
        assert result is not None
        assert not result.is_valid
        assert result.confidence == 0.0
        assert result.breakdown is not None
        assert result.breakdown.overall == 0.0
        assert any("Incomplete task" in issue for issue in result.issues)
    
    def test_validation_rejects_empty_data(self):
        """Test that empty provider responses fail validation."""
        val = validator()
        
        state = Jasperstate(query="test")
        task = Task(id="task1", description="Fetch data", status="completed")
        state.plan = [task]
        state.task_results["task1"] = {}  # Empty result dict
        
        result = val.validate(state)
        
        assert result is not None
        assert not result.is_valid
        assert result.confidence == 0.0
        assert any("empty" in issue.lower() for issue in result.issues)
    
    def test_validation_rejects_task_errors(self):
        """Test that tasks with errors fail validation."""
        val = validator()
        
        state = Jasperstate(query="test")
        task = Task(id="task1", description="Fetch data", status="completed", error="Provider timeout")
        state.plan = [task]
        state.task_results["task1"] = {"fiscalDateEnding": "2023-12-31"}
        
        result = val.validate(state)
        
        assert result is not None
        assert not result.is_valid
        assert result.confidence == 0.0
        assert any("failed" in issue.lower() for issue in result.issues)
    
    def test_validation_passes_with_valid_data(self):
        """Test that valid data passes validation."""
        val = validator()
        
        state = Jasperstate(query="test")
        task = Task(id="task1", description="Fetch AAPL income statement", status="completed")
        state.plan = [task]
        state.task_results["task1"] = {
            "2023": {"fiscalDateEnding": "2023-12-31", "totalRevenue": "100000"},
            "2022": {"fiscalDateEnding": "2022-12-31", "totalRevenue": "95000"},
        }
        
        result = val.validate(state)
        
        assert result is not None
        assert result.is_valid
        assert result.confidence > 0.0
        assert result.breakdown is not None
        assert result.breakdown.overall > 0.0


class TestDataProviderErrors:
    """Test that empty/malformed provider responses are rejected."""
    
    @pytest.mark.asyncio
    async def test_empty_response_rejected(self):
        """Test that None response from provider is rejected."""
        from jasper.tools.financials import FinancialDataRouter
        
        mock_provider = MagicMock()
        mock_provider.income_statement = AsyncMock(return_value=None)
        mock_provider.__class__.__name__ = "MockProvider"
        
        router = FinancialDataRouter(providers=[mock_provider])
        
        with pytest.raises(DataProviderError) as exc_info:
            await router.fetch_income_statement("AAPL")
        
        assert "Empty" in exc_info.value.message or "failed" in exc_info.value.message.lower()
        assert exc_info.value.suggestion is not None
    
    @pytest.mark.asyncio
    async def test_empty_list_rejected(self):
        """Test that empty list from provider is rejected."""
        from jasper.tools.financials import FinancialDataRouter
        
        mock_provider = MagicMock()
        mock_provider.income_statement = AsyncMock(return_value=[])
        mock_provider.__class__.__name__ = "MockProvider"
        
        router = FinancialDataRouter(providers=[mock_provider])
        
        with pytest.raises(DataProviderError) as exc_info:
            await router.fetch_income_statement("AAPL")
        
        assert "failed" in exc_info.value.message.lower()


class TestCLI:
    """Test CLI smoke tests."""
    
    def test_help_flag(self):
        """Test that jasper --help works."""
        from typer.testing import CliRunner
        from jasper.cli.main import app
        
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        assert "Financial Research Agent" in result.stdout
    
    def test_missing_api_key_friendly_error(self):
        """Test that missing API key shows friendly message, not traceback."""
        from typer.testing import CliRunner
        from jasper.cli.main import app
        
        runner = CliRunner()
        
        # Clear API keys
        with patch.dict('os.environ', {}, clear=True):
            result = runner.invoke(app, ["test query"])
        
        # Should exit with error code
        assert result.exit_code == 1
        # Should contain friendly message
        assert "Setup Required" in result.stdout or "Setup" in result.stdout
        # Should NOT contain Python traceback
        assert "Traceback" not in result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
