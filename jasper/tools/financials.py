import httpx 
from typing import Optional, Dict, Any, List
from ..core.errors import DataProviderError

# --- Financial Data Router ---
# Aggregates multiple data providers to ensure reliability
class FinancialDataRouter:
    def __init__(self, providers: List[Any]):
        self.providers = providers

    async def fetch_income_statement(self, ticker: str) -> Any:
        """Fetch income statement from available providers.
        
        Returns:
            dict or list of financial data
            
        Raises:
            DataProviderError: If all providers fail or return empty data
        """
        errors = []
        for provider in self.providers:
            try:
                result = await provider.income_statement(ticker)
                
                # REJECT empty responses
                if result is None:
                    errors.append(f"{provider.__class__.__name__}: returned None")
                    continue
                
                if isinstance(result, (list, dict)) and len(result) == 0:
                    errors.append(f"{provider.__class__.__name__}: returned empty data")
                    continue
                
                # Valid response
                return result
                
            except Exception as e:
                errors.append(f"{provider.__class__.__name__}: {str(e)}")

        error_details = "; ".join(errors)
        raise DataProviderError(
            message=f"All providers failed to fetch income statement for {ticker}. "
                    f"Verify the ticker is valid (e.g., AAPL, RELIANCE.NS, INFY.NS).",
            suggestion=f"Check that {ticker} is a valid ticker symbol.",
            debug_details=f"Provider errors: {error_details}"
        )


class FinancialClient:
    def __init__(self, timeout: float = 10.0):
        self.client = httpx.AsyncClient(timeout=timeout)

    async def fetch_financial_statement(self, entity: str) -> Dict[str, Any]:
        """Fetch financial statement data for a given entity."""
        try:
            # Placeholder URL; replace with actual financial data API endpoint
            url = f"https://api.example.com/financials/{entity}"
            request = httpx.Request("GET", url)
            response = httpx.Response(404, request=request)
            raise httpx.HTTPStatusError("Not Found", request=request, response=response)  # Placeholder for demonstration
        except httpx.HTTPStatusError as e:
            raise DataProviderError(
                message=f"Failed to fetch data for {entity}",
                suggestion="Check the financial data source and try again.",
                debug_details=str(e)
            ) from e