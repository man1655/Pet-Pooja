import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from django.http import JsonResponse
import os

def get_ingredient_data(request):
    try:
        # Load Data
        file_path = os.path.join(os.path.dirname(__file__), "Balaji_Fast_Food_Sales_Final_Complete.csv")
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df.dropna(subset=["date"], inplace=True)  # Remove invalid dates
        
        # Extract Time Features
        df["weekday"] = df["date"].dt.day_name()
        df["month"] = df["date"].dt.month
        df["season"] = df["month"].map(lambda x: "Winter" if x in [12,1,2] else 
                                                 "Spring" if x in [3,4,5] else 
                                                 "Summer" if x in [6,7,8] else "Fall")

        # Process Ingredients
        df["Ingredients"] = df["Ingredients"].apply(lambda x: x.split(", ") if isinstance(x, str) else [])
        
        # Aggregate Ingredient Consumption
        ingredient_usage = []
        for _, row in df.iterrows():
            for ingredient in row["Ingredients"]:
                if ingredient.lower() != "seasoning":  # Exclude "seasoning"
                    ingredient_usage.append({"date": row["date"], "ingredient": ingredient, "consumption": row["quantity"]})

        # Convert to DataFrame
        ingredient_df = pd.DataFrame(ingredient_usage)
        if ingredient_df.empty:
            return JsonResponse({"error": "No ingredient data found."}, status=400)

        ingredient_df = ingredient_df.groupby(["date", "ingredient"])["consumption"].sum().unstack().fillna(0)
        
        # Forecast Function
        def forecast_all_ingredients(steps=7):
            forecast_data = {}
            
            for ingredient in ingredient_df.columns:
                data = ingredient_df[ingredient]
                train = data[:-steps]
                
                # Check if sufficient data exists for SARIMAX
                if len(train) < 10:  
                    continue  
                
                try:
                    model = SARIMAX(train, order=(1,1,1), seasonal_order=(1,1,1,7))
                    model_fit = model.fit(disp=False)  # Suppress warnings
                    forecast = model_fit.forecast(steps=steps)
                    
                    forecast_data[ingredient] = forecast.sum()  # Sum for total consumption
                
                except Exception as e:
                    print(f"Error forecasting {ingredient}: {e}")
                    continue
            
            # Convert forecast to DataFrame & Get Top 10 Ingredients
            if not forecast_data:
                return {"error": "No forecast could be generated."}
            
            forecast_df = pd.DataFrame.from_dict(forecast_data, orient='index', columns=['Predicted Consumption'])
            forecast_df = forecast_df.nlargest(10, 'Predicted Consumption')
            return forecast_df

        # Run Forecast
        forecast_df = forecast_all_ingredients(steps=7)

        # Visualization (Optional, Remove If Not Needed)
        plt.figure(figsize=(12, 6))
        plt.bar(forecast_df.index, forecast_df['Predicted Consumption'], color='skyblue')
        plt.xlabel("Ingredients")
        plt.ylabel("Predicted Consumption")
        plt.title("Next Week's Top 10 Ingredient Demand Forecast")
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        for index, value in enumerate(forecast_df['Predicted Consumption']):
            plt.text(index, value + 1, f'{value:.0f}', ha='center', fontsize=10)
        
        plt.show()
        
        return JsonResponse(forecast_df.to_dict())

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
