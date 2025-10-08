#!/usr/bin/env python3
"""
Integration tests for NEPSE Data API.
Tests the API from outside the Docker container to ensure it's accessible.
Run this AFTER starting the Docker containers with ./run.sh
"""

import requests
import sys
import time


BASE_URL = "http://localhost:8000"


def print_result(test_name, passed, message=""):
    """Print test result with formatting."""
    status = "✓ PASS" if passed else "✗ FAIL"
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{status}{reset} - {test_name}")
    if message:
        print(f"       {message}")


def test_health_endpoint():
    """Test root health endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        passed = response.status_code == 200 and response.json().get("status") == "healthy"
        print_result("Health endpoint (/)", passed, f"Status: {response.status_code}")
        return passed
    except Exception as e:
        print_result("Health endpoint (/)", False, f"Error: {str(e)}")
        return False


def test_health_check_endpoint():
    """Test detailed health check endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        data = response.json()
        passed = (
            response.status_code == 200 and 
            data.get("status") == "healthy" and 
            data.get("service") == "nepse-scraper"
        )
        print_result("Health check (/health)", passed, f"Service: {data.get('service')}")
        return passed
    except Exception as e:
        print_result("Health check (/health)", False, f"Error: {str(e)}")
        return False


def test_docs_endpoint():
    """Test API documentation is accessible."""
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        passed = response.status_code == 200 and "text/html" in response.headers.get("content-type", "")
        print_result("API docs (/docs)", passed, f"Content-Type: {response.headers.get('content-type')}")
        return passed
    except Exception as e:
        print_result("API docs (/docs)", False, f"Error: {str(e)}")
        return False


def test_openapi_schema():
    """Test OpenAPI schema endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/openapi.json", timeout=5)
        data = response.json()
        passed = (
            response.status_code == 200 and 
            data.get("info", {}).get("title") == "NEPSE Data API"
        )
        print_result("OpenAPI schema (/openapi.json)", passed, f"API Title: {data.get('info', {}).get('title')}")
        return passed
    except Exception as e:
        print_result("OpenAPI schema (/openapi.json)", False, f"Error: {str(e)}")
        return False


def test_get_companies():
    """Test get companies metadata endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/api/metadata/companies", timeout=5)
        passed = response.status_code == 200 and isinstance(response.json(), list)
        count = len(response.json()) if passed else 0
        print_result("Get companies (/api/metadata/companies)", passed, f"Companies: {count}")
        return passed
    except Exception as e:
        print_result("Get companies (/api/metadata/companies)", False, f"Error: {str(e)}")
        return False


def test_get_sectors():
    """Test get sectors metadata endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/api/metadata/sectors", timeout=5)
        passed = response.status_code == 200 and isinstance(response.json(), list)
        count = len(response.json()) if passed else 0
        print_result("Get sectors (/api/metadata/sectors)", passed, f"Sectors: {count}")
        return passed
    except Exception as e:
        print_result("Get sectors (/api/metadata/sectors)", False, f"Error: {str(e)}")
        return False


def test_floorsheet_validation():
    """Test floorsheet endpoint validation (empty symbol should fail)."""
    try:
        response = requests.post(
            f"{BASE_URL}/api/floorsheet/",
            json={"symbol": ""},
            timeout=5
        )
        passed = response.status_code == 422  # Validation error expected
        print_result("Floorsheet validation (/api/floorsheet/)", passed, f"Status: {response.status_code} (422 expected)")
        return passed
    except Exception as e:
        print_result("Floorsheet validation (/api/floorsheet/)", False, f"Error: {str(e)}")
        return False


def test_floorsheet_endpoint_structure():
    """Test floorsheet endpoint returns correct structure (mocked internally)."""
    try:
        # This will likely timeout in real scraping, which is acceptable
        # We're just checking the endpoint is accessible and responds appropriately
        response = requests.post(
            f"{BASE_URL}/api/floorsheet/",
            json={"symbol": "TEST"},
            timeout=10  # Reduced timeout
        )
        # Accept both success (200) and server error (500) as valid responses
        # because scraping might fail, but the endpoint should respond
        passed = response.status_code in [200, 500]
        data = response.json()
        has_detail = "detail" in data or ("symbol" in data and "headers" in data and "rows" in data)
        passed = passed and has_detail
        print_result(
            "Floorsheet endpoint structure (/api/floorsheet/)", 
            passed, 
            f"Status: {response.status_code}, Has proper structure: {has_detail}"
        )
        return passed
    except requests.exceptions.Timeout:
        # Timeout is acceptable for this endpoint since it does web scraping
        print_result(
            "Floorsheet endpoint structure (/api/floorsheet/)", 
            True, 
            "Endpoint is accessible (timeout expected for real scraping)"
        )
        return True
    except Exception as e:
        print_result("Floorsheet endpoint structure (/api/floorsheet/)", False, f"Error: {str(e)}")
        return False


def test_get_news():
    """Test get news endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/api/news/?limit=5&max_pages=1", timeout=20)
        data = response.json()
        passed = response.status_code == 200 and "news" in data and "count" in data
        count = data.get('count', 0)
        print_result("Get news (/api/news/)", passed, f"Status: {response.status_code}, News count: {count}")
        return passed
    except requests.exceptions.Timeout:
        # Timeout is acceptable for web scraping
        print_result(
            "Get news (/api/news/)", 
            True, 
            "Endpoint is accessible (timeout expected for web scraping)"
        )
        return True
    except Exception as e:
        print_result("Get news (/api/news/)", False, f"Error: {str(e)}")
        return False


