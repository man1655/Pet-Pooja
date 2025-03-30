import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_percentage_error

# Load Data
df = pd.read_csv("Balaji_Fast_Food_Sales_Final_Complete.csv")
df.columns = df.columns.str.strip()
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df["weekday"] = df["date"].dt.day_name()
df["month"] = df["date"].dt.month
df["season"] = df["month"].map(lambda x: "Winter" if x in [12,1,2] else "Spring" if x in [3,4,5] else "Summer" if x in [6,7,8] else "Fall")

df["Ingredients"] = df["Ingredients"].apply(lambda x: x.split(", ") if isinstance(x, str) else [])

# # Aggregate sales by week and ingredient
# ingredient_usage = []
# for _, row in df.iterrows():
#     for ingredient in row["Ingredients"]:
#         if ingredient.lower() != "seasoning":  # Exclude seasoning
#             ingredient_usage.append({"date": row["date"], "ingredient": ingredient, "consumption": row["quantity"]})

# ingredient_df = pd.DataFrame(ingredient_usage)
# ingredient_df = ingredient_df.groupby(["date", "ingredient"]).sum().unstack().fillna(0)
# ingredient_df.columns = ingredient_df.columns.droplevel()

# def forecast_all_ingredients(steps=7):
#     forecast_data = {}
    
#     for ingredient in ingredient_df.columns:
#         data = ingredient_df[ingredient]
#         train = data[:-steps]
        
#         model = SARIMAX(train, order=(1,1,1), seasonal_order=(1,1,1,7))
#         model_fit = model.fit()
#         forecast = model_fit.forecast(steps=steps)
        
#         forecast_data[ingredient] = forecast.sum()
    
#     # Convert forecast data to DataFrame
#     forecast_df = pd.DataFrame.from_dict(forecast_data, orient='index', columns=['Predicted Consumption'])
#     forecast_df = forecast_df.nlargest(10, 'Predicted Consumption')  # Top 10 ingredients
    
#     # Plot bar chart
#     plt.figure(figsize=(12, 6))
#     plt.bar(forecast_df.index, forecast_df['Predicted Consumption'], color='skyblue')
    
#     plt.xlabel("Ingredients")
#     plt.ylabel("Predicted Consumption")
#     plt.title("Next Week's Top 10 Ingredient Demand Forecast")
#     plt.xticks(rotation=45, ha='right')
#     plt.grid(axis='y', linestyle='--', alpha=0.7)
    
#     for index, value in enumerate(forecast_df['Predicted Consumption']):
#         plt.text(index, value + 1, f'{value:.0f}', ha='center', fontsize=10)
    
    # plt.show()

print(df.columns)


# print(df.groupby([df['item_name'] , df['weekday']]).agg({'quantity' : 'sum'}))

# Example Usage
# forecast_all_ingredients()


# Load CSV file
import pandas as pd

# Load the CSV file
file_path = "Balaji_Fast_Food_Sales_Final_Complete.csv"
df = pd.read_csv(file_path)

# Convert 'date' column to datetime format
df['date'] = pd.to_datetime(df['date'])

# Sort dataset by date in descending order
df = df.sort_values(by='date', ascending=False)

# Get the last 7 unique dates
last_7_dates = df['date'].drop_duplicates().head(7)

# Filter data for the last 7 unique dates
df_last_7_days = df[df['date'].isin(last_7_dates)]

# Group by 'item_name' and sum the 'quantity' sold
item_sales_last_7_days = df_last_7_days.groupby('item_name')['quantity'].sum()

# Get the two most sold items
most_sold_last_7 = item_sales_last_7_days.nlargest(2)

# Get the two least sold items
least_sold_last_7 = item_sales_last_7_days.nsmallest(2)
data=dict(most_sold_last_7)
# Display results
print(data['Panipuri'])
print("Most Sold Items in Last 7 Unique Days:\n",)
print("\nLeast Sold Items in Last 7 Unique Days:\n", least_sold_last_7)