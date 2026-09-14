import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("darkgrid")
plt.rcParams['figure.figsize'] = (16, 12)

print("\nGenerating performance visualizations...")
print("="*70)

# Try to load trade data
try:
    trades_1 = pd.read_csv('trades_gap_reversion.csv')
except:
    trades_1 = pd.DataFrame()

try:
    trades_2 = pd.read_csv('trades_bb_breakout.csv')
except:
    trades_2 = pd.DataFrame()

try:
    trades_3 = pd.read_csv('trades_support_resistance.csv')
except:
    trades_3 = pd.DataFrame()

# Create figure with subplots
fig = plt.figure(figsize=(18, 14))

# Plot 1: Win Rate Comparison
ax1 = plt.subplot(3, 3, 1)
strategies = []
win_rates = []

for trades, name in [(trades_1, 'Gap Reversion'), 
                      (trades_2, 'BB Breakout'), 
                      (trades_3, 'Support/Resistance')]:
    if len(trades) > 0:
        win_rate = (len(trades[trades['net_profit'] > 0]) / len(trades)) * 100
        strategies.append(name)
        win_rates.append(win_rate)

if strategies:
    colors = ['green' if wr > 50 else 'red' for wr in win_rates]
    ax1.bar(strategies, win_rates, color=colors, alpha=0.7, edgecolor='black')
    ax1.axhline(y=50, color='orange', linestyle='--', label='50% (Break-even)')
    ax1.set_ylabel('Win Rate (%)', fontsize=10, fontweight='bold')
    ax1.set_title('Strategy Win Rates', fontsize=12, fontweight='bold')
    ax1.set_ylim([0, 100])
    for i, v in enumerate(win_rates):
        ax1.text(i, v+2, f'{v:.1f}%', ha='center', fontweight='bold')
    ax1.legend()
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=15, ha='right')

# Plot 2: Total Profit Comparison
ax2 = plt.subplot(3, 3, 2)
strategies = []
profits = []

for trades, name in [(trades_1, 'Gap Reversion'), 
                      (trades_2, 'BB Breakout'), 
                      (trades_3, 'Support/Resistance')]:
    if len(trades) > 0:
        total_profit = trades['net_profit'].sum()
        strategies.append(name)
        profits.append(total_profit)

if strategies:
    colors = ['green' if p > 0 else 'red' for p in profits]
    ax2.bar(strategies, profits, color=colors, alpha=0.7, edgecolor='black')
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax2.set_ylabel('Total Profit (₹)', fontsize=10, fontweight='bold')
    ax2.set_title('Total Net Profit (with costs)', fontsize=12, fontweight='bold')
    for i, v in enumerate(profits):
        ax2.text(i, v+50, f'₹{v:,.0f}', ha='center', fontweight='bold', fontsize=9)
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=15, ha='right')

# Plot 3: Profit Factor Comparison
ax3 = plt.subplot(3, 3, 3)
strategies = []
profit_factors = []

for trades, name in [(trades_1, 'Gap Reversion'), 
                      (trades_2, 'BB Breakout'), 
                      (trades_3, 'Support/Resistance')]:
    if len(trades) > 0:
        winning = trades[trades['net_profit'] > 0]['net_profit'].sum()
        losing = abs(trades[trades['net_profit'] < 0]['net_profit'].sum())
        pf = winning / losing if losing > 0 else 0
        strategies.append(name)
        profit_factors.append(pf)

if strategies:
    colors = ['green' if pf > 1.0 else 'red' for pf in profit_factors]
    ax3.bar(strategies, profit_factors, color=colors, alpha=0.7, edgecolor='black')
    ax3.axhline(y=1.0, color='orange', linestyle='--', label='1.0 (Break-even)')
    ax3.set_ylabel('Profit Factor', fontsize=10, fontweight='bold')
    ax3.set_title('Profit Factor (Wins/Losses)', fontsize=12, fontweight='bold')
    for i, v in enumerate(profit_factors):
        ax3.text(i, v+0.05, f'{v:.2f}', ha='center', fontweight='bold')
    ax3.legend()
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=15, ha='right')

# Plot 4: Trade Count
ax4 = plt.subplot(3, 3, 4)
strategies = []
trade_counts = []

