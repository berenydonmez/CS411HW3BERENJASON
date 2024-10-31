import pytest
from meal_max.models.meal import Meal, create_meal, get_meal_by_id, get_meal_by_name, delete_meal, update_meal_stats, get_leaderboard

@pytest.fixture
def sample_meal1():
    """Fixture to provide sample meal for testing."""
    return Meal(
        id=1,
        meal="Manti",
        cuisine="Turkish",
        price=12.99,
        difficulty="MED"
    )

@pytest.fixture
def sample_meal2():
    """Fixture to provide another sample meal for testing."""
    return Meal(
        id=2,
        meal="Sushi Roll",
        cuisine="Japanese",
        price=15.99,
        difficulty="HIGH"
    )

@pytest.fixture
def mock_db_connection(mocker):
    """Mock database connection for testing."""
    mock_conn = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_conn.__enter__.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    return mocker.patch('meal_max.utils.sql_utils.get_db_connection', return_value=mock_conn)

##################################################
# Meal Creation Test Cases
##################################################

def test_create_meal_success(mock_db_connection):
    """Test success of meal creation."""
    create_meal("Manti", "Turkish", 12.99, "MED")
    
    mock_cursor = mock_db_connection().cursor()
    mock_cursor.execute.assert_called_once()
    assert "INSERT INTO meals" in mock_cursor.execute.call_args[0][0]

def test_create_meal_invalid_price():
    """Test create_meal raises error for invalid price."""
    with pytest.raises(ValueError, match="Invalid price: -5. Price must be a positive number"):
        create_meal("Manti", "Turkish", -5, "MED")

def test_create_meal_invalid_difficulty():
    """Test create_meal raises error for invalid difficulty."""
    with pytest.raises(ValueError, match="Invalid difficulty level: EXTREME"):
        create_meal("Manti", "Turkish", 12.99, "EXTREME")

def test_create_duplicate_meal(mock_db_connection):
    """Test create_meal raises error for duplicate meal name."""
    mock_cursor = mock_db_connection().cursor()
    mock_cursor.execute.side_effect = sqlite3.IntegrityError
    
    with pytest.raises(ValueError, match="Meal with name 'Manti' already exists"):
        create_meal("Manti", "Turkish", 12.99, "MED")

##################################################
# Meal Retrieval Test Cases
##################################################

def test_get_meal_by_id_success(mock_db_connection, sample_meal1):
    """Test successful meal getting by the meals ID."""
    mock_cursor = mock_db_connection().cursor()
    mock_cursor.fetchone.return_value = (1, "Manti", "Turkish", 12.99, "MED", False)
    
    meal = get_meal_by_id(1)
    assert meal.meal == "Manti"
    assert meal.cuisine == "Turkish"
    assert meal.price == 12.99
    assert meal.difficulty == "MED"

def test_get_meal_by_id_not_found(mock_db_connection):
    """Test get_meal_by_id raises error for non-existent ID."""
    mock_cursor = mock_db_connection().cursor()
    mock_cursor.fetchone.return_value = None
    
    with pytest.raises(ValueError, match="Meal with ID 999 not found"):
        get_meal_by_id(999)

def test_get_meal_by_name_success(mock_db_connection, sample_meal1):
    """Test successful meal getting by name."""
    mock_cursor = mock_db_connection().cursor()
    mock_cursor.fetchone.return_value = (1, "Manti", "Turkish", 12.99, "MED", False)
    
    meal = get_meal_by_name("Manti")
    assert meal.meal == "Manti"
    assert meal.cuisine == "Turkish"

##################################################
# Meal Deletion Test Cases
##################################################

def test_delete_meal_success(mock_db_connection):
    """Test successful meal delete."""
    mock_cursor = mock_db_connection().cursor()
    mock_cursor.fetchone.return_value = (False,)
    
    delete_meal(1)
    assert "UPDATE meals SET deleted = TRUE" in mock_cursor.execute.call_args_list[-1][0][0]

def test_delete_already_deleted_meal(mock_db_connection):
    """Test delete_meal raises error for already deleted meal."""
    mock_cursor = mock_db_connection().cursor()
    mock_cursor.fetchone.return_value = (True,)
    
    with pytest.raises(ValueError, match="Meal with ID 1 has been deleted"):
        delete_meal(1)

##################################################
# Battle Statistics Test Cases
##################################################

def test_update_meal_stats_win(mock_db_connection):
    """Test updating meal statistics when win."""
    mock_cursor = mock_db_connection().cursor()
    mock_cursor.fetchone.return_value = (False,)
    
    update_meal_stats(1, 'win')
    assert "UPDATE meals SET battles = battles + 1, wins = wins + 1" in mock_cursor.execute.call_args_list[-1][0][0]

def test_update_meal_stats_loss(mock_db_connection):
    """Test updating meal statistics when loss."""
    mock_cursor = mock_db_connection().cursor()
    mock_cursor.fetchone.return_value = (False,)
    
    update_meal_stats(1, 'loss')
    assert "UPDATE meals SET battles = battles + 1" in mock_cursor.execute.call_args_list[-1][0][0]

def test_update_meal_stats_invalid_result(mock_db_connection):
    """Test update_meal_stats raises error for invalid result."""
    mock_cursor = mock_db_connection().cursor()
    mock_cursor.fetchone.return_value = (False,)
    
    with pytest.raises(ValueError, match="Invalid result: draw"):
        update_meal_stats(1, 'draw')

##################################################
# Leaderboard Test Cases
##################################################

def test_get_leaderboard_by_wins(mock_db_connection):
    """Test retrieve leaderboard sorted by wins."""
    mock_cursor = mock_db_connection().cursor()
    mock_cursor.fetchall.return_value = [
        (1, "Manti", "Turkish", 12.99, "MED", 10, 8, 0.8),
        (2, "Sushi", "Japanese", 15.99, "HIGH", 8, 6, 0.75)
    ]
    
    leaderboard = get_leaderboard("wins")
    assert len(leaderboard) == 2
    assert leaderboard[0]['wins'] == 8
    assert leaderboard[0]['win_pct'] == 80.0

def test_get_leaderboard_invalid_sort(mock_db_connection):
    """Test get_leaderboard raises error for invalid sort parameter."""
    with pytest.raises(ValueError, match="Invalid sort_by parameter: invalid"):
        get_leaderboard("invalid")
