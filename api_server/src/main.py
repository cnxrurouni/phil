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
import logging
from pathlib import Path

from Company import InstitutionalHolding, Session as DBSession
from src.13f_parser import SEC13FParser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def get_quarter_info() -> tuple[str, str]:
    """Get current quarter info and SEC index URL"""
    now = datetime.now()
    year = now.year
    month = now.month
    
    if month <= 3:
        quarter = f"12-31-{year-1}"
        url = f"https://www.sec.gov/Archives/edgar/daily-index/{year}/QTR1/index.html"
    elif month <= 6:
        quarter = f"03-31-{year}"
        url = f"https://www.sec.gov/Archives/edgar/daily-index/{year}/QTR2/index.html"
    elif month <= 9:
        quarter = f"06-30-{year}"
        url = f"https://www.sec.gov/Archives/edgar/daily-index/{year}/QTR3/index.html"
    else:
        quarter = f"09-30-{year}"
        url = f"https://www.sec.gov/Archives/edgar/daily-index/{year}/QTR4/index.html"
    
    return quarter, url

async def update_13f_data(quarter: Optional[str] = None, force_update: bool = False):
    """Update 13F holdings data for specified quarter or current quarter"""
    try:
        if quarter is None:
            quarter, sec_url = get_quarter_info()
        else:
            # Determine URL based on provided quarter
            date_parts = quarter.split('-')
            year = date_parts[2]
            month = int(date_parts[0])
            qtr = (month // 3) + 1
            sec_url = f"https://www.sec.gov/Archives/edgar/daily-index/{year}/QTR{qtr}/index.html"

        logger.info(f"Starting 13F update for quarter {quarter}")
        
        # Check if we already have data for this quarter
        if not force_update:
            with DBSession() as session:
                existing_data = session.query(InstitutionalHolding).filter_by(quarter=quarter).first()
                if existing_data:
                    logger.info(f"Data already exists for quarter {quarter}. Skipping update.")
                    return

        parser = SEC13FParser(target_quarter=quarter)
        parser.load_company_mappings()
        parser.process_index_page(sec_url)
        parser.cleanup()
        
        logger.info(f"Completed 13F update for quarter {quarter}")
        
    except Exception as e:
        logger.error(f"Error updating 13F data: {e}")
        raise

def schedule_13f_updates():
    """Schedule quarterly 13F updates"""
    # Schedule updates to run on the 45th day after quarter end (typical 13F filing deadline)
    scheduler.add_job(
        update_13f_data,
        CronTrigger(
            month='2,5,8,11',  # February, May, August, November
            day='14',          # 45 days after quarter end
            hour='0',
            minute='0',
            timezone=pytz.UTC
        ),
        id='quarterly_13f_update'
    )

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
    schedule_13f_updates()
    
    # Check if we need to run an initial update
    quarter, _ = get_quarter_info()
    with DBSession() as session:
        existing_data = session.query(InstitutionalHolding).filter_by(quarter=quarter).first()
        if not existing_data:
            await update_13f_data(quarter)

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

@app.get("/update_13f/{quarter}")
async def manual_13f_update(quarter: str, background_tasks: BackgroundTasks, force: bool = False):
    """
    Manually trigger 13F update for a specific quarter
    Quarter format: MM-DD-YYYY (e.g., 12-31-2024)
    """
    background_tasks.add_task(update_13f_data, quarter, force)
    return {"message": f"Started 13F update for quarter {quarter}"}

@app.get("/holdings/{ticker}")
async def get_holdings(ticker: str, quarter: Optional[str] = None):
    """Get institutional holdings for a specific ticker"""
    with DBSession() as session:
        query = session.query(InstitutionalHolding).filter_by(company_ticker=ticker)
        if quarter:
            query = query.filter_by(quarter=quarter)
        holdings = query.all()
        
        return {
            "ticker": ticker,
            "quarter": quarter or "all",
            "holdings": [
                {
                    "holder_name": h.holder_name,
                    "shares": h.shares,
                    "filing_date": h.filing_date.isoformat(),
                    "quarter": h.quarter
                }
                for h in holdings
            ]
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)