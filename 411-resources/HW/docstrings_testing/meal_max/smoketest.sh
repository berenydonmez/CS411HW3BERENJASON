#!/bin/bash

# Define the base URL for the Kitchen API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the kitchen connection
check_kitchen() {
  echo "Checking kitchen connection..."
  curl -s -X GET "$BASE_URL/kitchen-check" | grep -q '"kitchen_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Kitchen connection is healthy."
  else
    echo "Kitchen check failed."
    exit 1
  fi
}


##########################################################
#
# Meal Management
#
##########################################################

create_meal() {
  name=$1
  ingredients=$2
  preparation_time=$3
  calories=$4

  echo "Adding meal ($name) to the kitchen..."
  curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\", \"ingredients\":\"$ingredients\", \"preparation_time\":$preparation_time, \"calories\":$calories}" | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "Meal added successfully."
  else
    echo "Failed to add meal."
    exit 1
  fi
}

delete_meal_by_id() {
  meal_id=$1

  echo "Deleting meal by ID ($meal_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal deleted successfully by ID ($meal_id)."
  else
    echo "Failed to delete meal by ID ($meal_id)."
    exit 1
  fi
}

get_all_meals() {
  echo "Getting all meals in the kitchen..."
  response=$(curl -s -X GET "$BASE_URL/get-all-meals")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "All meals retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meals JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meals."
    exit 1
  fi
}

get_meal_by_id() {
  meal_id=$1

  echo "Getting meal by ID ($meal_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by ID ($meal_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (ID $meal_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by ID ($meal_id)."
    exit 1
  fi
}

get_meal_by_name() {
  name=$1

  echo "Getting meal by name ($name)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-name?name=$(echo $name | sed 's/ /%20/g')")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by name."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (by name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by name."
    exit 1
  fi
}

get_random_meal() {
  echo "Getting a random meal from the kitchen..."
  response=$(curl -s -X GET "$BASE_URL/get-random-meal")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Random meal retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Random Meal JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get a random meal."
    exit 1
  fi
}


############################################################
#
# Battle Meal Management
#
############################################################

add_battle_meal() {
  meal_id=$1
  battle_id=$2

  echo "Adding meal ID $meal_id to battle ID $battle_id..."
  response=$(curl -s -X POST "$BASE_URL/add-battle-meal" \
    -H "Content-Type: application/json" \
    -d "{\"meal_id\":$meal_id, \"battle_id\":$battle_id}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal added to battle successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Battle Meal JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to add meal to battle."
    exit 1
  fi
}

remove_battle_meal() {
  battle_meal_id=$1

  echo "Removing battle meal ID ($battle_meal_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/remove-battle-meal/$battle_meal_id")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Battle meal removed successfully."
  else
    echo "Failed to remove battle meal."
    exit 1
  fi
}

get_battle_meals() {
  battle_id=$1

  echo "Getting all battle meals for battle ID ($battle_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-battle-meals/$battle_id")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Battle meals retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Battle Meals JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve battle meals."
    exit 1
  fi
}

get_battle_meal_by_id() {
  battle_meal_id=$1

  echo "Getting battle meal by ID ($battle_meal_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-battle-meal-by-id/$battle_meal_id")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Battle meal retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Battle Meal JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve battle meal."
    exit 1
  fi
}

# Function to start a battle meal session
start_battle_meal() {
  battle_id=$1
  echo "Starting battle meal session for battle ID ($battle_id)..."
  response=$(curl -s -X POST "$BASE_URL/start-battle-meal/$battle_id")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Battle meal session started successfully."
  else
    echo "Failed to start battle meal session."
    exit 1
  fi
}

# Function to end a battle meal session
end_battle_meal() {
  battle_id=$1
  echo "Ending battle meal session for battle ID ($battle_id)..."
  response=$(curl -s -X POST "$BASE_URL/end-battle-meal/$battle_id")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Battle meal session ended successfully."
  else
    echo "Failed to end battle meal session."
    exit 1
  fi
}