for trades, name in [(trades_1, 'Gap Reversion'), 
                      (trades_2, 'BB Breakout'), 
                      (trades_3, 'Support/Resistance')]:
    if len(trades) > 0:
        strategies.append(name)
        trade_counts.append(len(trades))

if strategies:
    ax4.bar(strategies, trade_counts, color='steelblue', alpha=0.7, edgecolor='black')
    ax4.set_ylabel('Number of Trades', fontsize=10, fontweight='bold')
    ax4.set_title('Total Trades Generated', fontsize=12, fontweight='bold')
    for i, v in enumerate(trade_counts):
        ax4.text(i, v+5, f'{v}', ha='center', fontweight='bold')
    plt.setp(ax4.xaxis.get_majorticklabels(), rotation=15, ha='right')

# Plot 5: Average Win vs Average Loss
ax5 = plt.subplot(3, 3, 5)
x = np.arange(len(strategies) if strategies else 0)
width = 0.35

avg_wins = []
avg_losses = []

for trades in [trades_1, trades_2, trades_3]:
    if len(trades) > 0:
        avg_w = trades[trades['net_profit'] > 0]['net_profit'].mean() if len(trades[trades['net_profit'] > 0]) > 0 else 0
        avg_l = abs(trades[trades['net_profit'] < 0]['net_profit'].mean()) if len(trades[trades['net_profit'] < 0]) > 0 else 0
        avg_wins.append(avg_w)
        avg_losses.append(avg_l)

if avg_wins:
    ax5.bar(x - width/2, avg_wins, width, label='Avg Win', color='green', alpha=0.7, edgecolor='black')
    ax5.bar(x + width/2, avg_losses, width, label='Avg Loss', color='red', alpha=0.7, edgecolor='black')
    ax5.set_ylabel('Rupees (₹)', fontsize=10, fontweight='bold')
    ax5.set_title('Average Win vs Average Loss', fontsize=12, fontweight='bold')
    ax5.set_xticks(x)
    ax5.set_xticklabels(strategies if strategies else [])
    ax5.legend()
    plt.setp(ax5.xaxis.get_majorticklabels(), rotation=15, ha='right')

# Plot 6: Cumulative Profit Over Time
ax6 = plt.subplot(3, 3, 6)
for trades, name, color in [(trades_1, 'Gap Reversion', 'blue'), 
                              (trades_2, 'BB Breakout', 'green'), 
                              (trades_3, 'Support/Resistance', 'red')]:
    if len(trades) > 0:
        trades_sorted = trades.sort_values('exit_date')
        cumulative = trades_sorted['net_profit'].cumsum()
        ax6.plot(range(len(cumulative)), cumulative.values, marker='o', 
                label=name, color=color, alpha=0.7, linewidth=2, markersize=3)

ax6.set_xlabel('Trade Number', fontsize=10, fontweight='bold')
ax6.set_ylabel('Cumulative Profit (₹)', fontsize=10, fontweight='bold')
ax6.set_title('Cumulative Profit Over Time', fontsize=12, fontweight='bold')
ax6.axhline(y=0, color='black', linestyle='--', linewidth=1)
ax6.legend()
ax6.grid(True, alpha=0.3)

# Plot 7: Profit Distribution
ax7 = plt.subplot(3, 3, 7)
for trades, name, color in [(trades_1, 'Gap Reversion', 'blue'), 
                              (trades_2, 'BB Breakout', 'green'), 
                              (trades_3, 'Support/Resistance', 'red')]:
    if len(trades) > 0:
        ax7.hist(trades['net_profit'], bins=20, alpha=0.5, label=name, color=color, edgecolor='black')

ax7.axvline(x=0, color='black', linestyle='--', linewidth=2)
ax7.set_xlabel('Net Profit per Trade (₹)', fontsize=10, fontweight='bold')
ax7.set_ylabel('Frequency', fontsize=10, fontweight='bold')
ax7.set_title('Profit Distribution by Trade', fontsize=12, fontweight='bold')
ax7.legend()
ax7.grid(True, alpha=0.3)

# Plot 8: Max Consecutive Losses
ax8 = plt.subplot(3, 3, 8)
strategies = []
max_losses = []

