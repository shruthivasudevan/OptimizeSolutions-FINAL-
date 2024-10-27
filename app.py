from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import date
from typing import Optional
from main import trade_decision

# Create the FastAPI instance
app = FastAPI()

# Allow CORS for the frontend (React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model to validate incoming request data
class OptionFormData(BaseModel):
    strategy: str
    stockIndex: str
    startDate: date
    endDate: date
    expiryDate: date

# POST endpoint to handle form submission
@app.post("/api/submit")
async def submit_option_data(form_data: OptionFormData):
    try:

        # Print the incoming request data
        print("Received request data:", form_data.model_dump)

        # Extract data from the request body (validated by Pydantic)
        strategy = form_data.strategy
        underlying_stock = form_data.stockIndex.upper()
        start_date = form_data.startDate.strftime("%d-%m-%Y")
        end_date = form_data.endDate.strftime("%d-%m-%Y")
        expiry_date = form_data.expiryDate.strftime("%d-%b-%Y").upper()

        #print(start_date, end_date, expiry_date)

        result = trade_decision(strategy, underlying_stock, start_date, end_date, expiry_date)

        # Example calculation (you can replace this with actual logic)
        """ contracts_to_buy = 15  # Mock data
        break_even_price = 1400.75  # Mock data
        maximum_profit = 7500  # Mock data
        maximum_loss = 2500 """  # Mock data

        # Return the calculated data as JSON response
        return {
            "contractsToBuy": 25,  # Mock data
            "breakEvenPrice": result.break_even,
            "maximumProfit": result.max_profit,
            "maximumLoss": result.max_loss
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Start the FastAPI app using Uvicorn if run as the main script
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)