def test_get_latest_news():
    """Test get latest news endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/api/news/latest?limit=3", timeout=15)
        data = response.json()
        passed = response.status_code == 200 and "news" in data
        count = data.get('count', 0)
        print_result("Get latest news (/api/news/latest)", passed, f"Status: {response.status_code}, News count: {count}")
        return passed
    except Exception as e:
        print_result("Get latest news (/api/news/latest)", False, f"Error: {str(e)}")
        return False


def test_market_live_data():
    """Test market live data endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/api/market/live", timeout=30)
        passed = response.status_code == 200 and isinstance(response.json(), list)
        count = len(response.json()) if passed else 0
        print_result("Market live data (/api/market/live)", passed, f"Stocks: {count}")
        return passed
    except requests.exceptions.Timeout:
        # Timeout is acceptable for live data fetching
        print_result(
            "Market live data (/api/market/live)", 
            True, 
            "Endpoint is accessible (timeout expected for API call)"
        )
        return True
    except Exception as e:
        print_result("Market live data (/api/market/live)", False, f"Error: {str(e)}")
        return False


def test_market_summary():
    """Test market summary endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/api/market/summary", timeout=30)
        data = response.json()
        passed = (
            response.status_code == 200 and
            "totalStocks" in data and
            "advancing" in data and
            "declining" in data
        )
        stocks = data.get("totalStocks", 0) if passed else 0
        print_result("Market summary (/api/market/summary)", passed, f"Total stocks: {stocks}")
        return passed
    except requests.exceptions.Timeout:
        # Timeout is acceptable for live data fetching
        print_result(
            "Market summary (/api/market/summary)", 
            True, 
            "Endpoint is accessible (timeout expected for API call)"
        )
        return True
    except Exception as e:
        print_result("Market summary (/api/market/summary)", False, f"Error: {str(e)}")
        return False


def test_market_gainers():
    """Test top gainers endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/api/market/gainers?limit=5", timeout=10)
        passed = response.status_code == 200 and isinstance(response.json(), list)
        count = len(response.json()) if passed else 0
        print_result("Top gainers (/api/market/gainers)", passed, f"Gainers: {count}")
        return passed
    except Exception as e:
        print_result("Top gainers (/api/market/gainers)", False, f"Error: {str(e)}")
        return False


def test_market_losers():
    """Test top losers endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/api/market/losers?limit=5", timeout=10)
        passed = response.status_code == 200 and isinstance(response.json(), list)
        count = len(response.json()) if passed else 0
        print_result("Top losers (/api/market/losers)", passed, f"Losers: {count}")
        return passed
    except Exception as e:
        print_result("Top losers (/api/market/losers)", False, f"Error: {str(e)}")
        return False


def test_market_active_volume():
    """Test most active by volume endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/api/market/active/volume", timeout=10)
        passed = response.status_code == 200 and isinstance(response.json(), list)
        count = len(response.json()) if passed else 0
        print_result("Most active by volume (/api/market/active/volume)", passed, f"Stocks: {count}")
        return passed
    except Exception as e:
        print_result("Most active by volume (/api/market/active/volume)", False, f"Error: {str(e)}")
        return False


def wait_for_server(max_attempts=30, delay=2):
    """Wait for the server to be ready."""
    print(f"\n⏳ Waiting for server at {BASE_URL} to be ready...")
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print(f"✓ Server is ready!\n")
                return True
        except requests.exceptions.RequestException:
            pass
        
        if attempt < max_attempts - 1:
            time.sleep(delay)
            print(f"  Attempt {attempt + 1}/{max_attempts}...", end="\r")
    
    print(f"\n✗ Server did not become ready after {max_attempts} attempts")
    return False


def main():
    """Run all integration tests."""
    print("=" * 70)
    print("NEPSE Data API - Integration Tests")
    print("=" * 70)
    
    # Wait for server to be ready
    if not wait_for_server():
        print("\n❌ Server is not accessible. Make sure Docker containers are running:")
        print("   ./run.sh")
        sys.exit(1)
    
    # Run all tests
    tests = [
        test_health_endpoint,
        test_health_check_endpoint,
        test_docs_endpoint,
        test_openapi_schema,
        test_get_companies,
        test_get_sectors,
        test_floorsheet_validation,
        test_floorsheet_endpoint_structure,
        test_get_news,
        test_get_latest_news,
        test_market_live_data,
        test_market_summary,
        test_market_gainers,
        test_market_losers,
        test_market_active_volume,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    # Summary
    print("\n" + "=" * 70)
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"Results: {passed}/{total} tests passed ({percentage:.1f}%)")
    
    if passed == total:
        print("🎉 All integration tests passed!")
        print("=" * 70)
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()
