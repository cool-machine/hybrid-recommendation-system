"""Entry point for Azure Functions Python v2 host discovery.

This module simply imports and re-exports the `FunctionApp` instance defined
inside the `HttpReco` package. Azure Functions Core Tools scans top-level
Python files in the app directory and looks for a variable named `app` that is
an instance of `azure.functions.FunctionApp`. Importing it here ensures the
function routes are registered even though the actual implementation lives in
`HttpReco/__init__.py`.
"""
from HttpReco import app  # noqa: F401
