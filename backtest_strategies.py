import pandas as pd
import numpy as np
import pickle
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class BacktestEngine:
    """
    Backtesting engine for Sensex scalping strategies
    with realistic costs (brokerage, STT, slippage)
    """
    
    def __init__(self, data, initial_capital=100000, position_size=0.95):
        """
        Args:
            data: DataFrame with OHLCV data
            initial_capital: Starting capital in rupees
            position_size: % of capital to use per trade (0.95 = 95%)
        """
        self.data = data.copy()
        self.initial_capital = initial_capital
        self.position_size = position_size
        self.capital = initial_capital
        
        # India-specific costs
        self.brokerage_pct = 0.0015  # 0.15% brokerage
        self.stt_pct = 0.0001  # 0.01% STT on sell (Sensex futures)
        self.slippage_points = 5  # 5 points slippage average
        
    def calculate_costs(self, entry_price, exit_price, quantity):
        """Calculate total trading costs"""
        entry_cost = entry_price * quantity * self.brokerage_pct
        exit_cost = exit_price * quantity * (self.brokerage_pct + self.stt_pct)
        slippage_cost = self.slippage_points * quantity
        return entry_cost + exit_cost + slippage_cost
    
    def strategy_1_gap_reversion(self):
        """
        Strategy 1: Gap & Reversion (Opening Hour Scalp)
        - Identifies opening gaps
        - Enters on reversion bounce
        - Quick exit at 20-30 point profit
        """
        trades = []
        entry_price = None
        position = False
        entry_index = None
        
        for i in range(1, len(self.data)):
            row = self.data.iloc[i]
            prev_row = self.data.iloc[i-1]
            
            # Entry condition: Opening gap exists and price is reverting
            if not position and i > 5:
                gap = row['Open'] - prev_row['Close']
                
                if abs(gap) > 50:  # Significant gap (50+ points)
                    # Wait for reversion
                    reversion = (row['Close'] - row['Open'])
                    
                    if gap < 0 and reversion > 20:  # Gap down, price bouncing up
                        entry_price = row['Close']
                        position = True
                        entry_index = i
                    elif gap > 0 and reversion < -20:  # Gap up, price coming down
                        entry_price = row['Close']
                        position = True
                        entry_index = i
            
            # Exit condition: 20-30 point profit or stop loss
            if position:
                profit_points = row['Close'] - entry_price
                
                if profit_points >= 30:  # Target hit
                    exit_price = row['Close']
                    quantity = 1
                    costs = self.calculate_costs(entry_price, exit_price, quantity)
                    net_profit = (profit_points * quantity) - costs
                    
                    trades.append({
                        'strategy': 'Gap Reversion',
                        'entry_date': self.data.index[entry_index],
                        'exit_date': row.name,
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'profit_points': profit_points,
                        'costs': costs,
                        'net_profit': net_profit,
                        'days_held': (row.name - self.data.index[entry_index]).days
                    })
                    position = False
                    
                elif profit_points <= -30:  # Stop loss hit
                    exit_price = row['Close']
                    quantity = 1
                    costs = self.calculate_costs(entry_price, exit_price, quantity)
                    net_profit = (profit_points * quantity) - costs
                    
                    trades.append({
                        'strategy': 'Gap Reversion',
                        'entry_date': self.data.index[entry_index],
                        'exit_date': row.name,
                        'entry_price': entry_price,
                        'exit_price': exit_price,
                        'profit_points': profit_points,
                        'costs': costs,
                        'net_profit': net_profit,
                        'days_held': (row.name - self.data.index[entry_index]).days
                    })
                    position = False
        
        return pd.DataFrame(trades)
    
    def strategy_2_bollinger_breakout(self):
        """
        Strategy 2: Bollinger Band Breakout
        - Identifies BB squeeze (narrow bands)
        - Enters on breakout above/below bands
        - Quick exit on reversion or target
        """
        trades = []
        entry_price = None
        position = False
        entry_index = None
        direction = None  # 'long' or 'short'
        
        for i in range(20, len(self.data)):
            row = self.data.iloc[i]
            
            # Entry condition: Price breaks above/below Bollinger Bands
            if not position:
                # Long setup: price closes above upper BB
                if row['Close'] > row['BB_20_UPPER']:
                    entry_price = row['Close']
                    position = True
                    entry_index = i
                    direction = 'long'
                
                # Short setup: price closes below lower BB
                elif row['Close'] < row['BB_20_LOWER']:
                    entry_price = row['Close']
                    position = True
                    entry_index = i
                    direction = 'short'
            
            # Exit condition
            if position:
                if direction == 'long':
                    profit_points = row['Close'] - entry_price
                    
                    if profit_points >= 25:  # Target
                        exit_price = row['Close']
                        quantity = 1
                        costs = self.calculate_costs(entry_price, exit_price, quantity)
                        net_profit = (profit_points * quantity) - costs
                        
                        trades.append({
                            'strategy': 'BB Breakout',
                            'entry_date': self.data.index[entry_index],
                            'exit_date': row.name,
                            'entry_price': entry_price,
                            'exit_price': exit_price,
                            'profit_points': profit_points,
                            'costs': costs,
                            'net_profit': net_profit,
                            'days_held': (row.name - self.data.index[entry_index]).days
                        })
                        position = False
                    
                    elif profit_points <= -20:  # Stop loss
                        exit_price = row['Close']
                        quantity = 1
                        costs = self.calculate_costs(entry_price, exit_price, quantity)
                        net_profit = (profit_points * quantity) - costs
                        
                        trades.append({
                            'strategy': 'BB Breakout',
                            'entry_date': self.data.index[entry_index],
                            'exit_date': row.name,
                            'entry_price': entry_price,
                            'exit_price': exit_price,
                            'profit_points': profit_points,
                            'costs': costs,
                            'net_profit': net_profit,
                            'days_held': (row.name - self.data.index[entry_index]).days
                        })
                        position = False
                
                elif direction == 'short':
                    profit_points = entry_price - row['Close']
                    
                    if profit_points >= 25:  # Target
                        exit_price = row['Close']
                        quantity = 1
                        costs = self.calculate_costs(entry_price, exit_price, quantity)
                        net_profit = (profit_points * quantity) - costs
                        
                        trades.append({
                            'strategy': 'BB Breakout',
                            'entry_date': self.data.index[entry_index],
                            'exit_date': row.name,
                            'entry_price': entry_price,
                            'exit_price': exit_price,
                            'profit_points': profit_points,
                            'costs': costs,
                            'net_profit': net_profit,
                            'days_held': (row.name - self.data.index[entry_index]).days
                        })
                        position = False
                    
                    elif profit_points <= -20:  # Stop loss
                        exit_price = row['Close']
                        quantity = 1
                        costs = self.calculate_costs(entry_price, exit_price, quantity)
                        net_profit = (profit_points * quantity) - costs
                        
                        trades.append({
                            'strategy': 'BB Breakout',
                            'entry_date': self.data.index[entry_index],
                            'exit_date': row.name,
                            'entry_price': entry_price,
                            'exit_price': exit_price,
                            'profit_points': profit_points,
                            'costs': costs,
                            'net_profit': net_profit,
                            'days_held': (row.name - self.data.index[entry_index]).days
                        })
                        position = False
        
        return pd.DataFrame(trades)
    
    def strategy_3_support_resistance(self):
        """
        Strategy 3: Support/Resistance Bounce + RSI
        - Identifies key support/resistance levels
        - Enters on bounce with RSI confirmation
        - Exits at next resistance or stop loss
        """
        trades = []
        entry_price = None
        position = False
        entry_index = None
        direction = None
        
        # Calculate support/resistance levels (simple approach)
        window = 20
        
        for i in range(window, len(self.data)):
            row = self.data.iloc[i]
            
            # Calculate local support/resistance
            local_high = self.data['High'].iloc[i-window:i].max()
            local_low = self.data['Low'].iloc[i-window:i].min()
            
            # Entry condition: Price bounces off support/resistance with RSI
            if not position:
                # Long setup: Price above support, RSI < 30 (oversold), bouncing up
                if row['Low'] <= local_low and row['RSI_14'] < 30:
                    if row['Close'] > row['Open']:  # Bullish candle
                        entry_price = row['Close']
                        position = True
                        entry_index = i
                        direction = 'long'
                
                # Short setup: Price below resistance, RSI > 70 (overbought), coming down
                elif row['High'] >= local_high and row['RSI_14'] > 70:
                    if row['Close'] < row['Open']:  # Bearish candle
                        entry_price = row['Close']
                        position = True
                        entry_index = i
                        direction = 'short'
            
            # Exit condition
            if position:
                if direction == 'long':
                    profit_points = row['Close'] - entry_price
                    
                    if profit_points >= 30:  # Target
                        exit_price = row['Close']
                        quantity = 1
                        costs = self.calculate_costs(entry_price, exit_price, quantity)
                        net_profit = (profit_points * quantity) - costs
                        
                        trades.append({
                            'strategy': 'Support/Resistance',
                            'entry_date': self.data.index[entry_index],
                            'exit_date': row.name,
                            'entry_price': entry_price,
                            'exit_price': exit_price,
                            'profit_points': profit_points,
                            'costs': costs,
                            'net_profit': net_profit,
                            'days_held': (row.name - self.data.index[entry_index]).days
                        })
                        position = False
                    
                    elif profit_points <= -25:  # Stop loss
                        exit_price = row['Close']
                        quantity = 1
                        costs = self.calculate_costs(entry_price, exit_price, quantity)
                        net_profit = (profit_points * quantity) - costs
                        
                        trades.append({
                            'strategy': 'Support/Resistance',
                            'entry_date': self.data.index[entry_index],
                            'exit_date': row.name,
                            'entry_price': entry_price,
                            'exit_price': exit_price,
                            'profit_points': profit_points,
                            'costs': costs,
                            'net_profit': net_profit,
                            'days_held': (row.name - self.data.index[entry_index]).days
                        })
                        position = False
                
                elif direction == 'short':
                    profit_points = entry_price - row['Close']
                    
                    if profit_points >= 30:  # Target
                        exit_price = row['Close']
                        quantity = 1
                        costs = self.calculate_costs(entry_price, exit_price, quantity)
                        net_profit = (profit_points * quantity) - costs
                        
                        trades.append({
                            'strategy': 'Support/Resistance',
                            'entry_date': self.data.index[entry_index],
                            'exit_date': row.name,
                            'entry_price': entry_price,
                            'exit_price': exit_price,
                            'profit_points': profit_points,
                            'costs': costs,
                            'net_profit': net_profit,
                            'days_held': (row.name - self.data.index[entry_index]).days
                        })
                        position = False
                    
                    elif profit_points <= -25:  # Stop loss
                        exit_price = row['Close']
                        quantity = 1
                        costs = self.calculate_costs(entry_price, exit_price, quantity)
                        net_profit = (profit_points * quantity) - costs
                        
                        trades.append({
                            'strategy': 'Support/Resistance',
                            'entry_date': self.data.index[entry_index],
                            'exit_date': row.name,
                            'entry_price': entry_price,
                            'exit_price': exit_price,
                            'profit_points': profit_points,
                            'costs': costs,
                            'net_profit': net_profit,
                            'days_held': (row.name - self.data.index[entry_index]).days
                        })
                        position = False
        
        return pd.DataFrame(trades)
    
    def calculate_metrics(self, trades_df):
        """Calculate performance metrics for a strategy"""
        if len(trades_df) == 0:
            return None
        
        trades_df = trades_df.copy()
        
        # Basic metrics
        total_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df['net_profit'] > 0])
        losing_trades = len(trades_df[trades_df['net_profit'] < 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # Profit metrics
        total_profit = trades_df['net_profit'].sum()
        avg_win = trades_df[trades_df['net_profit'] > 0]['net_profit'].mean() if winning_trades > 0 else 0
        avg_loss = trades_df[trades_df['net_profit'] < 0]['net_profit'].mean() if losing_trades > 0 else 0
        
        # Profit factor
        total_wins = trades_df[trades_df['net_profit'] > 0]['net_profit'].sum()
        total_losses = abs(trades_df[trades_df['net_profit'] < 0]['net_profit'].sum())
        profit_factor = total_wins / total_losses if total_losses > 0 else 0
        
        # Consecutive losses
        trades_df['is_win'] = trades_df['net_profit'] > 0
        max_consecutive_losses = 0
        current_losses = 0
        for is_win in trades_df['is_win']:
            if not is_win:
                current_losses += 1
                max_consecutive_losses = max(max_consecutive_losses, current_losses)
            else:
                current_losses = 0
        
        # Drawdown
        cumulative_profit = trades_df['net_profit'].cumsum()
        running_max = cumulative_profit.cummax()
        drawdown = running_max - cumulative_profit
        max_drawdown = drawdown.max()
        
        return {
            'Total Trades': total_trades,
            'Winning Trades': winning_trades,
            'Losing Trades': losing_trades,
            'Win Rate (%)': round(win_rate, 2),
            'Avg Win': round(avg_win, 2),
            'Avg Loss': round(avg_loss, 2),
            'Profit Factor': round(profit_factor, 2),
            'Total Net Profit': round(total_profit, 2),
            'Max Consecutive Losses': max_consecutive_losses,
            'Max Drawdown': round(max_drawdown, 2),
            'ROI (%)': round((total_profit / self.initial_capital) * 100, 2),
            'Avg Trade Duration (days)': round(trades_df['days_held'].mean(), 1)
        }

# Main execution
if __name__ == "__main__":
    print("\n" + "="*70)
    print("SENSEX SCALPING STRATEGY BACKTESTER")
    print("="*70)
    
    # Load data
    try:
        with open('sensex_data.pkl', 'rb') as f:
            data = pickle.load(f)
        print("✓ Data loaded successfully")
    except:
        print("✗ Error loading data. Please run fetch_sensex_data.py first")
        exit()
    
    # Initialize backtester
    backtester = BacktestEngine(data, initial_capital=100000)
    
    print("\nRunning backtests...")
    print("-"*70)
    
    # Test Strategy 1
    print("\n[1/3] Testing Gap & Reversion Strategy...")
    trades_1 = backtester.strategy_1_gap_reversion()
    metrics_1 = backtester.calculate_metrics(trades_1)
    
    # Test Strategy 2
    print("[2/3] Testing Bollinger Band Breakout Strategy...")
    trades_2 = backtester.strategy_2_bollinger_breakout()
    metrics_2 = backtester.calculate_metrics(trades_2)
    
    # Test Strategy 3
    print("[3/3] Testing Support/Resistance Bounce Strategy...")
    trades_3 = backtester.strategy_3_support_resistance()
    metrics_3 = backtester.calculate_metrics(trades_3)
    
    print("\n" + "="*70)
    print("BACKTEST RESULTS")
    print("="*70)
    
    # Display results
    strategies = ['Gap Reversion', 'BB Breakout', 'Support/Resistance']
    all_metrics = [metrics_1, metrics_2, metrics_3]
    
    for strategy, metrics in zip(strategies, all_metrics):
        if metrics:
            print(f"\n{strategy.upper()}")
            print("-"*70)
            for key, value in metrics.items():
                print(f"  {key:.<40} {value}")
        else:
            print(f"\n{strategy.upper()}: No trades generated")
    
    # Find best strategy
    print("\n" + "="*70)
    print("RANKING STRATEGIES (By Profit Factor)")
    print("="*70)
    
    valid_metrics = [(s, m) for s, m in zip(strategies, all_metrics) if m]
    ranked = sorted(valid_metrics, key=lambda x: x[1]['Profit Factor'], reverse=True)
    
    for rank, (strategy, metrics) in enumerate(ranked, 1):
        print(f"\n#{rank}: {strategy}")
        print(f"     Profit Factor: {metrics['Profit Factor']}")
        print(f"     Win Rate: {metrics['Win Rate (%)']}%")
        print(f"     Total Profit: ₹{metrics['Total Net Profit']:,.0f}")
    
    # Save all trades
    if len(trades_1) > 0:
        trades_1.to_csv('trades_gap_reversion.csv', index=False)
    if len(trades_2) > 0:
        trades_2.to_csv('trades_bb_breakout.csv', index=False)
    if len(trades_3) > 0:
        trades_3.to_csv('trades_support_resistance.csv', index=False)
    
    print("\n✓ Trade details saved to CSV files")
    print("\n" + "="*70)
