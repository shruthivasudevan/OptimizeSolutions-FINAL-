from nsepython import derivative_history
import pandas as pd
from itertools import combinations


def trade_decision(strategy: str, symbol: str, start_date: str, end_date: str, expiry_date: str):
    # symbol = "NIFTY"
    # start_date = "01-07-2024"
    # end_date = "30-07-2024"
    instrumentType = "options"
    # expiry_date = "14-Aug-2024"

    print("values", strategy, symbol, start_date, end_date, expiry_date)
    # Fetching data
    data = derivative_history(symbol, start_date, end_date, instrumentType, expiry_date)
    print("data")

    # Convert to DataFrame if necessary
    df = pd.DataFrame(data)

    # Filter for relevant columns
    df_filtered = df[['FH_STRIKE_PRICE', 'CALCULATED_PREMIUM_VAL', 'FH_OPTION_TYPE', 'FH_TIMESTAMP']]

    # Display the filtered DataFrame
    print("df_filtered", df_filtered)

    # Set display options to show all columns
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)

    print("strategy", strategy, strategy == 'Bull Call Spread')

    if strategy == 'Short Straddle':
        return Short_Straddle(df_filtered)
    elif strategy == 'Bull Call Spread':
        return Bull_Call_Spread(df)
    else:
        return Exception("unimplemented")


# ______________________________________________________________________________________________________________________#
def Bull_Call_Spread(df):
    print("bull call spread...")
    # Filter only call options ("CE")
    df_calls = df[df['FH_OPTION_TYPE'] == 'CE']

    # Prepare the new DataFrame to store the results
    results = []

    # Iterate through all combinations of call options
    for (index1, row1), (index2, row2) in combinations(df_calls.iterrows(), 2):
        # Determine which option is being bought and which is being sold based on strike prices
        if float(row1['FH_STRIKE_PRICE']) < float(row2['FH_STRIKE_PRICE']):
            bought_option = row1
            sold_option = row2
        else:
            bought_option = row2
            sold_option = row1

        # Calculate the strike difference and net premium paid
        strike_diff = abs(float(bought_option['FH_STRIKE_PRICE']) - float(sold_option['FH_STRIKE_PRICE']))
        net_premium_paid = float(bought_option['CALCULATED_PREMIUM_VAL']) - float(sold_option['CALCULATED_PREMIUM_VAL'])

        # Append data with tracking information
        results.append({
            'Strike_Price_Difference': strike_diff,
            'Net_Premium_Paid': net_premium_paid,
            'Bought_Strike_Price': bought_option['FH_STRIKE_PRICE'],
            'Bought_Premium': bought_option['CALCULATED_PREMIUM_VAL'],
            'Sold_Strike_Price': sold_option['FH_STRIKE_PRICE'],
            'Sold_Premium': sold_option['CALCULATED_PREMIUM_VAL'],
            'Bought_Timestamp': bought_option['FH_TIMESTAMP'],
            'Sold_Timestamp': sold_option['FH_TIMESTAMP']
        })

    # Convert results to DataFrame
    df_results = pd.DataFrame(results)

    # Filter out combinations where the expiration dates do not match
    df_results = df_results[df_results['Bought_Timestamp'] == df_results['Sold_Timestamp']]

    # Calculate Max Profit, Max Loss, and Breakeven
    df_results['Max_Profit'] = (df_results['Strike_Price_Difference'] - df_results['Net_Premium_Paid']) * 50
    df_results['Max_Loss'] = 50 * df_results['Net_Premium_Paid']
    df_results['Breakeven'] = df_results['Bought_Strike_Price'].astype(float) + df_results['Net_Premium_Paid']

    # Display the resulting DataFrame
    # print(df_results)

    # Choosing best option
    # Assume df_results is your DataFrame from the previous steps

    # Initialize variables to track the best option
    best_row = None
    max_profit = -float('inf')
    min_risk = float('inf')

    # Iterate through each row in the DataFrame
    for index, row in df_results.iterrows():
        # Compare current row's profit and risk with the best one found so far
        if row['Max_Profit'] > max_profit and row['Max_Loss'] < min_risk:
            best_row = row
            max_profit = row['Max_Profit']
            min_risk = row['Max_Loss']

    # Check if a best row was found
    if best_row is not None:
        # Print the results in words
        print(f"The best bull call spread option is as follows:")
        print(
            f"Buy the call option with a strike price of {best_row['Bought_Strike_Price']} and a premium of {best_row['Bought_Premium']}.")
        print(
            f"Sell the call option with a strike price of {best_row['Sold_Strike_Price']} and a premium of {best_row['Sold_Premium']}.")
        print(f"The maximum profit you can achieve with this spread is {best_row['Max_Profit']}.")
        print(f"The maximum loss you could incur is {best_row['Max_Loss']}.")
        print(f"The breakeven price for this spread is {best_row['Breakeven']}.")
        return {
            "max_profit": best_row['Max_Profit'],
            "max_loss": best_row['Max_Loss'],
            "break_even": best_row['Breakeven']
        }
    else:
        print("No suitable option found.")
        return Exception("no suitable option found.")


