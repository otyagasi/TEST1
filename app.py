from flask import Flask, render_template, request
import requests

app = Flask(__name__)

API_KEY = "yBXTCXZtKRIPO5u6d2tualQhcFxhPx4ceCacXlYi"
SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"


TARGET_NUTRIENTS = {
  "Energy": "カロリー",
  "Protein": "タンパク質",
  "fat": "脂質",
  "Carbohydrate": "炭水化物",
  "Sugars, total including NLEA": "糖質"
}

@app.route("/", methods=["GET","POST"])
def index():
  results = []
  if request.method == "POST":
    query = request.form.get("query")
    if query:
      params = {
        "api_key": API_KEY,
        "query": query,
        "pageSize": 5
      }
      response = requests.get(SEARCH_URL, params=params)
      if response.status_code == 200:
        data = response.json()
        foods = data.get("foods", [])

        for food in foods:
          nutrients = food.get("foodNutrients", [])
          nutrition_info = {}

          for nutrient in nutrients:
            name = nutrient.get("nutrientName", "不明")
            amount = nutrient.get("value", "不明")
            unit = nutrient.get("unitName", "")

            if name in TARGET_NUTRIENTS:
              nutrition_info[TARGET_NUTRIENTS[name]] = f"{amount} {unit}"

          results.append({
            "description": food.get("description", "名称不明"),
            "nutrients": nutrition_info
          })
      else:
        results = [{"description": "エラーが発生しました", "nutrients": {}}]

  return render_template("index.html", results=results)
  
if __name__ == "__main__":
  app.run(debug=True)
