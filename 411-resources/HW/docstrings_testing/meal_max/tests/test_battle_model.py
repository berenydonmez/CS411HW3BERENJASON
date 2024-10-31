import pytest
from unittest.mock import Mock
from meal_max.models.battle_model import BattleModel
from meal_max.models.kitchen_model import Meal

@pytest.fixture
def battle_model():
    """Fixture to provide new instance of BattleModel for each test."""
    return BattleModel()

@pytest.fixture
def sample_meal1():
    """Fixture to provide a sample meal for testing."""
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
def mock_random(mocker):
    """Mock the random number generator."""
    return mocker.patch('meal_max.utils.random_utils.get_random', return_value=0.5)

@pytest.fixture
def mock_update_stats(mocker):
    """Mock the update_meal_stats function."""
    return mocker.patch('meal_max.models.battle_model.update_meal_stats')

##################################################
# Combatant Management Test Cases
##################################################

def test_prep_combatant_success(battle_model, sample_meal1):
    """Test successful addition of a combatant."""
    battle_model.prep_combatant(sample_meal1)
    assert len(battle_model.get_combatants()) == 1
    assert battle_model.combatants[0].meal == "Manti"

def test_prep_combatant_full_list(battle_model, sample_meal1, sample_meal2):
    """Test error when adding combatant to full list."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    
    extra_meal = Meal(id=3, meal="Extra", cuisine="Test", price=10.0, difficulty="LOW")
    with pytest.raises(ValueError, match="Combatant list is full"):
        battle_model.prep_combatant(extra_meal)

def test_clear_combatants(battle_model, sample_meal1):
    """Test clearing  combatants list."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.clear_combatants()
    assert len(battle_model.get_combatants()) == 0

def test_get_combatants(battle_model, sample_meal1, sample_meal2):
    """Test retrieving the list of combatants."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    combatants = battle_model.get_combatants()
    assert len(combatants) == 2
    assert combatants[0].meal == "Manti"
    assert combatants[1].meal == "Sushi Roll"

##################################################
# Battle Score Calculation Test Cases
##################################################

def test_get_battle_score(battle_model, sample_meal1):
    """Test battle score calculation."""
    score = battle_model.get_battle_score(sample_meal1)
    expected_score = 12.99 * len("Turkish") - 2  
    assert score == pytest.approx(expected_score, 0.001)

def test_get_battle_score_different_difficulties(battle_model):
    """Test battle scores with different difficulties."""
    high_diff_meal = Meal(id=1, meal="Test", cuisine="Test", price=10.0, difficulty="HIGH")
    med_diff_meal = Meal(id=2, meal="Test", cuisine="Test", price=10.0, difficulty="MED")
    low_diff_meal = Meal(id=3, meal="Test", cuisine="Test", price=10.0, difficulty="LOW")
    
    high_score = battle_model.get_battle_score(high_diff_meal)
    med_score = battle_model.get_battle_score(med_diff_meal)
    low_score = battle_model.get_battle_score(low_diff_meal)
    
    assert high_score < med_score < low_score

##################################################
# Battle Execution Test Cases
##################################################

def test_battle_not_enough_combatants(battle_model, sample_meal1):
    """Test battle raises error for insufficient combatants."""
    battle_model.prep_combatant(sample_meal1)
    with pytest.raises(ValueError, match="Two combatants must be prepped"):
        battle_model.battle()

def test_battle_execution(battle_model, sample_meal1, sample_meal2, mock_random, mock_update_stats):
    """Test complete battle execution."""
    mock_random.return_value = 0.3  # Set random number less than normalized delta
    
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    
    winner = battle_model.battle()
    
    assert winner in [sample_meal1.meal, sample_meal2.meal]
    assert mock_update_stats.call_count == 2
    assert len(battle_model.combatants) == 1

def test_battle_random_influence(battle_model, sample_meal1, sample_meal2, mock_random, mock_update_stats):
    """Test the way random number influences the battle outcome."""
    mock_random.return_value = 0.1
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    winner1 = battle_model.battle()
    
    battle_model.clear_combatants()
    mock_random.return_value = 0.9
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal2)
    winner2 = battle_model.battle()
    
    assert mock_update_stats.call_count == 4

##################################################
# Edge Cases and Error Handling
##################################################

def test_battle_with_identical_meals(battle_model, sample_meal1, mock_random, mock_update_stats):
    """Test battle between identical meals."""
    identical_meal = Meal(
        id=2,
        meal="Manti Clone",
        cuisine="Turkish",
        price=12.99,
        difficulty="MED"
    )
    
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(identical_meal)
    
    winner = battle_model.battle()
    assert winner in [sample_meal1.meal, identical_meal.meal]
    assert mock_update_stats.call_count == 2

def test_prep_same_meal_twice(battle_model, sample_meal1):
    """Test to add the same meal twice."""
    battle_model.prep_combatant(sample_meal1)
    battle_model.prep_combatant(sample_meal1)
    assert len(battle_model.combatants) == 2
