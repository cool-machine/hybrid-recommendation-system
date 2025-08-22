"""Integration tests for deployment configurations."""
import pytest
import os
from pathlib import Path
import sys

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))


class TestAzureFunctionsDeployment:
    """Test Azure Functions deployment configuration."""
    
    def test_artifacts_path_exists(self):
        """Test that artifacts directory exists."""
        artifacts_path = Path(__file__).parent.parent.parent / "artifacts"
        assert artifacts_path.exists(), "Artifacts directory should exist"
        assert artifacts_path.is_dir(), "Artifacts should be a directory"
    
    def test_required_artifacts_present(self):
        """Test that required model artifacts are present."""
        artifacts_path = Path(__file__).parent.parent.parent / "artifacts"
        
        required_files = [
            "cf_i2i_top300.npy",
            "als_top100.npy", 
            "final_twotower_item_embeddings.npy",
            "final_twotower_user_embeddings.npy",
            "valid_clicks.parquet",
            "reranker.txt"
        ]
        
        for file_name in required_files:
            file_path = artifacts_path / file_name
            assert file_path.exists(), f"Required artifact {file_name} should exist"
    
    def test_function_app_structure(self):
        """Test Azure Functions app structure."""
        function_path = Path(__file__).parent.parent.parent / "deployment" / "azure_functions"
        
        # Check main function app files
        assert (function_path / "requirements.txt").exists()
        assert (function_path / "HttpReco" / "__init__.py").exists()
        assert (function_path / "HttpReco" / "function.json").exists()
    
    def test_requirements_format(self):
        """Test that requirements.txt is properly formatted."""
        requirements_path = Path(__file__).parent.parent.parent / "deployment" / "azure_functions" / "requirements.txt"
        
        if requirements_path.exists():
            content = requirements_path.read_text()
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            
            # Check for required packages
            required_packages = ["pandas", "numpy", "lightgbm"]
            for package in required_packages:
                assert any(package in line for line in lines), f"Required package {package} should be in requirements.txt"


class TestStreamlitDeployment:
    """Test Streamlit deployment configuration."""
    
    def test_streamlit_app_exists(self):
        """Test that Streamlit app file exists."""
        app_path = Path(__file__).parent.parent.parent / "deployment" / "streamlit" / "app.py"
        assert app_path.exists(), "Streamlit app.py should exist"
    
    def test_streamlit_config(self):
        """Test Streamlit configuration."""
        config_path = Path(__file__).parent.parent.parent / ".streamlit" / "config.toml"
        
        if config_path.exists():
            content = config_path.read_text()
            assert "[theme]" in content, "Streamlit config should have theme section"


class TestDockerDeployment:
    """Test Docker deployment configuration."""
    
    def test_dockerfile_exists(self):
        """Test that Dockerfile exists for containerization."""
        dockerfile_path = Path(__file__).parent.parent.parent / "Dockerfile"
        
        # Docker deployment is optional
        if dockerfile_path.exists():
            content = dockerfile_path.read_text()
            assert "FROM python:" in content, "Dockerfile should specify Python base image"
            assert "COPY requirements.txt" in content, "Dockerfile should copy requirements"


class TestEnvironmentConfiguration:
    """Test environment and configuration management."""
    
    def test_gitignore_excludes_secrets(self):
        """Test that .gitignore excludes sensitive files."""
        gitignore_path = Path(__file__).parent.parent.parent / ".gitignore"
        
        if gitignore_path.exists():
            content = gitignore_path.read_text()
            
            # Check for sensitive file patterns
            sensitive_patterns = [
                "*.env",
                ".env",
                "__pycache__",
                "*.pyc",
                ".venv",
                "venv/"
            ]
            
            for pattern in sensitive_patterns:
                assert pattern in content, f"Gitignore should exclude {pattern}"
    
    def test_no_hardcoded_secrets(self):
        """Test that code files don't contain hardcoded secrets."""
        code_files = []
        
        # Find Python files
        for root in ["src", "deployment"]:
            root_path = Path(__file__).parent.parent.parent / root
            if root_path.exists():
                code_files.extend(root_path.rglob("*.py"))
        
        # Common secret patterns
        secret_patterns = [
            "password =",
            "api_key =",
            "secret =",
            "token =",
            "connection_string ="
        ]
        
        for file_path in code_files:
            if file_path.exists():
                content = file_path.read_text().lower()
                for pattern in secret_patterns:
                    assert pattern not in content, f"Potential hardcoded secret in {file_path}: {pattern}"


class TestDataValidation:
    """Test data integrity and validation."""
    
    def test_sample_data_integrity(self):
        """Test that sample data files are valid."""
        data_path = Path(__file__).parent.parent.parent / "data" / "sample"
        
        if data_path.exists():
            csv_files = list(data_path.glob("*.csv"))
            
            for csv_file in csv_files:
                # Basic validation - file should not be empty
                assert csv_file.stat().st_size > 0, f"Sample data file {csv_file} should not be empty"
    
    def test_model_artifacts_size(self):
        """Test that model artifacts have reasonable sizes."""
        artifacts_path = Path(__file__).parent.parent.parent / "artifacts"
        
        if artifacts_path.exists():
            npy_files = list(artifacts_path.glob("*.npy"))
            
            for npy_file in npy_files:
                file_size = npy_file.stat().st_size
                # Model files should be at least 1KB and less than 500MB
                assert file_size > 1024, f"Model file {npy_file} seems too small"
                assert file_size < 500 * 1024 * 1024, f"Model file {npy_file} seems too large"


class TestPerformanceRequirements:
    """Test performance and scalability requirements."""
    
    def test_import_performance(self):
        """Test that imports don't take too long."""
        import time
        
        start_time = time.time()
        
        try:
            # Test critical imports
            import pandas as pd
            import numpy as np
            from pathlib import Path
        except ImportError as e:
            pytest.fail(f"Critical import failed: {e}")
        
        import_time = time.time() - start_time
        
        # Imports should complete within reasonable time
        assert import_time < 5.0, f"Imports took too long: {import_time:.2f}s"
    
    def test_memory_usage_reasonable(self):
        """Test that basic operations don't use excessive memory."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform basic operations
        import pandas as pd
        import numpy as np
        
        # Create sample data
        sample_data = pd.DataFrame({
            'user_id': range(1000),
            'item_id': range(1000, 2000),
            'rating': np.random.random(1000)
        })
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB for basic operations)
        assert memory_increase < 100, f"Excessive memory usage: {memory_increase:.2f}MB"