def Short_Straddle(df_filtered):
    # Filter puts and calls
    df_puts = df_filtered[df_filtered['FH_OPTION_TYPE'] == 'PE']
    df_calls = df_filtered[df_filtered['FH_OPTION_TYPE'] == 'CE']

    # Merge the put and call options based on strike price and expiration date
    df_short_straddle = pd.merge(df_puts, df_calls, on=['FH_STRIKE_PRICE', 'FH_TIMESTAMP'], suffixes=('_put', '_call'))

    # Calculate Max Profit
    df_short_straddle['Max_Profit'] = (df_short_straddle['CALCULATED_PREMIUM_VAL_put'] + df_short_straddle[
        'CALCULATED_PREMIUM_VAL_call']) * 50

    # Calculate Upper and Lower Breakevens
    df_short_straddle['Upper_Breakeven'] = df_short_straddle['FH_STRIKE_PRICE'].astype(float) + (
            df_short_straddle['CALCULATED_PREMIUM_VAL_put'] + df_short_straddle['CALCULATED_PREMIUM_VAL_call'])
    df_short_straddle['Lower_Breakeven'] = df_short_straddle['FH_STRIKE_PRICE'].astype(float) - (
            df_short_straddle['CALCULATED_PREMIUM_VAL_put'] + df_short_straddle['CALCULATED_PREMIUM_VAL_call'])

    # Display the resulting DataFrame
    print(df_short_straddle)

    def find_best_short_straddle(df):
        # Adding a column to represent the breakeven range
        df['Breakeven_Range'] = df['Upper_Breakeven'] - df['Lower_Breakeven']

        # Sort the DataFrame to prioritize rows with high Max Profit and wide Breakeven Range
        df_sorted = df.sort_values(by=['Max_Profit', 'Breakeven_Range'], ascending=[False, False])

        # Display the best row based on highest Max Profit and widest Breakeven Range
        best_row = df_sorted.iloc[0]

        return best_row

    # Call the function with the short straddle DataFrame
    best_straddle = find_best_short_straddle(df_short_straddle)

    if best_straddle is not None:
        # Display the best straddle information
        print(f"The best short straddle strategy is to:")
        print(
            f"Sell a call option with strike price {best_straddle['FH_STRIKE_PRICE']} at a premium of {best_straddle['CALCULATED_PREMIUM_VAL_call']}.")
        print(
            f"Sell a put option with strike price {best_straddle['FH_STRIKE_PRICE']} at a premium of {best_straddle['CALCULATED_PREMIUM_VAL_put']}.")
        print(f"The maximum profit you can achieve is {best_straddle['Max_Profit']}.")
        print(f"The breakeven range is from {best_straddle['Lower_Breakeven']} to {best_straddle['Upper_Breakeven']}.")
        return {
            "max_profit": best_straddle['Max_Profit'],
            "max_loss": best_straddle['Max_Loss'],
            "break_even": best_straddle['Upper_Breakeven']
        }
    else:
        print("No suitable option found.")
        return Exception("no suitable option found.")