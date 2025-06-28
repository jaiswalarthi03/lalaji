"""
Meet Lalaji Inventory LLM Integration
Specialized LLM integration for inventory management operations
"""

import time
import requests
from config import TOGETHER_API_KEY, GEMINI_API_KEY

API_URL = "https://api.together.xyz/v1/chat/completions"
IMG_URL = "https://api.together.xyz/v1/images/generations"
GEMINI_CHAT_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}" if GEMINI_API_KEY else None
GEMINI_EMBED_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-exp-03-07:embedContent?key={GEMINI_API_KEY}" if GEMINI_API_KEY else None

# Inventory-specific chat models
INVENTORY_CHAT_MODELS = [
    ("meta-llama/Llama-3.3-70B-Instruct-Turbo-Free", "Llama 3.3 70B Turbo Free (Together)"),
    ("lgai/exaone-3-5-32b-instruct", "Exaone 3.5 32B Instruct (Together)"),
    ("lgai/exaone-deep-32b", "Exaone Deep 32B (Together)"),
    ("deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free", "DeepSeek R1 Distill Llama 70B Free (Together)"),
    ("meta-llama/Llama-Vision-Free", "Llama Vision Free (Together)"),
    ("arcee-ai/AFM-4.5B-Preview", "AFM 4.5B Preview (Together)"),
    ("gemini", "Google Gemini 2.0 Flash (Gemini)")
]

# Product image generation models
PRODUCT_IMG_MODELS = [
    ("black-forest-labs/FLUX.1-schnell-Free", "FLUX.1 Schnell Free (Together)"),
]

class InventoryTogetherLLM:
    """Together AI LLM integration for inventory management operations."""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or TOGETHER_API_KEY
        if not self.api_key or self.api_key.startswith("your-"):
            raise ValueError("TOGETHER_API_KEY not set in config.py.")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def analyze_inventory(self, model, inventory_data):
        """Analyze inventory data and provide insights."""
        prompt = f"""
        Analyze the following inventory data for Meet Lalaji and provide insights:
        
        {inventory_data}
        
        Please provide:
        1. Stock level analysis
        2. Reorder recommendations
        3. Demand forecasting insights
        4. Seasonal pattern identification
        5. Pricing optimization suggestions
        """
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }
        
        try:
            resp = requests.post(API_URL, headers=self.headers, json=data)
            if resp.status_code == 429:
                print("Rate limit hit. Waiting 10 seconds...")
                time.sleep(10)
                return self.analyze_inventory(model, inventory_data)
            resp.raise_for_status()
            result = resp.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error analyzing inventory: {e}"

    def generate_reorder_recommendations(self, model, stock_data):
        """Generate reorder recommendations based on stock data."""
        prompt = f"""
        Based on the following stock data for Meet Lalaji, generate reorder recommendations:
        
        {stock_data}
        
        Please provide:
        1. Products requiring immediate reorder
        2. Optimal reorder quantities
        3. Recommended suppliers
        4. Expected delivery timelines
        5. Cost implications
        """
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }
        
        try:
            resp = requests.post(API_URL, headers=self.headers, json=data)
            if resp.status_code == 429:
                print("Rate limit hit. Waiting 10 seconds...")
                time.sleep(10)
                return self.generate_reorder_recommendations(model, stock_data)
            resp.raise_for_status()
            result = resp.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error generating reorder recommendations: {e}"

    def forecast_demand(self, model, historical_data):
        """Forecast demand based on historical data."""
        prompt = f"""
        Analyze the following historical sales data for Meet Lalaji and forecast future demand:
        
        {historical_data}
        
        Please provide:
        1. Demand forecasting for next 3 months
        2. Seasonal pattern analysis
        3. Trend identification
        4. Confidence intervals
        5. Inventory planning recommendations
        """
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }
        
        try:
            resp = requests.post(API_URL, headers=self.headers, json=data)
            if resp.status_code == 429:
                print("Rate limit hit. Waiting 10 seconds...")
                time.sleep(10)
                return self.forecast_demand(model, historical_data)
            resp.raise_for_status()
            result = resp.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Error forecasting demand: {e}"

    def generate_product_image(self, model, product_description):
        """Generate product images for inventory catalog."""
        data = {
            "model": model,
            "prompt": f"Professional product image for inventory catalog: {product_description}"
        }
        try:
            resp = requests.post(IMG_URL, headers=self.headers, json=data)
            if resp.status_code == 429:
                print("Rate limit hit. Waiting 10 seconds...")
                time.sleep(10)
                return self.generate_product_image(model, product_description)
            resp.raise_for_status()
            result = resp.json()
            return result.get("data", [{}])[0].get("url", "No image URL returned.")
        except Exception as e:
            return f"Error generating product image: {e}"

