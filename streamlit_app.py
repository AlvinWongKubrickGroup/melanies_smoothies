import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# -----------------------------
# Name on order
# -----------------------------
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# -----------------------------
# Snowflake connection
# -----------------------------
cnx = st.connection("snowflake")
session = cnx.session()

# -----------------------------
# Get fruit options from Snowflake
# -----------------------------
fruit_table = (
    session.table("smoothies.public.fruit_options")
    .select(col("FRUIT_NAME"))
)

fruit_rows = fruit_table.collect()
fruit_list = [row["FRUIT_NAME"] for row in fruit_rows]

# -----------------------------
# Choose ingredients
# -----------------------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# -----------------------------
# Submit smoothie order
# -----------------------------
if ingredients_list:
    ingredients_string = " ".join(ingredients_list)
    st.write("Your ingredients:", ingredients_string)

    submit_order = st.button("Submit Order")

    if submit_order:
        insert_stmt = f"""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """
        session.sql(insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")

# -----------------------------
# SmoothieFruit nutrition section
# -----------------------------
st.subheader("SmoothieFruit Nutrition Information")

fruit_choice = st.selectbox(
    "Choose a fruit to see its nutrition information:",
    fruit_list
)

if st.button("Get Fruit Info"):
    smoothiefroot_response = requests.get(
        f"https://my.smoothiefroot.com/api/fruit/{fruit_choice.lower()}"
    )

    if smoothiefroot_response.status_code == 200:
        smoothiefroot_json = smoothiefroot_response.json()

        # Show formatted JSON
        st.json(smoothiefroot_json)

        # Convert nutrition data into a dataframe
        nutrition_rows = []

        for nutrient_name, nutrient_value in smoothiefroot_json["nutrition"].items():
            nutrition_rows.append(
                {
                    "family": smoothiefroot_json["family"],
                    "genus": smoothiefroot_json["genus"],
                    "id": smoothiefroot_json["id"],
                    "name": smoothiefroot_json["name"],
                    "nutrition": nutrient_name,
                    "value": nutrient_value,
                    "order": smoothiefroot_json["order"]
                }
            )

        sf_df = pd.DataFrame(nutrition_rows)
        st.dataframe(sf_df, use_container_width=True)

    else:
        st.error("Failed to get fruit information from the API.")
