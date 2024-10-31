import pytest
import requests
from meal_max.utils.random_utils import get_random

@pytest.fixture
def mock_requests_get(mocker):
    """Fixture to mock  requests.get function."""
    return mocker.patch('requests.get')

@pytest.fixture
def mock_response():
    """Fixture to create a mock response object."""
    class MockResponse:
        def __init__(self, text="0.55", status_code=200):
            self.text = text
            self.status_code = status_code
        
        def raise_for_status(self):
            if self.status_code != 200:
                raise requests.exceptions.HTTPError(
                    f"HTTP Error: {self.status_code}"
                )
    
    return MockResponse

##################################################
# Successful Request Test Cases
##################################################

def test_get_random_success(mock_requests_get, mock_response):
    """Test successful random number retrieval."""
    # Setup mock response
    mock_requests_get.return_value = mock_response(text="0.55\n")
    
    # Execute function
    result = get_random()
    
    # Verify results
    assert result == 0.55
    mock_requests_get.assert_called_once()
    assert "random.org" in mock_requests_get.call_args[0][0]

def test_get_random_different_values(mock_requests_get, mock_response):
    """Test getting different random values."""
    test_values = ["0.12\n", "0.98\n", "0.50\n"]
    expected_values = [0.12, 0.98, 0.50]
    
    for test_value, expected in zip(test_values, expected_values):
        mock_requests_get.return_value = mock_response(text=test_value)
        result = get_random()
        assert result == expected

##################################################
# Error Handling Test Cases
##################################################

def test_get_random_timeout(mock_requests_get):
    """Test handling of timeout errors."""
    mock_requests_get.side_effect = requests.exceptions.Timeout
    
    with pytest.raises(RuntimeError, match="Request to random.org timed out"):
        get_random()

def test_get_random_connection_error(mock_requests_get):
    """Test handling of connection errors."""
    mock_requests_get.side_effect = requests.exceptions.ConnectionError("Connection refused")
    
    with pytest.raises(RuntimeError, match="Request to random.org failed"):
        get_random()

def test_get_random_http_error(mock_requests_get, mock_response):
    """Test handling of HTTP errors."""
    mock_requests_get.return_value = mock_response(status_code=500)
    
    with pytest.raises(RuntimeError, match="Request to random.org failed"):
        get_random()

def test_get_random_invalid_response(mock_requests_get, mock_response):
    """Test handling of invalid response format."""
    mock_requests_get.return_value = mock_response(text="not a number")
    
    with pytest.raises(ValueError, match="Invalid response from random.org"):
        get_random()

##################################################
# Request Parameter Test Cases
##################################################

def test_get_random_request_parameters(mock_requests_get, mock_response):
    """Test that the request is made with correct parameters."""
    mock_requests_get.return_value = mock_response()
    
    get_random()
    
    args, kwargs = mock_requests_get.call_args
    url = args[0]
    
    assert "random.org" in url
    assert "decimal-fractions" in url
    assert "num=1" in url
    assert "dec=2" in url
    assert "format=plain" in url
    assert kwargs.get('timeout') == 5

##################################################
# Edge Case Test Cases
##################################################

def test_get_random_empty_response(mock_requests_get, mock_response):
    """Test handling of empty response."""
    mock_requests_get.return_value = mock_response(text="\n")
    
    with pytest.raises(ValueError, match="Invalid response from random.org"):
        get_random()

def test_get_random_whitespace_response(mock_requests_get, mock_response):
    """Test handling of whitespace response."""
    mock_requests_get.return_value = mock_response(text="  \n  ")
    
    with pytest.raises(ValueError, match="Invalid response from random.org"):
        get_random()

def test_get_random_invalid_number_formats(mock_requests_get, mock_response):
    """Test handling of various invalid number formats."""
    invalid_formats = [
        "1,23",  
        "1.2.3", 
        "abc",    
        "0.5f",   
        ""        
    ]
    
    for invalid_format in invalid_formats:
        mock_requests_get.return_value = mock_response(text=invalid_format)
        with pytest.raises(ValueError, match="Invalid response from random.org"):
            get_random()

##################################################
# Response Processing Test Cases
##################################################

def test_get_random_strips_whitespace(mock_requests_get, mock_response):
    """Test that whitespace is properly stripped from response."""
    mock_requests_get.return_value = mock_response(text="  0.55  \n")
    
    result = get_random()
    
    assert result == 0.55

def test_get_random_range(mock_requests_get, mock_response):
    """Test that returned values are within expected range."""
    test_values = ["0.00\n", "0.50\n", "0.99\n"]
    
    for value in test_values:
        mock_requests_get.return_value = mock_response(text=value)
        result = get_random()
        assert 0 <= result <= 1
