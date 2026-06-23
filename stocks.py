import yfinance  as yf 
import requests 
import matplotlib.pylab as plt
import numpy as np
import pandas as pd
import fredapi as fred    
import decimal
from datetime import date
import re
import sqlalchemy as sq
import pyodbc as py
from DB import DB


class Stocks:
    
    def __init__(self):
         self
      
    def get_ky(self):
        f_key = pd.read_csv('../src/API_KEY.csv')
        ky = f_key['Fred_key'][0]
        formatted_date_1 = str(date.today().strftime("%d-%m-%Y"))
        print(formatted_date_1)
        return ky
    
    #returns current date formatted as YYYYY-MM-DD
    def get_today(self):
        formatted_date_1 = str(date.today().strftime("%d-%m-%Y"))
        return formatted_date_1
    
    #test function for api keys
    def dt_ky(self, dt:date):
        print()
        
    #FEDERAL RESERVE TEST FUNCTION ON US DOLLAR INDEX.
    def get_fed(self):
        f = fred.Fred(api_key=self.get_ky())
        usd_fred = f.get_series('DTWEXBGS', observation_start='2015-01-01'
                                ,observation_end=self.get_today())
        print(type(usd_fred))
        usd_srs = pd.Series(usd_fred, name=['Dt','USD'])
        fed =usd_fred.to_frame()
        print(usd_fred)
        

    def ticks_plt(self)->pd.DataFrame:
        ticker_lst =['PL=F', 'GC=F','SI=F','HG=F','PA=F', 'CL=F', 'BZ=F' ,'DXY']
        dt = yf.download(ticker_lst, start='2015-01-01', group_by='ticker')
        #Download historical data for the last year
        dt = pd.DataFrame(data=dt)
        #dt_dt = dt.reset_index()
        return dt


     #Primary function to pull tickers from yfinanace.
     #Returns Dataframe with reshaped index...dataframe comes in series with main index of date.
     #Yfinance returns a series with Date the index requires reshape fn().
     #CL=F is ticker for WTI crude oil, BZ=F=Brent crude oil. 
    def ticks_sql(self)->pd.DataFrame:
        ticker_lst =['PL=F', 'GC=F','SI=F','HG=F','PA=F', 'CL=F'
                     , 'BZ=F' ,'NDX', 'XEL', 'CVX', 'B', 'MP', 'DJI']
        dt = yf.download(ticker_lst, start='2010-01-01', group_by='ticker')
        #Download historical data for the last year
        dt = pd.DataFrame(data=dt)
        dt_f = dt.reset_index()
        dt_f.columns = ['_'.join(col).strip() for col in dt_f.columns.values] #transform white space to underscore.
        dt_f.columns = ["".join(col).replace('=','_') for col in dt_f.columns.values] #change '=' to underscore.
        dt_f = np.round(dt_f, decimals=2)
        #print(dt_f.columns)
        return dt_f    
        
    #method for plotting
    def plotting(self, dt: pd.DataFrame):
        y1= dt['GC_F']['Close']
        y2 = dt['PL_F']['Close']
        y3 = dt['SI_F']['Close']
        #y4 = dt['RTX']['Close']
        cmap = plt.cm.RdYlGn #tooltip
        plt.figure(figsize=(12, 8))
        plt.plot(y1, label='Gold Price', color='gold')
        plt.plot(y2, label='Platinum', color='gray')
        plt.plot(y3, label='USD', color='green')
        #plt.plot(y4, label='Raytheon', color='orange')
        plt.title('Precious Metals to USD Index Yahoo Finance')
        plt.xlabel('Date')
        plt.ylabel('US Dollar')
        #plt.ylabel('Raytheon')
        y_tick_locations = np.arange(500, 4000, 500) #start, stop, step
        plt.yticks(y_tick_locations)
        plt.legend()
        plt.grid(True)
        plt.show()
        #print(dt.head(10))
        
     #USE DB CLASS   
     #insert stock/futures data into SQL-server.  
     #creates datekey for database date dimension.      
    def sql_insert(self,df:pd.DataFrame):
        SERVER= "DESKTOP-03RVSDU\SQLEXPRESS"
        DB_NAME = "Labor_Stats"
        #Call DB class with server and name parameters
        db = DB(server=SERVER, db_nm=DB_NAME)
        cnx = db.sql_cnx()
        df.rename(columns={'Date_': 'Dt'}, inplace=True)
        df['Dt'] = pd.to_datetime(df['Dt'], format='%d/%m/%Y').dt.date
        #create datekey for date dimension...turn pandas date int yyyymmdd e.g. (20260210)
        df['datekey'] = pd.to_datetime(df['Dt'], format='%Y%m%d').dt.strftime('%Y%m%d').astype(int)
        df.to_sql(name='Commodity', schema='dbo'
            , con=cnx, if_exists='replace', index=False,index_label=False)
        #close connection DB:Close()
        print(sq.inspect(cnx).has_table('Commodity_Test'))
        db.close_cnx()    
    
    def csv_x(self, df:pd.DataFrame):
        df['Gld_Close'] = df['GC=F_Close'].round(2)
        df.to_csv('Silver_Price.csv', columns=['Date_', 'Gld_Close'])
        
        
    #PLEASE USE THIS METHOD IF DB CLASS IS NOT WORKNG 
    #USE FOR ADHOC PURPOSES ONLY.
    def insert_db(self,df:pd.DataFrame):
        SERVER= "DESKTOP-03RVSDU\SQLEXPRESS"
        DB_NAME = "Labor_Stats"
        conn_str = f"mssql+pyodbc://{SERVER}/{DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server"
        engine = sq.create_engine(conn_str)
        #cast to date yyyy-mm-dd
        cnx = engine.connect()
        #df.rename(columns={'SI=F_Close': 'SI_Close', 'SI=F_Volume': 'SI_Vol',
         #                  'GC=F_Close': 'GC_Close', 'GC=F_Volume':'GC_Vol', 'Date_': 'Dt'}, inplace=True)
        df.rename(columns={'Date_': 'Dt'}, inplace=True)
        df['Dt'] = pd.to_datetime(df['Dt'], format='%d/%m/%Y')
        df.to_sql(name='Commodity', schema='dbo'
            , con=cnx, if_exists='replace', index=False,index_label=False)
        cnx.close()
        
        
st = Stocks()
#df = st.ticks_plt()
df = st.ticks_sql()
#st.plotting(df)
#st.csv_x(df=df)
st.sql_insert(df=df)
#st.insert_db(df=df)