class InventoryGeminiLLM:
    """Google Gemini LLM integration for inventory management operations."""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or GEMINI_API_KEY
        if not self.api_key or self.api_key.startswith("your-"):
            raise ValueError("GEMINI_API_KEY not set in config.py.")
        self.chat_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}"
        self.embed_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-exp-03-07:embedContent?key={self.api_key}"
        self.headers = {"Content-Type": "application/json"}

    def analyze_inventory(self, inventory_data):
        """Analyze inventory data using Gemini."""
        prompt = f"""
        Analyze the following inventory data for Meet Lalaji and provide comprehensive insights:
        
        {inventory_data}
        
        Please provide:
        1. Stock level analysis and reorder point assessment
        2. Demand forecasting and seasonal pattern identification
        3. Pricing optimization recommendations
        4. Supplier performance analysis
        5. Inventory turnover and efficiency metrics
        """
        
        data = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ]
        }
        
        try:
            resp = requests.post(self.chat_url, headers=self.headers, json=data)
            if resp.status_code == 429:
                print("Gemini rate limit hit. Waiting 10 seconds...")
                time.sleep(10)
                return self.analyze_inventory(inventory_data)
            resp.raise_for_status()
            result = resp.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"Error analyzing inventory with Gemini: {e}"

    def generate_reorder_recommendations(self, stock_data):
        """Generate reorder recommendations using Gemini."""
        prompt = f"""
        Based on the following stock data for Meet Lalaji, generate detailed reorder recommendations:
        
        {stock_data}
        
        Please provide:
        1. Products requiring immediate reorder with urgency levels
        2. Optimal reorder quantities based on EOQ calculations
        3. Recommended suppliers with pricing and availability
        4. Expected delivery timelines and lead time analysis
        5. Cost implications and budget impact
        """
        
        data = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ]
        }
        
        try:
            resp = requests.post(self.chat_url, headers=self.headers, json=data)
            if resp.status_code == 429:
                print("Gemini rate limit hit. Waiting 10 seconds...")
                time.sleep(10)
                return self.generate_reorder_recommendations(stock_data)
            resp.raise_for_status()
            result = resp.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"Error generating reorder recommendations with Gemini: {e}"

    def forecast_demand(self, historical_data):
        """Forecast demand using Gemini."""
        prompt = f"""
        Analyze the following historical sales data for Meet Lalaji and provide demand forecasting:
        
        {historical_data}
        
        Please provide:
        1. Demand forecasting for next 3-6 months with confidence intervals
        2. Seasonal pattern analysis and trend identification
        3. Product category performance analysis
        4. Market condition impact assessment
        5. Inventory planning and procurement recommendations
        """
        
        data = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ]
        }
        
        try:
            resp = requests.post(self.chat_url, headers=self.headers, json=data)
            if resp.status_code == 429:
                print("Gemini rate limit hit. Waiting 10 seconds...")
                time.sleep(10)
                return self.forecast_demand(historical_data)
            resp.raise_for_status()
            result = resp.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"Error forecasting demand with Gemini: {e}"

    def embed_inventory_data(self, text, task_type=None):
        """Embed inventory data for similarity search and analysis."""
        data = {
            "model": "models/gemini-embedding-exp-03-07",
            "content": {"parts": [{"text": text}]}
        }
        if task_type:
            data["taskType"] = task_type
        try:
            resp = requests.post(self.embed_url, headers=self.headers, json=data)
            if resp.status_code == 429:
                print("Gemini embedding rate limit hit. Waiting 10 seconds...")
                time.sleep(10)
                return self.embed_inventory_data(text, task_type)
            resp.raise_for_status()
            result = resp.json()
            return result.get("embedding", result)
        except Exception as e:
            return f"Error embedding inventory data with Gemini: {e}"

