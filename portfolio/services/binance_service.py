"""
Binance API Service
Handles all interactions with the Binance API to fetch portfolio data.
"""
from binance.client import Client
from binance.exceptions import BinanceAPIException
from django.conf import settings
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class BinanceService:
    """Service to interact with Binance API"""
    
    def __init__(self):
        """Initialize Binance client with API credentials"""
        self.api_key = settings.BINANCE_API_KEY
        self.api_secret = settings.BINANCE_API_SECRET
        self.testnet = settings.BINANCE_TESTNET
        
        if not self.api_key or not self.api_secret:
            raise ValueError("Binance API credentials not configured")
        
        try:
            self.client = Client(self.api_key, self.api_secret, testnet=self.testnet)
        except Exception as e:
            logger.error(f"Failed to initialize Binance client: {e}")
            raise
    
    def get_account_balance(self):
        """
        Fetch account balance from Binance
        Returns: List of assets with balances
        """
        try:
            account = self.client.get_account()
            balances = account.get('balances', [])
            
            # Filter out zero balances
            non_zero_balances = [
                balance for balance in balances
                if float(balance['free']) > 0 or float(balance['locked']) > 0
            ]
            
            return non_zero_balances
        except BinanceAPIException as e:
            logger.error(f"Binance API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Error fetching account balance: {e}")
            raise
    
    def get_portfolio_composition(self):
        """
        Get portfolio composition with USD values
        Returns: Dict with portfolio data
        """
        try:
            balances = self.get_account_balance()
            
            # Get current prices for all symbols
            tickers = self.client.get_all_tickers()
            price_map = {ticker['symbol']: float(ticker['price']) for ticker in tickers}
            
            portfolio = []
            total_value_usd = 0
            
            for balance in balances:
                asset = balance['asset']
                free = float(balance['free'])
                locked = float(balance['locked'])
                total = free + locked
                
                # Get USD value
                usd_value = 0
                if asset == 'USDT' or asset == 'BUSD' or asset == 'USD':
                    usd_value = total
                else:
                    # Try to get price in USDT
                    symbol_usdt = f"{asset}USDT"
                    symbol_busd = f"{asset}BUSD"
                    
                    if symbol_usdt in price_map:
                        usd_value = total * price_map[symbol_usdt]
                    elif symbol_busd in price_map:
                        usd_value = total * price_map[symbol_busd]
                    else:
                        # Try BTC conversion
                        symbol_btc = f"{asset}BTC"
                        if symbol_btc in price_map and 'BTCUSDT' in price_map:
                            btc_value = total * price_map[symbol_btc]
                            usd_value = btc_value * price_map['BTCUSDT']
                
                if usd_value > 0.01:  # Only include assets worth more than 1 cent
                    portfolio.append({
                        'asset': asset,
                        'free': free,
                        'locked': locked,
                        'total': total,
                        'usd_value': round(usd_value, 2)
                    })
                    total_value_usd += usd_value
            
            # Sort by USD value descending
            portfolio.sort(key=lambda x: x['usd_value'], reverse=True)
            
            # Calculate percentages
            for item in portfolio:
                item['percentage'] = round((item['usd_value'] / total_value_usd * 100), 2) if total_value_usd > 0 else 0
            
            return {
                'assets': portfolio,
                'total_value_usd': round(total_value_usd, 2),
                'asset_count': len(portfolio)
            }
        except Exception as e:
            logger.error(f"Error getting portfolio composition: {e}")
            raise
    
    def test_connection(self):
        """
        Test Binance API connection
        Returns: True if connection successful, False otherwise
        """
        try:
            self.client.ping()
            return True
        except Exception as e:
            logger.error(f"Binance connection test failed: {e}")
            return False
