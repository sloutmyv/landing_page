import React, { useState, useEffect } from 'react';
import { getPortfolio } from '../services/api';
import './Portfolio.css';

const Portfolio = () => {
    const [portfolio, setPortfolio] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [lastUpdate, setLastUpdate] = useState(null);

    const fetchPortfolio = async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await getPortfolio();

            if (data.success) {
                setPortfolio(data.data);
                setLastUpdate(new Date());
            } else {
                setError(data.error || 'Failed to fetch portfolio');
            }
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to connect to server');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchPortfolio();
        // Refresh every 30 seconds
        const interval = setInterval(fetchPortfolio, 30000);
        return () => clearInterval(interval);
    }, []);

    if (loading && !portfolio) {
        return (
            <div className="portfolio-container">
                <div className="loading">
                    <div className="spinner"></div>
                    <p>Loading portfolio...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="portfolio-container">
                <div className="error">
                    <h2>⚠️ Error</h2>
                    <p>{error}</p>
                    <button onClick={fetchPortfolio} className="retry-button">
                        Retry
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="portfolio-container">
            <div className="portfolio-header">
                <h1>💼 Binance Portfolio</h1>
                <div className="header-info">
                    <div className="total-value">
                        <span className="label">Total Value</span>
                        <span className="value">${portfolio?.total_value_usd?.toLocaleString()}</span>
                    </div>
                    <div className="asset-count">
                        <span className="label">Assets</span>
                        <span className="value">{portfolio?.asset_count}</span>
                    </div>
                    <button onClick={fetchPortfolio} className="refresh-button" disabled={loading}>
                        {loading ? '⟳' : '🔄'} Refresh
                    </button>
                </div>
                {lastUpdate && (
                    <p className="last-update">
                        Last updated: {lastUpdate.toLocaleTimeString()}
                    </p>
                )}
            </div>

            <div className="assets-grid">
                {portfolio?.assets?.map((asset) => (
                    <div key={asset.asset} className="asset-card">
                        <div className="asset-header">
                            <h3 className="asset-name">{asset.asset}</h3>
                            <span className="asset-percentage">{asset.percentage}%</span>
                        </div>
                        <div className="asset-details">
                            <div className="detail-row">
                                <span className="detail-label">Total:</span>
                                <span className="detail-value">{asset.total.toFixed(8)}</span>
                            </div>
                            <div className="detail-row">
                                <span className="detail-label">Free:</span>
                                <span className="detail-value">{asset.free.toFixed(8)}</span>
                            </div>
                            {asset.locked > 0 && (
                                <div className="detail-row">
                                    <span className="detail-label">Locked:</span>
                                    <span className="detail-value locked">{asset.locked.toFixed(8)}</span>
                                </div>
                            )}
                            <div className="detail-row usd-value">
                                <span className="detail-label">USD Value:</span>
                                <span className="detail-value">${asset.usd_value.toLocaleString()}</span>
                            </div>
                        </div>
                        <div className="asset-bar">
                            <div
                                className="asset-bar-fill"
                                style={{ width: `${asset.percentage}%` }}
                            ></div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Portfolio;
