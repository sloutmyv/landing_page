"""
Portfolio API Views
Exposes portfolio data from Binance API
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .services.binance_service import BinanceService
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
def portfolio_view(request):
    """
    GET /api/portfolio/
    Returns portfolio composition with asset balances and USD values
    """
    try:
        binance_service = BinanceService()
        portfolio_data = binance_service.get_portfolio_composition()
        
        return Response({
            'success': True,
            'data': portfolio_data
        }, status=status.HTTP_200_OK)
    
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return Response({
            'success': False,
            'error': 'Binance API not configured properly'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    except Exception as e:
        logger.error(f"Error fetching portfolio: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def test_connection_view(request):
    """
    GET /api/portfolio/test/
    Test Binance API connection
    """
    try:
        binance_service = BinanceService()
        is_connected = binance_service.test_connection()
        
        return Response({
            'success': True,
            'connected': is_connected
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
