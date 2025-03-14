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
from parse_13F import SEC13FParser

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

def get_quarter_info() -> tuple[str, str, str]:
    """Get current quarter info and SEC index URL"""
    now = datetime.now()
    year = now.year
    month = now.month
    
    if month <= 3:
        report_quarter = f"12-31-{year-1}"
        current_quarter = f"03-31-{year}"
        url = f"https://www.sec.gov/Archives/edgar/daily-index/{year}/QTR1/index.html"
    elif month <= 6:
        report_quarter = f"03-31-{year}"
        current_quarter = f"06-30-{year}"
        url = f"https://www.sec.gov/Archives/edgar/daily-index/{year}/QTR2/index.html"
    elif month <= 9:
        report_quarter = f"06-30-{year}"
        current_quarter = f"09-30-{year}"
        url = f"https://www.sec.gov/Archives/edgar/daily-index/{year}/QTR3/index.html"
    else:
        report_quarter = f"09-30-{year}"
        current_quarter = f"12-31-{year}"
        url = f"https://www.sec.gov/Archives/edgar/daily-index/{year}/QTR4/index.html"
    
    return report_quarter, current_quarter, url

@app.get("/update_13F_data")
async def update_13F_data(
    report_quarter: Optional[str] = Query(None),
    force_update: bool = Query(False)
):
    """Update 13F holdings data for specified quarter or current quarter"""
    try:
        if report_quarter is None:
            report_quarter, current_quarter, sec_url = get_quarter_info()
            print(f"Updating for quarter {report_quarter}")
        else:
            # Calculate current quarter based on report quarter
            date_parts = report_quarter.split('-')
            year = int(date_parts[2])
            month = int(date_parts[0])
            
            # Current quarter is the next quarter after report quarter
            if month == 12:  # If December, move to next year Q1
                current_quarter = f"03-31-{year + 1}"
                quarter = 1
                year = year + 1
            else:
                next_month = ((month + 3) // 3) * 3  # Round to next quarter end
                current_quarter = f"{str(next_month).zfill(2)}-30-{year}"
                quarter = (month + 2) // 3
            
            sec_url = f"https://www.sec.gov/Archives/edgar/daily-index/{year}/QTR{quarter}/index.html"
            print(f"Using quarter {current_quarter}, URL: {sec_url}")

        logger.info(f"Starting 13F update for quarter {report_quarter}")
        logger.info(f"Parsing URLs from {sec_url}")
        
        # Check if we already have data for this quarter
        if not force_update:
            with DBSession() as session:
                existing_data = session.query(InstitutionalHolding).filter_by(quarter=str(quarter)).first()
                if existing_data:
                    logger.info(f"Data already exists for quarter {report_quarter}. Skipping update.")
                    return {"message": f"Data already exists for quarter {report_quarter}"}

        parser = SEC13FParser(target_quarter=str(report_quarter), current_quarter=str(current_quarter))
        logger.info("Parser initialized")
        parser.load_company_mappings()
        logger.info("Company mappings loaded")
        parser.process_index_page(sec_url)
        logger.info("Index page processed")
        parser.cleanup()
        logger.info("Cleanup complete")
        
        logger.info(f"Completed 13F update for quarter {report_quarter}")
        return {"message": f"Successfully updated 13F data for quarter {report_quarter}"}
        
    except Exception as e:
        logger.error(f"Error updating 13F data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# def schedule_13F_updates():
#     """Schedule quarterly 13F updates"""
#     # Schedule updates to run on the 45th day after quarter end (typical 13F filing deadline)
#     scheduler.add_job(
#         update_13F_data,
#         CronTrigger(
#             month='2,5,8,11',  # February, May, August, November
#             day='14',          # 45 days after quarter end
#             hour='0',
#             minute='0',
#             timezone=pytz.UTC
#         ),
#         id='quarterly_13F_update'
#     )

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
    try:
        # Initial data update
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

        # Start the scheduler
        scheduler.start()
        
        # # Schedule 13F updates
        # schedule_13F_updates()
        
        # # Check if we need to run an initial 13F update
        # report_quarter, current_quarter, _ = get_quarter_info()
        # await update_13F_data(report_quarter, current_quarter)
        
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise

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
    """Get all available tickers"""
    try:
        tickers = db.get_tickers()
        return {"tickers": tickers}
    except Exception as e:
        logger.error(f"Error fetching tickers: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch tickers")

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

# @app.get("/update_13F/{quarter}")
# async def manual_13F_update(quarter: str, background_tasks: BackgroundTasks, force: bool = False):
#     """
#     Manually trigger 13F update for a specific quarter
#     Quarter format: MM-DD-YYYY (e.g., 12-31-2024)
#     """
#     background_tasks.add_task(update_13F_data, quarter, force)
#     return {"message": f"Started 13F update for quarter {quarter}"}

@app.get("/holdings/{ticker}")
async def get_holdings(
    ticker: str,
    quarter: Optional[str] = Query(None)
):
    """Get institutional holdings for a specific ticker and quarter"""
    try:
        with DBSession() as session:
            query = session.query(InstitutionalHolding).filter_by(company_ticker=ticker)
            
            if quarter:
                # Convert MM-DD-YYYY to Q#-YYYY format
                date_parts = quarter.split('-')
                month = int(date_parts[0])
                year = date_parts[2]
                q_num = ((month - 1) // 3) + 1
                formatted_quarter = f"Q{q_num}-{year}"
                query = query.filter_by(quarter=formatted_quarter)
            
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
    except Exception as e:
        logger.error(f"Error fetching holdings for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)