from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import database as db
from models import MeasurementPeriodEnum
from typing import List, Optional
from datetime import date, datetime, timedelta
from pydantic import BaseModel
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz


# Allow CORS for your frontend URL
origins = [
    "http://localhost:3000",  # Frontend URL
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow requests from these origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Initialize the scheduler
scheduler = BackgroundScheduler()

# Define Pydantic models for request validation
class UpdateStockDataRequest(BaseModel):
    symbols: str  # comma-separated list of stock symbols
    index: Optional[str] = None
    days: Optional[int] = 60

async def update_all_universe_data():
    """
    Update stock and index data for all tickers in the universe
    """
    try:
        # Get all universes
        universes = db.get_universes()
        if not universes:
            print("No universes found")
            return

        # Collect all unique tickers and indices
        all_tickers = set()
        indices = {'^GSPC', '^IXIC', '^DJI'}  # Add any other indices you want to track

        for universe in universes:
            all_tickers.update(universe['tickers'])

        # Update stock data for all tickers
        if all_tickers:
            ticker_str = ','.join(all_tickers)
            await update_stock_data(UpdateStockDataRequest(
                symbols=ticker_str,
                days=2  # Only update recent data for daily updates
            ))

        # Update index data
        index_str = ','.join(indices)
        await update_stock_data(UpdateStockDataRequest(
            symbols=index_str,
            days=2  # Only update recent data for daily updates
        ))

        print(f"Successfully updated data for {len(all_tickers)} stocks and {len(indices)} indices at {datetime.now()}")
    except Exception as e:
        print(f"Error updating universe data: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """
    Run when the FastAPI application starts
    """
    # Initial update with more historical data
    try:
        print("Performing initial data update...")
        universes = db.get_universes()
        if universes:
            all_tickers = set()
            indices = {'^GSPC', '^IXIC', '^DJI'}

            for universe in universes:
                all_tickers.update(universe['tickers'])

            # Update stock data with 60 days of history
            if all_tickers:
                ticker_str = ','.join(all_tickers)
                await update_stock_data(UpdateStockDataRequest(
                    symbols=ticker_str,
                    days=60
                ))

            # Update index data with 60 days of history
            index_str = ','.join(indices)
            await update_stock_data(UpdateStockDataRequest(
                symbols=index_str,
                days=60
            ))
    except Exception as e:
        print(f"Error during startup data update: {str(e)}")

    # Schedule daily updates at market close (4:00 PM Eastern Time)
    scheduler.add_job(
        update_all_universe_data,
        trigger=CronTrigger(
            hour=16,  # 4 PM
            minute=0,
            timezone=pytz.timezone('America/New_York')
        )
    )
    scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    """
    Run when the FastAPI application shuts down
    """
    scheduler.shutdown()

@app.get("/")
async def read_root():
    return {"message": "Hello, FastAPI with PostgreSQL!"}

@app.get("/tickers")
async def read_tickers():
    tickers = db.get_tickers()
    return {"tickers": tickers}


@app.post("/create_universe")
async def create_universe(body: db.CreateUniverseRequestBody):
    print(body)
    universe = db.post_create_universe(body)
    return {"universe": universe}


@app.get("/get_universes")
async def read_universes():
    universes = db.get_universes()
    return {"universes": universes}


@app.put("/edit_universe/{universe_id}")
def edit_universe(universe_id: int, body: db.EditUniverseRequestBody):
  universe = db.update_universe(universe_id, body)
  return {"universe": universe}


@app.get("/measurement_periods", response_model=List[int])
async def get_measurement_periods():
    """
    Return the allowed measurement period values as a list of integers
    """
    return [period.value for period in MeasurementPeriodEnum]


@app.delete("/delete_universes")
async def delete_universes(body: db.DeleteUniverseRequestBody):
    """
    Delete a set of universes based on the list of universe_ids provided.
    """
    db.delete_universes(body)
    return {"message": "Universes deleted successfully", "deleted_ids": body.universe_ids}

# sample query: http://your-domain.com/get_short_interest?ticker=AAPL&start_date=2024-01-01&end_date=2024-02-01
@app.get("/get_short_interest") #, response_model=list[db.ShortInterestResponse])
async def get_short_interest(
    tickers: str,
    start_date: date = Query(..., description="Start of date range"),
    end_date: date = Query(..., description="End of date range"),
):
    ticker_list = tickers.split(',')
    short_interest = db.get_short_interest_for_tickers(ticker_list, start_date, end_date)
    return {'short_interest': short_interest}

# New endpoints for stock price data

@app.post("/update_stock_data")
async def update_stock_data(data: UpdateStockDataRequest):
    """
    Update stock price data for the given symbols.
    
    Parameters:
    - symbols: Comma-separated list of stock symbols
    - index: Optional index symbol (e.g., '^IXIC' for NASDAQ)
    - days: Number of days of historical data to fetch (default: 60)
    """
    symbols = [s.strip() for s in data.symbols.split(',')]
    result = db.update_stock_data(symbols=symbols, index=data.index, days=data.days)
    return result

@app.get("/stock_volatility")
async def get_stock_volatility(
    symbol: str = Query(..., description="Stock symbol (e.g., 'AAPL')"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)")
):
    """
    Calculate volatility metrics for a stock.
    
    Parameters:
    - symbol: Stock symbol
    - start_date: Optional start date 
    - end_date: Optional end date
    """
    result = db.calculate_stock_volatility(
        stock_symbol=symbol,
        start_date=start_date,
        end_date=end_date
    )
    return result

@app.get("/stock_correlation")
async def get_stock_correlation(
    symbol: str = Query(..., description="Stock symbol (e.g., 'AAPL')"),
    index: str = Query(..., description="Index symbol (e.g., '^IXIC')"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)")
):
    """
    Calculate correlation between a stock and an index.
    
    Parameters:
    - symbol: Stock symbol
    - index: Index symbol
    - start_date: Optional start date 
    - end_date: Optional end date
    """
    result = db.calculate_stock_correlation(
        stock_symbol=symbol,
        index=index,
        start_date=start_date,
        end_date=end_date
    )
    return result

@app.route('/api/volatility', methods=['GET'])
def get_volatility():
    try:
        symbol = request.args.get('symbol')
        start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d')
        end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d')
        
        if not symbol or not start_date or not end_date:
            return jsonify({'error': 'Missing required parameters'}), 400
        
        volatility = calculate_volatility(symbol, start_date, end_date)
        if volatility is None:
            return jsonify({'error': f'No data found for symbol {symbol}'}), 404
            
        return jsonify({'volatility': volatility})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/correlation', methods=['GET'])
def get_correlation():
    try:
        symbol1 = request.args.get('symbol1')
        symbol2 = request.args.get('symbol2')
        start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d')
        end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d')
        
        if not symbol1 or not symbol2 or not start_date or not end_date:
            return jsonify({'error': 'Missing required parameters'}), 400
            
        correlation = calculate_correlation(symbol1, symbol2, start_date, end_date)
        if correlation is None:
            return jsonify({'error': f'Insufficient data for correlation between {symbol1} and {symbol2}'}), 404
            
        return jsonify({'correlation': correlation})
    except Exception as e:
        return jsonify({'error': str(e)}), 500