for trades, name in [(trades_1, 'Gap Reversion'), 
                      (trades_2, 'BB Breakout'), 
                      (trades_3, 'Support/Resistance')]:
    if len(trades) > 0:
        trades['is_loss'] = trades['net_profit'] < 0
        max_consecutive = 0
        current = 0
        for is_loss in trades['is_loss']:
            if is_loss:
                current += 1
                max_consecutive = max(max_consecutive, current)
            else:
                current = 0
        strategies.append(name)
        max_losses.append(max_consecutive)

if strategies:
    ax8.bar(strategies, max_losses, color='orange', alpha=0.7, edgecolor='black')
    ax8.set_ylabel('Consecutive Losses', fontsize=10, fontweight='bold')
    ax8.set_title('Max Consecutive Losses', fontsize=12, fontweight='bold')
    for i, v in enumerate(max_losses):
        ax8.text(i, v+0.5, f'{v}', ha='center', fontweight='bold')
    plt.setp(ax8.xaxis.get_majorticklabels(), rotation=15, ha='right')

# Plot 9: Win % by Strategy
ax9 = plt.subplot(3, 3, 9)
strategies_list = []
win_pct = []
loss_pct = []

for trades, name in [(trades_1, 'Gap Reversion'), 
                      (trades_2, 'BB Breakout'), 
                      (trades_3, 'Support/Resistance')]:
    if len(trades) > 0:
        wins = len(trades[trades['net_profit'] > 0])
        losses = len(trades[trades['net_profit'] < 0])
        total = len(trades)
        strategies_list.append(name)
        win_pct.append((wins/total)*100)
        loss_pct.append((losses/total)*100)

if strategies_list:
    x = np.arange(len(strategies_list))
    width = 0.6
    ax9.bar(x, win_pct, width, label='Wins', color='green', alpha=0.7, edgecolor='black')
    ax9.bar(x, loss_pct, width, bottom=win_pct, label='Losses', color='red', alpha=0.7, edgecolor='black')
    ax9.set_ylabel('Percentage (%)', fontsize=10, fontweight='bold')
    ax9.set_title('Win/Loss Distribution', fontsize=12, fontweight='bold')
    ax9.set_xticks(x)
    ax9.set_xticklabels(strategies_list)
    ax9.legend()
    ax9.set_ylim([0, 100])
    plt.setp(ax9.xaxis.get_majorticklabels(), rotation=15, ha='right')

plt.tight_layout()
plt.savefig('performance_charts.png', dpi=300, bbox_inches='tight')
print("✓ Performance chart saved: performance_charts.png")

# Create a detailed metrics comparison table
print("\n" + "="*70)
print("DETAILED METRICS COMPARISON")
print("="*70)

metrics_data = []

for trades, name in [(trades_1, 'Gap Reversion'), 
                      (trades_2, 'BB Breakout'), 
                      (trades_3, 'Support/Resistance')]:
    if len(trades) > 0:
        wins = len(trades[trades['net_profit'] > 0])
        losses = len(trades[trades['net_profit'] < 0])
        win_rate = (wins / len(trades)) * 100
        
        winning = trades[trades['net_profit'] > 0]['net_profit'].sum()
        losing = abs(trades[trades['net_profit'] < 0]['net_profit'].sum())
        pf = winning / losing if losing > 0 else 0
        
        total_profit = trades['net_profit'].sum()
        avg_win = trades[trades['net_profit'] > 0]['net_profit'].mean() if wins > 0 else 0
        avg_loss = trades[trades['net_profit'] < 0]['net_profit'].mean() if losses > 0 else 0
        
        roi = (total_profit / 100000) * 100
        
        metrics_data.append({
            'Strategy': name,
            'Total Trades': len(trades),
            'Wins': wins,
            'Losses': losses,
            'Win Rate (%)': f"{win_rate:.2f}",
            'Profit Factor': f"{pf:.2f}",
            'Total Profit (₹)': f"{total_profit:,.0f}",
            'Avg Win (₹)': f"{avg_win:,.0f}",
            'Avg Loss (₹)': f"{avg_loss:,.0f}",
            'ROI (%)': f"{roi:.2f}"
        })

metrics_df = pd.DataFrame(metrics_data)
print("\n" + metrics_df.to_string(index=False))

# Save metrics to CSV
metrics_df.to_csv('strategy_comparison_metrics.csv', index=False)
print("\n✓ Metrics saved to: strategy_comparison_metrics.csv")

print("\n" + "="*70)
print("✓ Visualization complete!")
print("="*70)
