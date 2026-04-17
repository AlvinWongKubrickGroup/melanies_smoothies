import streamlit as st
from snowflake.snowpark.functions import col
import requests

st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))
fruit_rows = my_dataframe.collect()
fruit_list = [row["FRUIT_NAME"] for row in fruit_rows]

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

if ingredients_list:
    ingredients_string = " ".join(ingredients_list)

    st.write("Your ingredients:", ingredients_string)

    if st.button("Submit Order"):
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders(ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """
        session.sql(my_insert_stmt).collect()
        st.success(f"Your Smoothie is ordered, {name_on_order}!", icon="✅")

st.subheader("Fruit Nutrition Check")

fruit_choice = st.selectbox("Pick a fruit to learn more about:", fruit_list)

if st.button("Get Fruit Info"):
    response = requests.get(
        f"https://my.smoothiefroot.com/api/fruit/{fruit_choice.lower()}"
    )

    if response.status_code == 200:
        st.write(response.json())
    else:
        st.error("Could not fetch fruit information.")
