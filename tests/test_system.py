#!/usr/bin/env python3
"""
Comprehensive test suite for the recommendation system implementation
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

import numpy as np
import pandas as pd

from src.service import RecommendationService
from src.config import Config, ModelConfig

def print_section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print('='*60)

def print_result(test_name: str, passed: bool, details: str = "") -> None:
    """Print test result with status."""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"    {details}")

def test_artifacts_availability() -> bool:
    """Test if all required artifacts are available."""
    print_section("Testing Artifact Availability")
    
    artifacts_dir = Path("deployment/azure_functions/artifacts")
    
    required_files = [
        "als_top100.npy",
        "cf_i2i_top300.npy", 
        "final_twotower_item_vec.npy",
        "final_twotower_user_vec.npy",
        "last_click.npy",
        "pop_list.npy",
        "reranker.txt",
        "tt_top200.npy",
        "valid_clicks.parquet"
    ]
    
    all_available = True
    for filename in required_files:
        filepath = artifacts_dir / filename
        available = filepath.exists()
        all_available = all_available and available
        
        if available:
            size = filepath.stat().st_size
            print_result(f"Artifact {filename}", True, f"Size: {size:,} bytes")
        else:
            print_result(f"Artifact {filename}", False, "File not found")
    
    return all_available

def test_configuration() -> bool:
    """Test configuration loading and validation."""
    print_section("Testing Configuration")
    
    try:
        # Test default config
        config = Config()
        print_result("Default config creation", True)
        
        # Test config with artifacts directory
        artifacts_dir = Path("deployment/azure_functions/artifacts")
        config = Config.load(artifacts_dir)
        print_result("Config loading with artifacts dir", True, f"Artifacts: {config.model.artifacts_dir}")
        
        # Test validation (if artifacts exist)
        if artifacts_dir.exists():
            try:
                config.validate()
                print_result("Config validation", True, "All required files found")
                return True
            except (ValueError, FileNotFoundError) as e:
                print_result("Config validation", False, str(e))
                return False
        else:
            print_result("Config validation", False, "Artifacts directory not found")
            return False
            
    except Exception as e:
        print_result("Configuration test", False, str(e))
        return False

def test_service_initialization() -> tuple[bool, RecommendationService]:
    """Test service initialization."""
    print_section("Testing Service Initialization")
    
    try:
        # Initialize with artifacts directory
        artifacts_dir = Path("deployment/azure_functions/artifacts")
        config = Config.load(artifacts_dir)
        
        service = RecommendationService(config)
        print_result("Service creation", True)
        
        # Check initial state
        ready_before = service.is_ready()
        print_result("Service ready before loading", ready_before, "Should be False initially")
        
        return True, service
        
    except Exception as e:
        print_result("Service initialization", False, str(e))
        return False, None

def test_model_loading(service: RecommendationService) -> bool:
    """Test model loading."""
    print_section("Testing Model Loading")
    
    if not service:
        print_result("Model loading", False, "Service not available")
        return False
    
    try:
        start_time = time.time()
        service.load_models()
        load_time = time.time() - start_time
        
        print_result("Model loading", True, f"Loaded in {load_time:.2f}s")
        
        # Check if service is ready after loading
        ready_after = service.is_ready()
        print_result("Service ready after loading", ready_after)
        
        # Get status
        status = service.get_status()
        print_result("Service status retrieval", True, f"Models: {len(status['models'])}")
        
        # Print detailed status
        print("\n📊 Detailed Status:")
        print(f"  Service Ready: {status['service_ready']}")
        print(f"  Models: {status['models']}")
        print(f"  Config: {status['config']}")
        print(f"  Auxiliary Data: {status['auxiliary_data']}")
        
        return ready_after
        
    except Exception as e:
        print_result("Model loading", False, str(e))
        return False

def test_recommendations(service: RecommendationService) -> bool:
    """Test recommendation generation."""
    print_section("Testing Recommendation Generation")
    
    if not service or not service.is_ready():
        print_result("Recommendation test", False, "Service not ready")
        return False
    
    test_results = []
    
    # Test cold user recommendations
    try:
        print("\n🧊 Testing Cold User Recommendations:")
        cold_user_context = {
            "device": 1,
            "os": 2, 
            "country": "US"
        }
        
        cold_result = service.get_recommendations(
            user_id=99999,  # Likely a cold user
            k=10,
            context=cold_user_context
        )
        
        cold_success = (
            "recommendations" in cold_result and
            len(cold_result["recommendations"]) > 0 and
            cold_result.get("user_type") == "cold"
        )
        
        print_result("Cold user recommendations", cold_success, 
                    f"Got {len(cold_result.get('recommendations', []))} recs, "
                    f"Algorithm: {cold_result.get('algorithm')}")
        
        test_results.append(cold_success)
        
    except Exception as e:
        print_result("Cold user recommendations", False, str(e))
        test_results.append(False)
    
    # Test warm user recommendations
    try:
        print("\n🔥 Testing Warm User Recommendations:")
        
        # Try several user IDs to find a warm user
        for user_id in [0, 1, 100, 1000]:
            try:
                warm_result = service.get_recommendations(user_id=user_id, k=10)
                
                if warm_result.get("user_type") == "warm":
                    warm_success = (
                        "recommendations" in warm_result and
                        len(warm_result["recommendations"]) > 0
                    )
                    
                    print_result(f"Warm user {user_id} recommendations", warm_success,
                                f"Got {len(warm_result.get('recommendations', []))} recs, "
                                f"Algorithm: {warm_result.get('algorithm')}, "
                                f"Candidates: {warm_result.get('candidate_count', 'N/A')}")
                    
                    test_results.append(warm_success)
                    break
                    
            except Exception as e:
                print_result(f"Warm user {user_id} test", False, str(e))
                continue
        else:
            print_result("Warm user recommendations", False, "No warm users found")
            test_results.append(False)
            
    except Exception as e:
        print_result("Warm user recommendations", False, str(e))
        test_results.append(False)
    
    return all(test_results)

def test_edge_cases(service: RecommendationService) -> bool:
    """Test edge cases and error handling."""
    print_section("Testing Edge Cases")
    
    if not service or not service.is_ready():
        print_result("Edge case testing", False, "Service not ready")
        return False
    
    test_results = []
    
    # Test invalid user ID
    try:
        result = service.get_recommendations(user_id=-1, k=10)
        has_error = "error" in result or len(result.get("recommendations", [])) == 0
        print_result("Invalid user ID handling", has_error, "Should handle gracefully")
        test_results.append(has_error)
    except Exception as e:
        print_result("Invalid user ID handling", True, f"Caught exception: {type(e).__name__}")
        test_results.append(True)
    
    # Test k=0
    try:
        result = service.get_recommendations(user_id=1, k=0)
        # Should return at least 1 recommendation due to max(1, k) logic
        valid_k_handling = len(result.get("recommendations", [])) >= 1
        print_result("k=0 handling", valid_k_handling, "Should return at least 1 rec")
        test_results.append(valid_k_handling)
    except Exception as e:
        print_result("k=0 handling", False, str(e))
        test_results.append(False)
    
    # Test very large k
    try:
        result = service.get_recommendations(user_id=1, k=1000)
        # Should be capped by max_recommendations
        reasonable_count = len(result.get("recommendations", [])) <= 100
        print_result("Large k handling", reasonable_count, 
                    f"Got {len(result.get('recommendations', []))} recs (should be ≤100)")
        test_results.append(reasonable_count)
    except Exception as e:
        print_result("Large k handling", False, str(e))
        test_results.append(False)
    
    return all(test_results)

def test_performance(service: RecommendationService) -> bool:
    """Test recommendation performance."""
    print_section("Testing Performance")
    
    if not service or not service.is_ready():
        print_result("Performance testing", False, "Service not ready")
        return False
    
    try:
        # Test recommendation latency
        user_ids = [0, 1, 100, 1000, 10000]
        latencies = []
        
        for user_id in user_ids:
            start_time = time.time()
            result = service.get_recommendations(user_id=user_id, k=10)
            latency = (time.time() - start_time) * 1000  # Convert to milliseconds
            latencies.append(latency)
            
            success = len(result.get("recommendations", [])) > 0
            print_result(f"User {user_id} latency", success, f"{latency:.1f}ms")
        
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        
        # Performance thresholds
        avg_ok = avg_latency < 500  # Average < 500ms
        max_ok = max_latency < 1000  # Max < 1000ms
        
        print_result("Average latency", avg_ok, f"{avg_latency:.1f}ms (target: <500ms)")
        print_result("Maximum latency", max_ok, f"{max_latency:.1f}ms (target: <1000ms)")
        
        return avg_ok and max_ok
        
    except Exception as e:
        print_result("Performance testing", False, str(e))
        return False

def run_comprehensive_tests() -> Dict[str, bool]:
    """Run all tests and return results."""
    print("🚀 Starting Comprehensive Recommendation System Tests")
    print(f"📁 Working directory: {Path.cwd()}")
    
    results = {}
    
    # Test 1: Artifact availability
    results["artifacts"] = test_artifacts_availability()
    
    # Test 2: Configuration
    results["configuration"] = test_configuration()
    
    # Only proceed if basic setup works
    if not (results["artifacts"] and results["configuration"]):
        print_section("Stopping Tests - Basic Setup Failed")
        return results
    
    # Test 3: Service initialization
    service_ok, service = test_service_initialization()
    results["service_init"] = service_ok
    
    if not service_ok:
        print_section("Stopping Tests - Service Initialization Failed")
        return results
    
    # Test 4: Model loading
    results["model_loading"] = test_model_loading(service)
    
    if not results["model_loading"]:
        print_section("Stopping Tests - Model Loading Failed")
        return results
    
    # Test 5: Recommendations
    results["recommendations"] = test_recommendations(service)
    
    # Test 6: Edge cases
    results["edge_cases"] = test_edge_cases(service)
    
    # Test 7: Performance
    results["performance"] = test_performance(service)
    
    return results

def print_final_summary(results: Dict[str, bool]) -> None:
    """Print final test summary."""
    print_section("Final Test Summary")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"📊 Test Results: {passed_tests}/{total_tests} ({success_rate:.1f}%) passed\n")
    
    for test_name, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {test_name.replace('_', ' ').title()}")
    
    if success_rate == 100:
        print(f"\n🎉 All tests passed! The recommendation system is working correctly.")
    elif success_rate >= 80:
        print(f"\n⚠️  Most tests passed. Some issues need attention.")
    else:
        print(f"\n🚨 Multiple test failures. System needs debugging.")

if __name__ == "__main__":
    try:
        results = run_comprehensive_tests()
        print_final_summary(results)
        
        # Exit with non-zero code if tests failed
        if not all(results.values()):
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)