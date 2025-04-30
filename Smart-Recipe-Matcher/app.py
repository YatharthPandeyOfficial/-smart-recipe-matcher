import streamlit as st # Import Streamlit to create the web app interface
import requests # Import requests to send API requests


# Inject custom CSS for dark mode + background image
st.markdown("""
    <style>
    body {
        background-image: url('https://images.unsplash.com/photo-1600891964599-f61ba0e24092');
        background-size: cover;
        background-attachment: fixed;
        background-repeat: no-repeat;
        background-position: center;
    }
    .stApp {
        background-color: rgba(0, 0, 0, 0.7);
        padding: 20px;
        border-radius: 10px;
    }
    h1, h2, h3, h4, h5, h6, p, li {
        color: white !important;
    }
    .stButton>button {
        background-color: #00C853;
        color: white;
    }
    a {
        text-decoration: none;
    }
    </style>
""", unsafe_allow_html=True)
 
# Display the app title and description at the top
st.markdown("<h1 style='text-align: center;'>🍽️ Smart Recipe Matcher</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Find meals based on ingredients you already have! 🧂</p>", unsafe_allow_html=True)


# Input section where users can enter ingredients they have
st.subheader("📝 Enter Ingredients You Have")
ingredients_input = st.text_input("Separate with commas (e.g. chicken, rice, onion)", "chicken, rice, onion")


# Function to get meals based on a single ingredient
def get_meals_by_ingredient(ingredient):
    try:
        # API endpoint to get meals based on the ingredient
        url = f"https://www.themealdb.com/api/json/v1/1/filter.php?i={ingredient}"
        res = requests.get(url)  # Send a request to the API
        data = res.json() # Parse the response as JSON
        return data["meals"] if data["meals"] else []  # Return meals or an empty list if no meals are found
    except:
        return [] # Return an empty list if there's an error in the request

# Function to get detailed information for a specific meal by its ID
def get_meal_details(meal_id):
    try:
        # API endpoint to get detailed meal information
        url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}"
        res = requests.get(url)
        return res.json()["meals"][0] if res.json()["meals"] else None
    except:
        return None

# Action when the "Find Recipes" button is clicked
if st.button("🔍 Find Recipes"):
    if ingredients_input.strip() == "":
        st.warning("⚠️ Please enter at least one ingredient.")
    else:
        with st.spinner("🔄 Searching for recipes..."):
            input_ingredients = [i.strip().lower() for i in ingredients_input.split(",")]
            all_meals = {}
            match_count = {}
            seen_meals = set()

            # Loop through each ingredient to search for matching meals
            for ingredient in input_ingredients:
                meals = get_meals_by_ingredient(ingredient)
                for meal in meals:
                    meal_id = meal["idMeal"]
                    if meal_id not in seen_meals:
                        seen_meals.add(meal_id)
                        all_meals[meal_id] = meal
                        match_count[meal_id] = 1
                    else:
                        match_count[meal_id] += 1

            if not all_meals:
                st.error("❌ No recipes found with any of the ingredients.")
            else:
                sorted_meals = sorted(all_meals.items(), key=lambda x: match_count[x[0]], reverse=True)
                st.success(f"✅ Found {len(sorted_meals)} recipe(s) with at least one matching ingredient!")
                
                # Loop through and display each matching meal
                for meal_id, meal in sorted_meals:
                    details = get_meal_details(meal_id)
                    if details:
                        recipe_name = details["strMeal"]
                        recipe_image = details["strMealThumb"]
                        recipe_url = f"https://www.themealdb.com/meal/{meal_id}"
                        matched = match_count[meal_id]

                        recipe_ingredients = []
                        for i in range(1, 21):
                            ing = details.get(f"strIngredient{i}")
                            meas = details.get(f"strMeasure{i}")
                            if ing and ing.strip():
                                recipe_ingredients.append(f"{ing.strip()} - {meas.strip()}")
                        
                        # Identify the ingredients that match the user's input
                        matched_ingredients = [ing for ing in recipe_ingredients if any(i in ing.lower() for i in input_ingredients)]

                        st.markdown("---")
                        col1, col2 = st.columns([1, 1.2])

                        with col1:
                            st.image(recipe_image, width=300)
                            st.markdown(f"<h3 style='color:black; margin-top:10px;'>{recipe_name}</h3>", unsafe_allow_html=True)

                            st.markdown(
                                f"""
                                <a href="{recipe_url}" target="_blank">
                                    <div style="margin-top:10px; padding:10px 15px; background-color:#00C853; color:white; border-radius:10px; text-align:center; font-weight:bold; width:70%;">
                                        🌐 Click here to view full ingredients list
                                    </div>
                                </a>
                                """,
                                unsafe_allow_html=True,
                            )

                        with col2:
                            st.markdown(f"<h4 style='color:#FFD700;'>🧂 Matched Ingredients ({matched})</h4>", unsafe_allow_html=True)
                            for ing in matched_ingredients:
                                st.markdown(f"<li>{ing}</li>", unsafe_allow_html=True)

                            st.markdown("<h4>📋 Instructions (Step-by-Step)</h4>", unsafe_allow_html=True)
                            instructions = details["strInstructions"]
                            
                            # Split the instructions into steps by period and display each step as a separate line
                            steps = instructions.split(". ")
                            for i, step in enumerate(steps, 1):
                                st.markdown(f"**Step {i}:** {step.strip()}") 