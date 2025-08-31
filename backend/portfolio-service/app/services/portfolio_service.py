# app/services/portfolio_service.py

from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import numpy as np
from datetime import datetime, timezone, timedelta

from app.models.portfolio import Portfolio
from app.models.holding import Holding
from app.models.transaction import Transaction
from app.schemas.portfolio import PortfolioCreate, PortfolioUpdate, PortfolioSummary, PortfolioMetrics
from app.schemas.holding import HoldingCreate, HoldingUpdate
from app.schemas.transaction import TransactionCreate
from app.services.market_data_service import market_data_service
from app.utils.calculations import PortfolioCalculations

class PortfolioService:
    """
    Portfolio service with database-first approach and graceful degradation
    """

    def __init__(self, db: Session):
        self.db = db
        self.calculations = PortfolioCalculations()

    async def create_portfolio(self, user_id: int, portfolio_data: PortfolioCreate) -> Portfolio:
        """Create a new portfolio for user"""
        db_portfolio = Portfolio(
            user_id=user_id,
            name=portfolio_data.name,
            description=portfolio_data.description,
            # Initialize calculated fields
            total_value=0.0,
            total_cost=0.0,
            total_return=0.0,
            total_return_percent=0.0,
            day_change=0.0,
            day_change_percent=0.0,
            dividend_income=0.0
        )
        
        self.db.add(db_portfolio)
        self.db.commit()
        self.db.refresh(db_portfolio)
        return db_portfolio

    def get_user_portfolios(self, user_id: int) -> List[Portfolio]:
        """Get all portfolios for a user"""
        return self.db.query(Portfolio).filter(Portfolio.user_id == user_id).all()

    def get_portfolio(self, portfolio_id: int, user_id: int) -> Optional[Portfolio]:
        """Get a specific portfolio"""
        return self.db.query(Portfolio).filter(
            Portfolio.id == portfolio_id,
            Portfolio.user_id == user_id
        ).first()

    async def get_portfolio_summary(self, user_id: int) -> PortfolioSummary:
        """Get portfolio summary - DATABASE FIRST approach"""
        # Get default portfolio or create one
        portfolio = self.db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
        if not portfolio:
            portfolio_data = PortfolioCreate(name="Default Portfolio")
            portfolio = await self.create_portfolio(user_id, portfolio_data)

        # ALWAYS return stored values first (never 0)
        summary = PortfolioSummary(
        total_value=getattr(portfolio, 'total_value', 0.0) or 0.0,
        total_cost=getattr(portfolio, 'total_cost', 0.0) or 0.0,
        total_return=getattr(portfolio, 'total_return', 0.0) or 0.0,
        total_return_percent=getattr(portfolio, 'total_return_percent', 0.0) or 0.0,
        day_change=getattr(portfolio, 'day_change', 0.0) or 0.0,
        day_change_percent=getattr(portfolio, 'day_change_percent', 0.0) or 0.0,
        cash_balance=portfolio.cash_balance or 0.0,
        dividend_income=getattr(portfolio, 'dividend_income', 0.0) or 0.0,
        last_sync=portfolio.last_sync
        )

        # Try to update with real-time data in background (non-blocking)
        try:
            await self._background_update_portfolio(portfolio)
            # Refetch updated values
            self.db.refresh(portfolio)
            summary = PortfolioSummary(
                total_value=portfolio.total_value,
                total_cost=portfolio.total_cost,
                total_return=portfolio.total_return,
                total_return_percent=portfolio.total_return_percent,
                day_change=portfolio.day_change,
                day_change_percent=portfolio.day_change_percent,
                cash_balance=portfolio.cash_balance,
                dividend_income=portfolio.dividend_income,
                last_sync=portfolio.last_sync
            )
        except Exception as e:
            print(f"Background update failed, using stored values: {e}")
            # Continue with stored values - don't fail

        return summary

    async def _background_update_portfolio(self, portfolio: Portfolio):
        """Update portfolio prices and recalculate - store in database"""
        holdings = self.db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()
        
        if not holdings:
            return

        # # Check if we need to update (rate limiting)
        # current_time = datetime.now(timezone.utc)
        # if portfolio.last_sync:
        #     last_sync = portfolio.last_sync
        #     if last_sync.tzinfo is None:
        #         last_sync = last_sync.replace(tzinfo=timezone.utc)
        #     if current_time - last_sync < timedelta(minutes=2):  # Rate limit: 2 minutes
        #         return

        # Get market data with proper error handling
        symbols = [h.symbol for h in holdings]
        quotes = {}
        
        # try:
        #     # Batch request with timeout
        #     quotes = await market_data_service.get_multiple_quotes(symbols)
        # except Exception as e:
        #     print(f"Market data service failed: {e}")
        #     return  # Use existing stored values

        # Update holdings and store in database
        total_value = portfolio.cash_balance
        total_cost = 0.0
        total_day_change = 0.0

        for holding in holdings:
            if holding.symbol in quotes:
                quote = quotes[holding.symbol]
                
                # Update holding with new prices
                holding.current_price = quote["price"]
                holding.market_value = holding.shares * quote["price"]
                holding.day_change = quote.get("change", 0)
                holding.day_change_percent = quote.get("changePercent", 0)
                holding.last_price_update = current_time

                # Recalculate returns
                cost_basis = holding.shares * holding.avg_cost
                holding.total_return = holding.market_value - cost_basis
                holding.total_return_percent = (holding.total_return / cost_basis * 100) if cost_basis > 0 else 0

            # Accumulate totals (use stored values if update failed)
            total_value += holding.market_value
            total_cost += holding.shares * holding.avg_cost
            total_day_change += (holding.day_change or 0) * holding.shares

        # Calculate portfolio-level metrics
        total_return = total_value - total_cost
        total_return_percent = (total_return / total_cost * 100) if total_cost > 0 else 0
        yesterday_value = total_value - total_day_change
        day_change_percent = (total_day_change / yesterday_value * 100) if yesterday_value > 0 else 0

        # Calculate dividend income
        dividend_transactions = self.db.query(Transaction).filter(
            Transaction.portfolio_id == portfolio.id,
            Transaction.type == "DIVIDEND"
        ).all()
        dividend_income = sum(t.total_amount for t in dividend_transactions)

        # STORE calculated values in database
        portfolio.total_value = total_value
        portfolio.total_cost = total_cost
        portfolio.total_return = total_return
        portfolio.total_return_percent = total_return_percent
        portfolio.day_change = total_day_change
        portfolio.day_change_percent = day_change_percent
        portfolio.dividend_income = dividend_income
        portfolio.last_sync = current_time

        try:
            self.db.commit()
        except Exception as e:
            print(f"Database commit failed: {e}")
            self.db.rollback()
            raise

    async def add_holding(self, user_id: int, holding_data: HoldingCreate) -> Holding:
        """Add holding and immediately update portfolio totals"""
        # Get or create default portfolio
        portfolio = self.db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
        if not portfolio:
            portfolio_data = PortfolioCreate(name="Default Portfolio")
            portfolio = await self.create_portfolio(user_id, portfolio_data)

        # Get market data with fallback
        current_price = holding_data.avg_cost  # Fallback to avg_cost
        quote_data = {"name": holding_data.symbol, "price": current_price}
        
        try:
            quote = await market_data_service.get_quote(holding_data.symbol.upper())
            if quote:
                quote_data = quote
                current_price = quote["price"]
        except Exception as e:
            print(f"Failed to fetch market data for {holding_data.symbol}: {e}")

        # Check if holding already exists
        existing_holding = self.db.query(Holding).filter(
            Holding.portfolio_id == portfolio.id,
            Holding.symbol == holding_data.symbol.upper()
        ).first()

        if existing_holding:
            # Update existing holding
            total_shares = existing_holding.shares + holding_data.shares
            total_cost = (existing_holding.shares * existing_holding.avg_cost) + (holding_data.shares * holding_data.avg_cost)
            new_avg_cost = total_cost / total_shares

            existing_holding.shares = total_shares
            existing_holding.avg_cost = new_avg_cost
            existing_holding.current_price = current_price
            existing_holding.market_value = total_shares * current_price
            existing_holding.last_price_update = datetime.utcnow()

            # Calculate returns
            cost_basis = total_shares * new_avg_cost
            existing_holding.total_return = existing_holding.market_value - cost_basis
            existing_holding.total_return_percent = (existing_holding.total_return / cost_basis * 100) if cost_basis > 0 else 0

            holding = existing_holding
        else:
            # Create new holding
            market_value = holding_data.shares * current_price
            cost_basis = holding_data.shares * holding_data.avg_cost
            total_return = market_value - cost_basis
            total_return_percent = (total_return / cost_basis * 100) if cost_basis > 0 else 0

            holding = Holding(
                portfolio_id=portfolio.id,
                symbol=holding_data.symbol.upper(),
                name=quote_data.get("name", holding_data.symbol),
                shares=holding_data.shares,
                avg_cost=holding_data.avg_cost,
                current_price=current_price,
                market_value=market_value,
                total_return=total_return,
                total_return_percent=total_return_percent,
                sector=quote_data.get("sector"),
                industry=quote_data.get("industry"),
                last_price_update=datetime.utcnow()
            )
            self.db.add(holding)

        # Record transaction
        transaction = Transaction(
            portfolio_id=portfolio.id,
            symbol=holding_data.symbol.upper(),
            type="BUY",
            shares=holding_data.shares,
            price=holding_data.avg_cost,
            total_amount=holding_data.shares * holding_data.avg_cost,
            transaction_date=datetime.utcnow()
        )
        self.db.add(transaction)

        # Immediately update portfolio totals
        await self._recalculate_and_store_portfolio(portfolio)
        
        self.db.commit()
        self.db.refresh(holding)
        return holding

    async def _recalculate_and_store_portfolio(self, portfolio: Portfolio):
        """Recalculate portfolio totals and store in database"""
        holdings = self.db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()
        
        total_value = portfolio.cash_balance
        total_cost = 0.0
        
        for holding in holdings:
            total_value += holding.market_value
            total_cost += holding.shares * holding.avg_cost

        total_return = total_value - total_cost
        total_return_percent = (total_return / total_cost * 100) if total_cost > 0 else 0

        # Calculate dividend income
        dividend_transactions = self.db.query(Transaction).filter(
            Transaction.portfolio_id == portfolio.id,
            Transaction.type == "DIVIDEND"
        ).all()
        dividend_income = sum(t.total_amount for t in dividend_transactions)

        # Store in database
        portfolio.total_value = total_value
        portfolio.total_cost = total_cost
        portfolio.total_return = total_return
        portfolio.total_return_percent = total_return_percent
        portfolio.dividend_income = dividend_income

    async def get_holdings(self, user_id: int) -> List[Holding]:
        """Get all holdings - database first"""
        portfolio = self.db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
        if not portfolio:
            return []

        holdings = self.db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()
        
        # Try background update but don't fail if it doesn't work
        try:
            await self._background_update_portfolio(portfolio)
            self.db.refresh(portfolio)
            # Refresh holdings after update
            holdings = self.db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()
        except Exception as e:
            print(f"Background update failed for holdings: {e}")

        return holdings

    async def get_portfolio_metrics(self, user_id: int) -> Dict:
        """Calculate advanced portfolio metrics"""
        portfolio = self.db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
        if not portfolio:
            return {"metrics": {}, "sectorAllocation": []}

        holdings = self.db.query(Holding).filter(Holding.portfolio_id == portfolio.id).all()
        if not holdings:
            return {"metrics": {}, "sectorAllocation": []}

        # Calculate sector allocation from current data
        sector_allocation = self._calculate_sector_allocation(holdings)

        # Basic metrics from stored data
        metrics = {
            "totalReturn": portfolio.total_return or 0,
            "totalReturnPercent": portfolio.total_return_percent or 0,
            "dayChange": portfolio.day_change or 0,
            "dayChangePercent": portfolio.day_change_percent or 0,
            "dividendYield": (portfolio.dividend_income / portfolio.total_value * 100) if portfolio.total_value > 0 else 0
        }

        return {
            "metrics": metrics,
            "sectorAllocation": sector_allocation
        }

    def _calculate_sector_allocation(self, holdings: List[Holding]) -> List[Dict]:
        """Calculate sector allocation"""
        sector_data = {}
        total_value = sum(h.market_value for h in holdings)

        for holding in holdings:
            sector = holding.sector or "Other"
            if sector not in sector_data:
                sector_data[sector] = {"value": 0, "count": 0}
            
            sector_data[sector]["value"] += holding.market_value
            sector_data[sector]["count"] += 1

        allocation = []
        for sector, data in sector_data.items():
            percentage = (data["value"] / total_value * 100) if total_value > 0 else 0
            allocation.append({
                "sector": sector,
                "value": data["value"],
                "percentage": percentage,
                "count": data["count"]
            })

        return sorted(allocation, key=lambda x: x["percentage"], reverse=True)
    
    async def get_transactions(
        self,
        user_id: int,
        symbol: str = None,
        transaction_type: str = None,
        start_date = None,
        end_date = None,
        limit: int = 50,
        offset: int = 0,
    ):
        # Get the user's portfolio
        portfolio = self.db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
        if not portfolio:
            return []

        query = self.db.query(Transaction).filter(Transaction.portfolio_id == portfolio.id)

        # Apply filters
        if symbol:
            query = query.filter(Transaction.symbol == symbol.upper())
        if transaction_type:
            query = query.filter(Transaction.type == transaction_type.upper())
        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)

        # Pagination
        transactions = query.order_by(Transaction.transaction_date.desc()).offset(offset).limit(limit).all()
        return transactions

    async def get_transaction(self, transaction_id: int, user_id: int):
        portfolio = self.db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
        if not portfolio:
            return None
        transaction = self.db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.portfolio_id == portfolio.id
        ).first()
        return transaction

    async def add_transaction(self, user_id: int, transaction_data):
        """Add a transaction and update corresponding holding"""
        portfolio = self.db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
        if not portfolio:
            portfolio_data = PortfolioCreate(name="Default Portfolio")
            portfolio = await self.create_portfolio(user_id, portfolio_data)

        # Create transaction
        transaction = Transaction(
            portfolio_id=portfolio.id,
            symbol=transaction_data.symbol.upper(),
            type=transaction_data.type,
            shares=transaction_data.shares,
            price=transaction_data.price,
            total_amount=transaction_data.shares * transaction_data.price,
            transaction_date=transaction_data.transaction_date or datetime.utcnow(),
            note=transaction_data.note,
            fees=transaction_data.fees or 0.0,
        )
        self.db.add(transaction)

        # Update or create corresponding holding
        if transaction_data.type in ['BUY', 'SELL']:
            holding = self.db.query(Holding).filter(
                Holding.portfolio_id == portfolio.id,
                Holding.symbol == transaction_data.symbol.upper()
            ).first()

            if transaction_data.type == 'BUY':
                if holding:
                    # Update existing holding
                    total_shares = holding.shares + transaction_data.shares
                    total_cost = (holding.shares * holding.avg_cost) + (transaction_data.shares * transaction_data.price)
                    holding.avg_cost = total_cost / total_shares
                    holding.shares = total_shares
                else:
                    # Create new holding
                    holding = Holding(
                        portfolio_id=portfolio.id,
                        symbol=transaction_data.symbol.upper(),
                        name=transaction_data.symbol.upper(),
                        shares=transaction_data.shares,
                        avg_cost=transaction_data.price,
                        current_price=transaction_data.price,
                        market_value=transaction_data.shares * transaction_data.price
                    )
                    self.db.add(holding)
            elif transaction_data.type == 'SELL' and holding:
                holding.shares -= transaction_data.shares
                if holding.shares <= 0:
                    self.db.delete(holding)

        # Commit changes
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    async def delete_transaction(self, transaction_id: int, user_id: int):
        portfolio = self.db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
        if not portfolio:
            return False
        transaction = self.db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.portfolio_id == portfolio.id
        ).first()
        if not transaction:
            return False
        self.db.delete(transaction)
        self.db.commit()
        return True

    async def get_transaction_stats(self, user_id: int):
        # This is just a placeholder for summary stats; implement as needed
        portfolio = self.db.query(Portfolio).filter(Portfolio.user_id == user_id).first()
        if not portfolio:
            return {}
        transactions = self.db.query(Transaction).filter(Transaction.portfolio_id == portfolio.id).all()
        total = len(transactions)
        buy_count = sum(1 for t in transactions if t.type == "BUY")
        sell_count = sum(1 for t in transactions if t.type == "SELL")
        dividend_count = sum(1 for t in transactions if t.type == "DIVIDEND")
        return {
            "total": total,
            "buy_count": buy_count,
            "sell_count": sell_count,
            "dividend_count": dividend_count
        }
