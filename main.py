#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 15:32:33 2022

@author: soidi
"""

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from pandas_datareader.data import DataReader
from datetime import datetime

class CryptoAnalysis:
    def __init__(self, crypto_list, start_date, end_date, epsilon, period):
        self.crypto_list = crypto_list
        self.data_crypto = None
        self.start_date = start_date
        self.end_date = end_date
        self.epsilon = epsilon
        self.period = period

    def import_files(self):
        
        #Download cryptocurrency data using Yahoo Finance API and save it to CSV files.
        data_frames = []
        for crypto in self.crypto_list:
            data = yf.download(f'{crypto}-EUR', start=self.start_date, end=self.end_date, period=self.period)
            data.reset_index(level=0, inplace=True)
            data['Crypto'] = crypto
            data_frames.append(data)
            data.to_csv(f'data_{crypto}.csv', index=False)

        self.data_crypto = pd.concat(data_frames)
        self.data_crypto.to_csv('data.csv', index=True)

    def calculate_indicators(self, window_sizes=[7, 30, 60, 100]):
        
        #Calculate moving averages and Bollinger Bands for each cryptocurrency.
        for crypto in self.crypto_list:
            df = self.data_crypto[self.data_crypto['Crypto'] == crypto]
            for window_size in window_sizes:
                # Calculate moving averages
                df[f'MA_{window_size}'] = df['Adj Close'].rolling(window=window_size).mean()

                # Calculate Bollinger Bands
                df[f'Upper_{window_size}'] = df[f'MA_{window_size}'] + 2 * df['Adj Close'].rolling(
                    window=window_size).std()
                df[f'Lower_{window_size}'] = df[f'MA_{window_size}'] - 2 * df['Adj Close'].rolling(
                    window=window_size).std()
                

            df.to_csv(f'{crypto}_indicators.csv', index=False)

    def calculate_percentage_change(self, window_sizes=[1, 7, 30, 180, 365]):
        
        #Calculate the percentage change for specified time intervals.        
        for crypto in self.crypto_list:
            df = self.data_crypto[self.data_crypto['Crypto'] == crypto]

            for window in window_sizes:
                # Calculate percentage change
                df[f'Change_{window}d'] = df['Adj Close'].pct_change(periods=window) * 100

            df.to_csv(f'{crypto}_percentage_change.csv', index=False)
        
    def execute_strategies(self, ma_crossover=True, bb_bounce=True):

        for crypto in self.crypto_list:
            df = pd.read_csv(f'{crypto}_indicators.csv')

            if ma_crossover:
                self.execute_ma_crossover_strategy(df, crypto)

            if bb_bounce:
                self.execute_bb_bounce_strategy(df, crypto)
            
            df.to_csv(f'{crypto}_signal.csv', index=False)

    def execute_ma_crossover_strategy(self, df, crypto):

        #Trade Strategy based on Moving Average.
        index = 0
        p_ma = 0
        df['Result_MA'] = 0
        df['Position_MA'] = ''
        df['Signal_MA'] = 0

        # Generate signals
        df['Signal_MA'][df['MA_7'] > df['MA_30']*(1+self.epsilon)] = 1  # Buy signal
        df['Signal_MA'][df['MA_7'] < df['MA_30']*(1+self.epsilon)] = -1  # Sell signal

        # Execute trades based on signals
        
        while index < len(df['Signal_MA']):
            if df['Signal_MA'].iloc[index] == 1:  # Buy signal
                p_ma = df['Adj Close'].iloc[index]  # Buy price
                df['Position_MA'].iloc[index] = "Buy"
                index = index + 1
        
                while index < len(df['Signal_MA']) and df['Signal_MA'].iloc[index] == 1:
                    df['Position_MA'].iloc[index] = "Hold"
                    index = index + 1
        
                if index < len(df['Signal_MA']):
                    df['Result_MA'].iloc[index] = df['Adj Close'].iloc[index] - p_ma
                    df['Position_MA'].iloc[index] = "Close"
        
            elif df['Signal_MA'].iloc[index] == -1:  # Sell signal
                p_ma = df['Adj Close'].iloc[index]  # Sell price
                df['Position_MA'].iloc[index] = "Sell"
                index = index + 1
        
                while index < len(df['Signal_MA']) and df['Signal_MA'].iloc[index] == -1:
                    df['Position_MA'].iloc[index] = "Hold"
                    index = index + 1
        
                if index < len(df['Signal_MA']):
                    df['Result_MA'].iloc[index] = p_ma - df['Adj Close'].iloc[index]
                    df['Position_MA'].iloc[index] = "Close"
        
            else:
                df['Position_MA'].iloc[index] = "Wait"
                index = index + 1
        
            if index >= len(df['Signal_MA']):
                break
                

        # Print the trading signals
        print(f"Trading signals for {crypto} based on Moving Average Crossover:")
        print(df[['Date', 'Signal_MA', 'Position_MA']])


    def execute_bb_bounce_strategy(self, df, crypto):
        
        #Execute trading strategy based on Bollinger Bands bounce.
        index = 0
        p_bb = 0
        df['Signal_BB'] = 0
        df['Result_BB'] = 0
        df['Position_BB'] = ''

        # Generate signals
        df['Signal_BB'][df['Adj Close'] < df['Lower_30']*(1+self.epsilon)] = 1  # Buy signal
        df['Signal_BB'][df['Adj Close'] > df['Upper_30']*(1-self.epsilon)] = -1  # Sell signal

        # Execute trades based on signals
        
        while index < len(df['Signal_MA']):
            if df['Signal_BB'].iloc[index] == 1:  # Buy signal
                p_bb = df['Adj Close'].iloc[index]  # Buy price
                df['Position_BB'].iloc[index] = "Buy"
                index = index + 1
        
                while index < len(df['Signal_BB']) and df['Signal_BB'].iloc[index] == 1:
                    df['Position_BB'].iloc[index] = "Hold"
                    index = index + 1
        
                if index < len(df['Signal_BB']):
                    df['Result_BB'].iloc[index] = df['Adj Close'].iloc[index] - p_bb
                    df['Position_BB'].iloc[index] = "Close"
        
            elif df['Signal_BB'].iloc[index] == -1:  # Sell signal
                p_BB = df['Adj Close'].iloc[index]  # Sell price
                df['Position_BB'].iloc[index] = "Sell"
                index = index + 1
        
                while index < len(df['Signal_BB']) and df['Signal_BB'].iloc[index] == -1:
                    df['Position_BB'].iloc[index] = "Hold"
                    index = index + 1
        
                if index < len(df['Signal_BB']):
                    df['Result_BB'].iloc[index] = p_BB - df['Adj Close'].iloc[index]
                    df['Position_BB'].iloc[index] = "Close"
        
            else:
                df['Position_BB'].iloc[index] = "Wait"
                index = index + 1
        
            if index >= len(df['Signal_BB']):
                break


        # Print the trading signals
        print(f"Trading signals for {crypto} based on Bollinger Bands Bounce:")
        print(df[['Date', 'Signal_BB', 'Position_BB', 'Result_BB']])
        



    
def main():
    crypto_list = ['BTC', 'ETH', 'BNB', 'USDT']
    start_date = '2021-01-01'
    end_date = '2022-01-01'
    epsilon = 0.1
    period = '1d'
    crypto_analysis = CryptoAnalysis(crypto_list, start_date, end_date, epsilon, period)
    crypto_analysis.import_files()
    crypto_analysis.calculate_indicators()
    crypto_analysis.calculate_percentage_change()
    crypto_analysis.execute_strategies(ma_crossover=True, bb_bounce=True)





if __name__ == "__main__":
    main()