def main():
    print("\n=== Meet Lalaji Inventory LLM Demo ===")
    print("Select an inventory management task:")
    print("1. Analyze Inventory Data")
    print("2. Generate Reorder Recommendations")
    print("3. Forecast Demand")
    print("4. Generate Product Images")
    print("5. Embed Inventory Data")
    
    try:
        choice = int(input("Enter your choice: "))
    except ValueError:
        print("Invalid input.")
        return
    
    if choice == 1:
        print("\n=== Inventory Analysis ===")
        for i, (_, name) in enumerate(INVENTORY_CHAT_MODELS, 1):
            print(f"{i}. {name}")
        
        try:
            model_choice = int(input("Select model: "))
            if 1 <= model_choice <= len(INVENTORY_CHAT_MODELS):
                model, name = INVENTORY_CHAT_MODELS[model_choice-1]
                
                # Sample inventory data
                inventory_data = """
                Product: Lotte Chocopie
                Current Stock: 15 units
                Reorder Point: 20 units
                Daily Demand: 3 units
                Lead Time: 7 days
                Supplier: ABC Foods
                Cost: $3.20 per unit
                """
                
                if model == "gemini":
                    llm = InventoryGeminiLLM()
                    print("Analyzing inventory with Gemini...")
                    response = llm.analyze_inventory(inventory_data)
                else:
                    llm = InventoryTogetherLLM()
                    print(f"Analyzing inventory with {name}...")
                    response = llm.analyze_inventory(model, inventory_data)
                
                print(f"\nAnalysis Result:\n{response}")
            else:
                print("Invalid model choice.")
        except Exception as e:
            print(f"Error: {e}")
    
    elif choice == 2:
        print("\n=== Reorder Recommendations ===")
        # Sample stock data
        stock_data = """
        Product: Tata Salt
        Current Stock: 8 units
        Reorder Point: 15 units
        Safety Stock: 5 units
        Daily Demand: 2 units
        Lead Time: 5 days
        """
        
        try:
            llm = InventoryGeminiLLM()
            print("Generating reorder recommendations with Gemini...")
            response = llm.generate_reorder_recommendations(stock_data)
            print(f"\nRecommendations:\n{response}")
        except Exception as e:
            print(f"Error: {e}")
    
    elif choice == 3:
        print("\n=== Demand Forecasting ===")
        # Sample historical data
        historical_data = """
        Product: Basmati Rice (1kg)
        Jan: 120 units sold
        Feb: 135 units sold
        Mar: 150 units sold
        Apr: 140 units sold
        May: 160 units sold
        Jun: 175 units sold
        """
        
        try:
            llm = InventoryGeminiLLM()
            print("Forecasting demand with Gemini...")
            response = llm.forecast_demand(historical_data)
            print(f"\nForecast:\n{response}")
        except Exception as e:
            print(f"Error: {e}")
    
    elif choice == 4:
        print("\n=== Product Image Generation ===")
        model, name = PRODUCT_IMG_MODELS[0]
        product_description = input("Enter product description for image generation: ")
        
        try:
            llm = InventoryTogetherLLM()
            print("Generating product image...")
            url = llm.generate_product_image(model, product_description)
            print(f"\nProduct Image URL: {url}")
        except Exception as e:
            print(f"Error: {e}")
    
    elif choice == 5:
        print("\n=== Inventory Data Embedding ===")
        text = input("Enter inventory data to embed: ")
        task_type = input("Optional: Enter embedding task type (or leave blank): ") or None
        
        try:
            llm = InventoryGeminiLLM()
            print("Embedding inventory data with Gemini...")
            embedding = llm.embed_inventory_data(text, task_type)
            print(f"\nEmbedding: {embedding}")
        except Exception as e:
            print(f"Error: {e}")
    
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main() 