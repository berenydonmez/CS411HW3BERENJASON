# -*- coding: utf-8 -*-
"""Handles meal management for MealMax, including CRUD operations and battle 
statistics and provides database management for meals, letting creation, retrieval, 
and updating of meal data, also to track meal battle statistics.
"""

from dataclasses import dataclass
import logging
import sqlite3
from typing import Any

from meal_max.utils.sql_utils import get_db_connection
from meal_max.utils.logger import configure_logger


logger = logging.getLogger(__name__)
configure_logger(logger)


@dataclass
class Meal:
    """A class to represent a meal with its properties.

    Attributes:
        id (int): The identifier for the meal.
        meal (str): Name of the meal.
        cuisine (str): Type of cuisine (e.g., "Turkish", "Japanese").
        price (float): Price of the meal 
        difficulty (str): Preparation difficulty (must be 'LOW', 'MED', or 'HIGH').

    Raises:
        ValueError: If price is negative or difficulty is not one of the allowed values.
    """
    id: int
    meal: str
    cuisine: str
    price: float
    difficulty: str

    def __post_init__(self):
        """Validates meal attributes.

        Raises:
            ValueError: If price is not positive or difficulty is not 'LOW', 'MED', or 'HIGH'.
        """
        if self.price < 0:
            raise ValueError("Price must be a positive value.")
        if self.difficulty not in ['LOW', 'MED', 'HIGH']:
            raise ValueError("Difficulty must be 'LOW', 'MED', or 'HIGH'.")


def create_meal(meal: str, cuisine: str, price: float, difficulty: str) -> None:
    """Creates a new meal in the database.

    Args:
        meal (str): The meal's name.
        cuisine (str): The cuisine the meal belongs to.
        price (float): The price (positive) of the meal.
        difficulty (str): Preparing difficulty of meal.
        
    Returns:
        int: The ID of the newly created meal.

    Raises:
        ValueError: If price is not positive, difficulty is invalid, or meal
            name already exists.
        sqlite3.Error: For any different error with the database. 

    Example:
        >>> create_meal("Spaghetti", "Turkish", 12.99, "LOW")
    """
    if not isinstance(price, (int, float)) or price <= 0:
        raise ValueError(f"Invalid price: {price}. Price must be a positive number.")
    if difficulty not in ['LOW', 'MED', 'HIGH']:
        raise ValueError(f"Invalid difficulty level: {difficulty}. Must be 'LOW', 'MED', or 'HIGH'.")

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO meals (meal, cuisine, price, difficulty)
                VALUES (?, ?, ?, ?)
            """, (meal, cuisine, price, difficulty))
            conn.commit()

            logger.info("Meal successfully added to the database: %s", meal)

    except sqlite3.IntegrityError:
        logger.error("Duplicate meal name: %s", meal)
        raise ValueError(f"Meal with name '{meal}' already exists")

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e


def delete_meal(meal_id: int) -> None:
    """Deletes and marks the meal as deleted.

    Args:
        meal_id: The ID of the meal to delete.

    Raises:
        ValueError: If the meal is not found or has already been deleted.
        sqlite3.Error: For any different error with the database. 
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT deleted FROM meals WHERE id = ?", (meal_id,))
            try:
                deleted = cursor.fetchone()[0]
                if deleted:
                    logger.info("Meal with ID %s has already been deleted", meal_id)
                    raise ValueError(f"Meal with ID {meal_id} has been deleted")
            except TypeError:
                logger.info("Meal with ID %s not found", meal_id)
                raise ValueError(f"Meal with ID {meal_id} not found")

            cursor.execute("UPDATE meals SET deleted = TRUE WHERE id = ?", (meal_id,))
            conn.commit()

            logger.info("Meal with ID %s marked as deleted.", meal_id)

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e

