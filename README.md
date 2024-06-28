# ROIC Scraper

- Supported data:
  - Income Statements
  - Balance Sheets
  - Cash Flow Statements
  - Profitability Metrics
  - Credit Metrics
  - Liquidity Metrics
  - Working Capital Metrics
  - Enterprise Value Metrics
  - Multiples
  - Per Share Data

---

### Setup

1. Clone git repository: `https://github.com/Primitive-Coding/RoicScraper.git`
2. Configure the "config.json" file. All the necessary folders will be created within the `data_export_path`.

```
    {
        "chrome_driver_path": "D:\\PATH TO CHROMEDRIVER\\chromedriver.exe",
        "data_export_path": "D:\\PATH TO EXPORT DATA\\CompanyInfo"
    }

```

3. Install the projects requirements with `pip install -r requirements.txt`

---

### Instructions

- Create a class instance. If debug is set to true, various pieces of information will be logged to confirm steps of scraping were completed.

```
    roic = RoicScraper("AAPL")
```

###### Income Statement

```
     df = roic.get_income_statement()

     # Output (**NOTE** More years are available, but are ommitted for readability)
                                        2019        2020        2021        2022        2023
    index
    Sales/Revenue/Turnover             260174.00   274515.00   365817.00   394328.00   383285.00
    Sales & Services Revenue           260174.00   274515.00   365817.00   394328.00   383285.00
    Cost of Revenue                    161782.00   169559.00   212981.00   223546.00   214137.00
    Cost of Goods & Services           161782.00   169559.00   212981.00   223546.00   214137.00
    Gross Profit                        98392.00   104956.00   152836.00   170782.00   169148.00
    Other Operating Income                   NaN         NaN         NaN         NaN         NaN
    Operating Expenses                  34462.00    38668.00    43887.00    51345.00    54847.00
    Selling General & Admin             18245.00    19916.00    21973.00    25094.00    24932.00
    Research & Development              16217.00    18752.00    21914.00    26251.00    29915.00
    Other Operating Expense                  NaN         NaN         NaN         NaN         NaN
    Operating Income (Loss)             63930.00    66288.00   108949.00   119437.00   114301.00
    NonOperating (Income) Loss          -1807.00     -803.00     -258.00      334.00      565.00
    ...
    Gross Margin (%)                       37.82       38.23       41.78       43.31       44.13
    Operating Margin (%)                   24.57       24.15       29.78       30.29       29.82
    Profit Margin (%)                      21.24       20.91       25.88       25.31       25.31
    Sales per Employee                1899080.00  1867449.00  2375435.00  2404439.00  2380652.00
    Dividend per Share                      0.76        0.81        0.87        0.92        0.95
    Depreciation Expense                12547.00    11056.00    11284.00    11104.00    11519.00
```

###### Balance Sheet

```
    df = roic.get_balance_sheet()

    # Output

                                    2019       2020       2021       2022       2023
    index
    Total Current Assets          162819.00  143713.00  134836.00  135405.00  143566.00
    Cash Cash Equivalents & STI   100557.00   90943.00   62639.00   48304.00   61555.00
    Cash & Cash Equivalents        48844.00   38016.00   34940.00   23646.00   29965.00
    ST Investments                 51713.00   52927.00   27699.00   24658.00   31590.00
    Accounts & Notes Receiv        45804.00   37445.00   51506.00   60932.00   60985.00
    ...                                 ...        ...        ...        ...        ...
    Net Debt to Equity                65.43     113.90     142.30     190.29     130.54
    Tangible Common Equity Ratio      26.73      20.17      17.97      14.36      17.63
    Current Ratio                      1.54       1.36       1.07       0.88       0.99
    Cash Conversion Cycle            -73.66     -60.57     -51.93     -63.15     -70.23
    Number of Employees           137000.00  147000.00  154000.00  164000.00  161000.00
```

###### Cash Flow

```
    df = roic.get_cash_flow()

    # Output

                                        2019       2020       2021       2022       2023
    index
    Net Income                        55256.00   57411.00   94680.00   99803.00   96995.00
    Depreciation & Amortization       12547.00   11056.00   11284.00   11104.00   11519.00
    NonCash Items                      5076.00    6517.00    2985.00   10044.00    8606.00
    StockBased Compensation            6068.00    6829.00    7906.00    9038.00   10833.00
    Deferred Income Taxes              -340.00    -215.00   -4774.00     895.00        NaN
    Asset Impairment Charge                NaN        NaN        NaN        NaN        NaN
    Other NonCash Adj                  -652.00     -97.00    -147.00     111.00   -2227.00
    Chg in NonCash Work Cap           -3488.00    5690.00   -4911.00    1200.00   -6577.00
    (Inc) Dec in Accts Receiv          3176.00    8470.00  -14028.00   -9343.00    -417.00
    (Inc) Dec in Inventories           -289.00    -127.00   -2642.00    1484.00   -1618.00
    (Inc) Dec in Prepaid Assets            NaN        NaN        NaN        NaN        NaN
    Inc (Dec) in Accts Payable        -1923.00   -4062.00   12326.00    9448.00   -1889.00
    Inc (Dec) in Other                -4452.00    1409.00    -567.00    -389.00   -2653.00
    Net Cash From Disc Ops                 NaN        NaN        NaN        NaN        NaN
    ...
    Cash (Repurchase) of Equity      -66116.00  -71478.00  -84866.00  -89402.00  -77550.00
    Increase in Capital Stock           781.00     880.00    1105.00        NaN        NaN
    Decrease in Capital Stock        -66897.00  -72358.00  -85971.00  -89402.00  -77550.00
    Other Financing Activities        -8899.00   -4723.00   -5663.00   -2428.00   -9990.00
    Cash from Financing Activities   -90976.00  -86820.00  -93353.00 -110749.00 -108488.00
    Effect of Foreign Exchange Rates       NaN        NaN        NaN        NaN        NaN
    Net Changes in Cash               24311.00  -10435.00   -3860.00  -10952.00    5760.00
    Capital Expenditures             -10495.00   -7309.00  -11085.00  -10708.00  -10959.00
    EBITDA                            76477.00   77344.00  120233.00  130541.00  125820.00
    EBITDA Margin (%)                    29.39      28.17      32.87      33.10      32.83
    Net Cash Paid for Acquisitions      624.00    1524.00      33.00     306.00        NaN
    Free Cash Flow                    58896.00   73365.00   92953.00  111443.00   99584.00
    Free Cash Flow to Firm            61902.00   75823.00   95246.00  113899.00  102938.00
    Free Cash Flow to Equity          57054.00   76827.00  104596.00  107365.00   93661.00
    Free Cash Flow per Basic Share        3.19       4.23       5.57       6.87       6.33
    Price/Free Cash Flow                 12.86      22.67      21.05      17.36      22.39
    Cash Flow to Net Income               1.26       1.41       1.10       1.22       1.14

```
