"""Decision engine for AI-powered trading decisions"""

import json
from typing import Dict, Optional, List
from enum import Enum
from src.models.market_data import MarketData, Candle
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TradeSignal(str, Enum):
    """Trade signal types"""
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"


class DecisionEngine:
    """AI decision engine for trading signals"""
    
    def __init__(self):
        """Initialize decision engine"""
        self.min_confidence = 0.6  # Minimum confidence for trade
        self.decision_history: List[Dict] = []
    
    async def analyze_market(self, symbol: str, market_data: MarketData) -> Dict:
        """Analyze market data and generate trading signal
        
        Args:
            symbol: Trading symbol
            market_data: Market data for the symbol
        
        Returns:
            Decision with signal and confidence
        """
        try:
            # Technical analysis
            momentum_score = self._calculate_momentum(market_data)
            volatility_score = self._calculate_volatility(market_data)
            support_resistance = self._calculate_support_resistance(market_data)
            
            # Aggregate signals
            signal, confidence = self._aggregate_signals(
                momentum_score,
                volatility_score,
                support_resistance
            )
            
            decision = {
                "symbol": symbol,
                "signal": signal,
                "confidence": confidence,
                "momentum_score": momentum_score,
                "volatility_score": volatility_score,
                "support_resistance": support_resistance,
                "recommended_action": self._signal_to_action(signal, confidence)
            }
            
            self.decision_history.append(decision)
            logger.info(f"Decision: {symbol} {signal} (confidence: {confidence:.2%})")
            return decision
        except Exception as e:
            logger.error(f"Error analyzing market for {symbol}: {e}")
            raise
    
    async def analyze_technical_indicators(
        self,
        symbol: str,
        candles: List[Candle]
    ) -> Dict:
        """Analyze technical indicators from candle data
        
        Args:
            symbol: Trading symbol
            candles: List of candles for analysis
        
        Returns:
            Technical analysis results
        """
        try:
            if len(candles) < 2:
                logger.warning(f"Insufficient data for {symbol}")
                return {"error": "Insufficient data"}
            
            # Calculate technical indicators
            sma_20 = self._calculate_sma(candles, 20)
            sma_50 = self._calculate_sma(candles, 50)
            rsi = self._calculate_rsi(candles, 14)
            macd = self._calculate_macd(candles)
            
            # Generate signals from indicators
            signals = []
            if sma_20 > sma_50:
                signals.append("uptrend")
            if rsi < 30:
                signals.append("oversold")
            if rsi > 70:
                signals.append("overbought")
            if macd["histogram"] > 0:
                signals.append("bullish_macd")
            
            return {
                "symbol": symbol,
                "sma_20": sma_20,
                "sma_50": sma_50,
                "rsi": rsi,
                "macd": macd,
                "signals": signals
            }
        except Exception as e:
            logger.error(f"Error analyzing indicators for {symbol}: {e}")
            raise
    
    def _calculate_momentum(self, market_data: MarketData) -> float:
        """Calculate momentum score (0-1)
        
        Args:
            market_data: Market data
        
        Returns:
            Momentum score
        """
        # Simple momentum: price change in 24h
        price_change_24h = market_data.price_change_24h_percent
        
        # Normalize to 0-1 range (-10% to +10% range)
        momentum = (price_change_24h + 10) / 20
        momentum = max(0, min(1, momentum))  # Clamp to 0-1
        
        return momentum
    
    def _calculate_volatility(self, market_data: MarketData) -> float:
        """Calculate volatility score (0-1)
        
        Args:
            market_data: Market data
        
        Returns:
            Volatility score
        """
        # Volatility based on 24h range
        volatility = market_data.volatility_24h() / 100  # Percentage to 0-1
        volatility = max(0, min(1, volatility))  # Clamp to 0-1
        
        return volatility
    
    def _calculate_support_resistance(self, market_data: MarketData) -> Dict:
        """Calculate support and resistance levels
        
        Args:
            market_data: Market data
        
        Returns:
            Support and resistance levels
        """
        return {
            "support": market_data.low_24h,
            "resistance": market_data.high_24h,
            "mid_point": (market_data.high_24h + market_data.low_24h) / 2
        }
    
    def _aggregate_signals(
        self,
        momentum_score: float,
        volatility_score: float,
        support_resistance: Dict
    ) -> tuple:
        """Aggregate multiple signals into final decision
        
        Args:
            momentum_score: Momentum score (0-1)
            volatility_score: Volatility score (0-1)
            support_resistance: Support/resistance levels
        
        Returns:
            (Signal, Confidence) tuple
        """
        # Weighted combination
        combined_score = (momentum_score * 0.6) + (1 - volatility_score * 0.2)
        
        if combined_score > 0.75:
            signal = TradeSignal.STRONG_BUY
            confidence = combined_score
        elif combined_score > 0.6:
            signal = TradeSignal.BUY
            confidence = combined_score
        elif combined_score < 0.25:
            signal = TradeSignal.STRONG_SELL
            confidence = 1 - combined_score
        elif combined_score < 0.4:
            signal = TradeSignal.SELL
            confidence = 1 - combined_score
        else:
            signal = TradeSignal.HOLD
            confidence = 1 - abs(combined_score - 0.5) * 2
        
        return signal, confidence
    
    def _signal_to_action(self, signal: TradeSignal, confidence: float) -> str:
        """Convert signal to action
        
        Args:
            signal: Trade signal
            confidence: Signal confidence
        
        Returns:
            Recommended action
        """
        if confidence < self.min_confidence:
            return "SKIP_LOW_CONFIDENCE"
        
        if signal in [TradeSignal.STRONG_BUY, TradeSignal.BUY]:
            return "PLACE_BUY_ORDER"
        elif signal in [TradeSignal.STRONG_SELL, TradeSignal.SELL]:
            return "PLACE_SELL_ORDER"
        else:
            return "HOLD"
    
    def _calculate_sma(self, candles: List[Candle], period: int) -> float:
        """Calculate Simple Moving Average
        
        Args:
            candles: List of candles
            period: SMA period
        
        Returns:
            SMA value
        """
        if len(candles) < period:
            return 0.0
        
        close_prices = [c.close for c in candles[-period:]]
        return sum(close_prices) / len(close_prices)
    
    def _calculate_rsi(self, candles: List[Candle], period: int = 14) -> float:
        """Calculate Relative Strength Index
        
        Args:
            candles: List of candles
            period: RSI period
        
        Returns:
            RSI value (0-100)
        """
        if len(candles) < period + 1:
            return 50.0  # Neutral
        
        gains = 0.0
        losses = 0.0
        
        for i in range(1, period + 1):
            change = candles[-i].close - candles[-i-1].close
            if change > 0:
                gains += change
            else:
                losses += abs(change)
        
        avg_gain = gains / period
        avg_loss = losses / period
        
        if avg_loss == 0:
            return 100.0 if avg_gain > 0 else 50.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_macd(
        self,
        candles: List[Candle],
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Dict:
        """Calculate MACD indicator
        
        Args:
            candles: List of candles
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period
        
        Returns:
            MACD values
        """
        if len(candles) < slow + 1:
            return {"macd": 0.0, "signal": 0.0, "histogram": 0.0}
        
        close_prices = [c.close for c in candles]
        
        # Calculate EMAs
        ema_fast = self._calculate_ema(close_prices, fast)
        ema_slow = self._calculate_ema(close_prices, slow)
        
        macd_line = ema_fast - ema_slow
        signal_line = self._calculate_ema([macd_line], signal)
        histogram = macd_line - signal_line
        
        return {
            "macd": macd_line,
            "signal": signal_line,
            "histogram": histogram
        }
    
    def _calculate_ema(
        self,
        values: List[float],
        period: int
    ) -> float:
        """Calculate Exponential Moving Average
        
        Args:
            values: List of values
            period: EMA period
        
        Returns:
            EMA value
        """
        if len(values) == 0:
            return 0.0
        
        if len(values) < period:
            return sum(values) / len(values)
        
        multiplier = 2 / (period + 1)
        ema = sum(values[:period]) / period
        
        for i in range(period, len(values)):
            ema = (values[i] * multiplier) + (ema * (1 - multiplier))
        
        return ema