def get_leaderboard(sort_by: str="wins") -> dict[str, Any]:
    """Gets the leaderboard of meals in the form of dictionary.

    Args:
        sort_by (str): Sorting criteria, either "wins" or "win_pct".

    Returns:
        dict[str, Any]: The dictionary having leaderboard entries for the meals.
     
    Raises:
        ValueError: If sorting criteria parameter is invalid.
        sqlite3.Error: For any different error with the database. 

    Example:
        >>> leaderboard = get_leaderboard(sort_by="win_pct")
        >>> print(leaderboard[0]['win_pct'])
    """
    query = """
        SELECT id, meal, cuisine, price, difficulty, battles, wins, (wins * 1.0 / battles) AS win_pct
        FROM meals WHERE deleted = false AND battles > 0
    """

    if sort_by == "win_pct":
        query += " ORDER BY win_pct DESC"
    elif sort_by == "wins":
        query += " ORDER BY wins DESC"
    else:
        logger.error("Invalid sort_by parameter: %s", sort_by)
        raise ValueError("Invalid sort_by parameter: %s" % sort_by)

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

        leaderboard = []
        for row in rows:
            meal = {
                'id': row[0],
                'meal': row[1],
                'cuisine': row[2],
                'price': row[3],
                'difficulty': row[4],
                'battles': row[5],
                'wins': row[6],
                'win_pct': round(row[7] * 100, 1)  # Convert to percentage
            }
            leaderboard.append(meal)

        logger.info("Leaderboard retrieved successfully")
        return leaderboard

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e

def get_meal_by_id(meal_id: int) -> Meal:
    """Retrieves a meal from the database by its ID.

    Args:
        meal_id(int): The ID of the meal to retrieve.

    Returns:
        A Meal object with the meal's information.

    Raises:
        ValueError: If the ID of meal is not found or has been deleted.
        sqlite3.Error: For any different error with the database. 

    Example:
        >>> meal = get_meal_by_id(1)
        >>> print(meal.cuisine)
        Turkish
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE id = ?", (meal_id,))
            row = cursor.fetchone()

            if row:
                if row[5]:
                    logger.info("Meal with ID %s has been deleted", meal_id)
                    raise ValueError(f"Meal with ID {meal_id} has been deleted")
                return Meal(id=row[0], meal=row[1], cuisine=row[2], price=row[3], difficulty=row[4])
            else:
                logger.info("Meal with ID %s not found", meal_id)
                raise ValueError(f"Meal with ID {meal_id} not found")

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e


def get_meal_by_name(meal_name: str) -> Meal:
    """Retrieves a meal from the database by its name.

    Args:
        meal_name: The name of the meal to retrieve.

    Returns:
        A Meal object with the meal's information.

    Raises:
        ValueError: If the name of meal is not found or has been deleted.
        sqlite3.Error: For any different error with the database. 

    Example:
        >>> meal = get_meal_by_name("Manti with yogurt")
        >>> print(meal.price)
        12.99
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, meal, cuisine, price, difficulty, deleted FROM meals WHERE meal = ?", (meal_name,))
            row = cursor.fetchone()

            if row:
                if row[5]:
                    logger.info("Meal with name %s has been deleted", meal_name)
                    raise ValueError(f"Meal with name {meal_name} has been deleted")
                return Meal(id=row[0], meal=row[1], cuisine=row[2], price=row[3], difficulty=row[4])
            else:
                logger.info("Meal with name %s not found", meal_name)
                raise ValueError(f"Meal with name {meal_name} not found")

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e


def update_meal_stats(meal_id: int, result: str) -> None:
    """Updates the statistics of  meal.

    Args:
        meal_id (int): The ID of the meal that will be updated.
        result (str): The battle outcome either 'win' or 'loss'.

    Raises:
        ValueError:  If the result is not found or has been deleted.
        sqlite3.Error: For any different error with the database. 

    Example:
        >>> update_meal_stats(1, 'win')  
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT deleted FROM meals WHERE id = ?", (meal_id,))
            try:
                deleted = cursor.fetchone()[0]
                if deleted:
                    logger.info("Meal with ID %s has been deleted", meal_id)
                    raise ValueError(f"Meal with ID {meal_id} has been deleted")
            except TypeError:
                logger.info("Meal with ID %s not found", meal_id)
                raise ValueError(f"Meal with ID {meal_id} not found")

            if result == 'win':
                cursor.execute("UPDATE meals SET battles = battles + 1, wins = wins + 1 WHERE id = ?", (meal_id,))
            elif result == 'loss':
                cursor.execute("UPDATE meals SET battles = battles + 1 WHERE id = ?", (meal_id,))
            else:
                raise ValueError(f"Invalid result: {result}. Expected 'win' or 'loss'.")

            conn.commit()

    except sqlite3.Error as e:
        logger.error("Database error: %s", str(e))
        raise e
