import os
import json
import numpy as np
import pandas as pd

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException


class RoicScraper:
    def __init__(self, ticker: str, country: str = "US", debug: bool = False) -> None:
        self.ticker = ticker.upper()
        self.country = country.upper()
        self.debug = debug
        self.base_url = f"https://roic.ai/quote/{self.ticker}:{self.country}"
        self.chrome_driver_path = self._get_chrome_driver_path()
        self.base_export_path = self._get_data_export_path()
        self.ticker_folder = f"{self.base_export_path}\\{self.ticker}"
        os.makedirs(self.base_export_path, exist_ok=True)  # Create folder for ROIC data
        os.makedirs(self.ticker_folder, exist_ok=True)  # Create folder for ticker

        """ -- Chromedriver options -- """
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument("--disable-gpu")

    """-----------------------------------"""

    def _get_data_export_path(self):
        with open("config.json", "r") as file:
            data = json.load(file)
        return data["data_export_path"]

    """-----------------------------------"""
    """----------------------------------- Browser Operations -----------------------------------"""

    def _get_chrome_driver_path(self):
        with open("config.json", "r") as file:
            data = json.load(file)
        return data["chrome_driver_path"]

    def _create_browser(self, url=None):
        """
        :param url: The website to visit.
        :return: None
        """
        service = Service(executable_path=self.chrome_driver_path)
        self.browser = webdriver.Chrome(service=service, options=self.chrome_options)
        # Default browser route
        if url == None:
            self.browser.get(url=self.sec_annual_url)
        # External browser route
        else:
            self.browser.get(url=url)

    def _clean_close(self) -> None:
        self.browser.close()
        self.browser.quit()

    def _read_data(
        self, xpath: str, wait: bool = False, _wait_time: int = 5, tag: str = ""
    ) -> str:
        """
        :param xpath: Path to the web element.
        :param wait: Boolean to determine if selenium should wait until the element is located.
        :param wait_time: Integer that represents how many seconds selenium should wait, if wait is True.
        :return: (str) Text of the element.
        """

        if wait:
            try:
                data = (
                    WebDriverWait(self.browser, _wait_time)
                    .until(EC.presence_of_element_located((By.XPATH, xpath)))
                    .text
                )
            except TimeoutException:
                print(f"[Failed Xpath] {xpath}")
                if tag != "":
                    print(f"[Tag]: {tag}")
                raise NoSuchElementException("Element not found")
            except NoSuchElementException:
                print(f"[Failed Xpath] {xpath}")
                return "N\A"
        else:
            try:
                data = self.browser.find_element("xpath", xpath).text
            except NoSuchElementException:
                data = "N\A"
        # Return the text of the element found.
        return data

    def _click_button(
        self,
        xpath: str,
        wait: bool = False,
        _wait_time: int = 5,
        scroll: bool = False,
        tag: str = "",
    ) -> None:
        """
        :param xpath: Path to the web element.
        :param wait: Boolean to determine if selenium should wait until the element is located.
        :param wait_time: Integer that represents how many seconds selenium should wait, if wait is True.
        :return: None. Because this function clicks the button but does not return any information about the button or any related web elements.
        """

        if wait:
            try:
                element = WebDriverWait(self.browser, _wait_time).until(
                    EC.presence_of_element_located((By.XPATH, xpath))
                )
                # If the webdriver needs to scroll before clicking the element.
                if scroll:
                    self.browser.execute_script("arguments[0].click();", element)
                element.click()
            except TimeoutException:
                print(f"[Failed Xpath] {xpath}")
                if tag != "":
                    print(f"[Tag]: {tag}")
                raise NoSuchElementException("Element not found")
        else:
            element = self.browser.find_element("xpath", xpath)
            if scroll:
                self.browser.execute_script("arguments[0].click();", element)
            element.click()

    """----------------------------------- Page Scraping -----------------------------------"""

    def _scrape_summary_page(self):
        self._create_browser(self.base_url)
        row_index = 1
        col_index = 3
        row_label_xpath = "/html/body/div[1]/div/div[2]/div[1]/div[2]/div/div/table/tbody/tr[{}]/td[1]/div/div[2]/span"
        col_label_xpath = "/html/body/div[1]/div/div[2]/div[1]/div[2]/div/div/table/thead/tr/th[{}]/div/span"
        data_xpath = "/html/body/div[1]/div/div[2]/div[1]/div[2]/div/div/table/tbody/tr[{}]/td[{}]/div/span"

        labels = self._get_table_labels(
            row_label_xpath, col_label_xpath, row_index, col_index
        )

        df = self._get_table_data(data_xpath, row_index, col_index, labels)
        self._clean_close()
        return df

    def get_summary(self):
        path = f"{self.ticker_folder}\\summary.csv"
        try:
            df = pd.read_csv(path).set_index("index")
            return df
        except FileNotFoundError:
            df = self._scrape_summary_page()
            df.to_csv(path)
            return df

    def update_summary(self):
        path = f"{self.ticker_folder}\\summary.csv"
        df = self._scrape_summary_page()
        df.to_csv(path)
        return df

    """----------------------------------- Scrape Income Statement  -----------------------------------"""

    def _scrape_income_statement(self):
        self._create_browser(f"{self.base_url}/financials")
        row_index = 1
        col_index = 3
        row_label_xpath = "/html/body/div[1]/div/div[2]/div[3]/div[1]/div/div/div/table/tbody/tr[{}]/td[1]/div/div[2]/span"
        col_label_xpath = "/html/body/div[1]/div/div[2]/div[3]/div[1]/div/div/div/table/thead/tr/th[{}]/div/span"
        data_xpath = "/html/body/div[1]/div/div[2]/div[3]/div[1]/div/div/div/table/tbody/tr[{}]/td[{}]/div/span"
        labels = self._get_table_labels(
            row_label_xpath, col_label_xpath, row_index, col_index
        )
        df = self._get_table_data(data_xpath, row_index, col_index, labels)
        self._clean_close()
        return df

    def get_income_statement(self):
        path = f"{self.ticker_folder}\\income_statement.csv"
        try:
            df = pd.read_csv(path).set_index("index")
            return df
        except FileNotFoundError:
            df = self._scrape_income_statement()
            df.to_csv(path)
            return df

    def update_income_statement(self):
        path = f"{self.ticker_folder}\\income_statement.csv"
        df = self._scrape_income_statement()
        df.to_csv(path)
        return df

    """----------------------------------- Scrape Balance Sheet  -----------------------------------"""

    def _scrape_balance_sheet(self):
        self._create_browser(f"{self.base_url}/financials")
        row_index = 1
        col_index = 3
        row_label_xpath = "/html/body/div[1]/div/div[2]/div[3]/div[2]/div/div/div/table/tbody/tr[{}]/td[1]/div/div[2]/span"
        col_label_xpath = "/html/body/div[1]/div/div[2]/div[3]/div[2]/div/div/div/table/thead/tr/th[{}]/div/span"
        data_xpath = "/html/body/div[1]/div/div[2]/div[3]/div[2]/div/div/div/table/tbody/tr[{}]/td[{}]/div/span"
        labels = self._get_table_labels(
            row_label_xpath, col_label_xpath, row_index, col_index
        )
        df = self._get_table_data(data_xpath, row_index, col_index, labels)
        self._clean_close()
        return df

    def get_balance_sheet(self):
        path = f"{self.ticker_folder}\\balance_sheet.csv"
        try:
            df = pd.read_csv(path).set_index("index")
            return df
        except FileNotFoundError:
            df = self._scrape_balance_sheet()
            df.to_csv(path)
            return df

    def update_balance_sheet(self):
        path = f"{self.ticker_folder}\\balance_sheet.csv"
        df = self._scrape_balance_sheet()
        df.to_csv(path)
        return df

    """----------------------------------- Scrape Cash Flow  -----------------------------------"""

    def _scrape_cash_flow(self):
        self._create_browser(f"{self.base_url}/financials")
        row_index = 1
        col_index = 3
        row_label_xpath = "/html/body/div[1]/div/div[2]/div[3]/div[3]/div/div/div/table/tbody/tr[{}]/td[1]/div/div[2]/span"
        col_label_xpath = "/html/body/div[1]/div/div[2]/div[3]/div[3]/div/div/div/table/thead/tr/th[{}]/div/span"
        data_xpath = "/html/body/div[1]/div/div[2]/div[3]/div[3]/div/div/div/table/tbody/tr[{}]/td[{}]/div/span"
        labels = self._get_table_labels(
            row_label_xpath, col_label_xpath, row_index, col_index
        )
        df = self._get_table_data(data_xpath, row_index, col_index, labels)
        self._clean_close()
        return df

    def get_cash_flow(self):
        path = f"{self.ticker_folder}\\cash_flow.csv"
        try:
            df = pd.read_csv(path).set_index("index")
            return df
        except FileNotFoundError:
            df = self._scrape_cash_flow()
            df.to_csv(path)
            return df

    def update_cash_flow(self):
        path = f"{self.ticker_folder}\\cash_flow.csv"
        df = self._scrape_cash_flow()
        df.to_csv(path)
        return df

    """----------------------------------- Scrape Profitability  -----------------------------------"""

    def _scrape_profitability(self):
        self._create_browser(f"{self.base_url}/ratios")
        row_index = 1
        col_index = 3
        row_label_xpath = "/html/body/div[1]/div/div[2]/div[3]/div[1]/div/div/div/table/tbody/tr[{}]/td[1]/div/div[2]/span"
        col_label_xpath = "/html/body/div[1]/div/div[2]/div[3]/div[1]/div/div/div/table/thead/tr/th[{}]/div/span"
        data_xpath = "/html/body/div[1]/div/div[2]/div[3]/div[1]/div/div/div/table/tbody/tr[{}]/td[{}]/div/span"
        labels = self._get_table_labels(
            row_label_xpath, col_label_xpath, row_index, col_index
        )
        df = self._get_table_data(data_xpath, row_index, col_index, labels)
        self._clean_close()
        return df

    def get_profitability(self):
        path = f"{self.ticker_folder}\\profitability.csv"
        try:
            df = pd.read_csv(path).set_index("index")
            return df
        except FileNotFoundError:
            df = self._scrape_profitability()
            df.to_csv(path)
            return df

    def update_profitability(self):
        path = f"{self.ticker_folder}\\profitability.csv"
        df = self._scrape_profitability()
        df.to_csv(path)
        return df

    """----------------------------------- Scrape Credit  -----------------------------------"""

    def _scrape_credit(self):
        self._create_browser(f"{self.base_url}/ratios")
        row_index = 1
        col_index = 3
        row_label_xpath = "/html/body/div[1]/div/div[2]/div[3]/div[2]/div/div/div/table/tbody/tr[{}]/td[1]/div/div[2]/span"
        col_label_xpath = "/html/body/div[1]/div/div[2]/div[3]/div[2]/div/div/div/table/thead/tr/th[{}]/div/span"
        data_xpath = "/html/body/div[1]/div/div[2]/div[3]/div[2]/div/div/div/table/tbody/tr[{}]/td[{}]/div/span"
        labels = self._get_table_labels(
            row_label_xpath, col_label_xpath, row_index, col_index
        )
        df = self._get_table_data(data_xpath, row_index, col_index, labels)
        self._clean_close()
        return df

    def get_credit(self):
        path = f"{self.ticker_folder}\\credit.csv"
        try:
            df = pd.read_csv(path).set_index("index")
            return df
        except FileNotFoundError:
            df = self._scrape_credit()
            df.to_csv(path)
            return df

    def update_credit(self):
        path = f"{self.ticker_folder}\\credit.csv"
        df = self._scrape_credit()
        df.to_csv(path)
        return df

    """----------------------------------- Scrape Liquidity  -----------------------------------"""

    def _scrape_liquidity(self):
        self._create_browser(f"{self.base_url}/ratios")
        row_index = 1
        col_index = 3
        row_label_xpath = "/html/body/div[1]/div/div[2]/div[3]/div[3]/div/div/div/table/tbody/tr[{}]/td[1]/div/div[2]/span"
        col_label_xpath = "/html/body/div[1]/div/div[2]/div[3]/div[3]/div/div/div/table/thead/tr/th[{}]/div/span"
        data_xpath = "/html/body/div[1]/div/div[2]/div[3]/div[3]/div/div/div/table/tbody/tr[{}]/td[{}]/div/span"
        labels = self._get_table_labels(
            row_label_xpath, col_label_xpath, row_index, col_index
        )
        df = self._get_table_data(data_xpath, row_index, col_index, labels)
        self._clean_close()
        return df

    def get_liquidity(self):
        path = f"{self.ticker_folder}\\liquidity.csv"
        try:
            df = pd.read_csv(path).set_index("index")
            return df
        except FileNotFoundError:
            df = self._scrape_liquidity()
            df.to_csv(path)
            return df

    def update_liquidity(self):
        path = f"{self.ticker_folder}\\liquidity.csv"
        df = self._scrape_liquidity()
        df.to_csv(path)
        return df

    """----------------------------------- Scrape Working Capital  -----------------------------------"""

    def _scrape_working_capital(self):
        self._create_browser(f"{self.base_url}/ratios")
        row_index = 1
        col_index = 3
        row_label_xpath = "/html/body/div[1]/div/div[2]/div[3]/div[4]/div/div/div/table/tbody/tr[{}]/td[1]/div/div[2]/span"
        col_label_xpath = "/html/body/div[1]/div/div[2]/div[3]/div[4]/div/div/div/table/thead/tr/th[{}]/div/span"
        data_xpath = "/html/body/div[1]/div/div[2]/div[3]/div[4]/div/div/div/table/tbody/tr[{}]/td[{}]/div/span"
        labels = self._get_table_labels(
            row_label_xpath, col_label_xpath, row_index, col_index
        )
        df = self._get_table_data(data_xpath, row_index, col_index, labels)
        self._clean_close()
        return df

    def get_working_capital(self):
        path = f"{self.ticker_folder}\\working_capital.csv"
        try:
            df = pd.read_csv(path).set_index("index")
            return df
        except FileNotFoundError:
            df = self._scrape_working_capital()
            df.to_csv(path)
            return df

    def update_working_capital(self):
        path = f"{self.ticker_folder}\\working_capital.csv"
        df = self._scrape_working_capital()
        df.to_csv(path)
        return df

    """----------------------------------- Scrape Enterprise Value  -----------------------------------"""

    def _scrape_enterprise_value(self):
        self._create_browser(f"{self.base_url}/ratios")
        row_index = 1
        col_index = 3
        row_label_xpath = "/html/body/div[1]/div/div[2]/div[3]/div[5]/div/div/div/table/tbody/tr[{}]/td[1]/div/div[2]/span"
        col_label_xpath = "/html/body/div[1]/div/div[2]/div[3]/div[5]/div/div/div/table/thead/tr/th[{}]/div/span"
        data_xpath = "/html/body/div[1]/div/div[2]/div[3]/div[5]/div/div/div/table/tbody/tr[{}]/td[{}]/div/span"
        labels = self._get_table_labels(
            row_label_xpath, col_label_xpath, row_index, col_index
        )
        df = self._get_table_data(data_xpath, row_index, col_index, labels)
        self._clean_close()
        return df

    def get_enterprise_value(self):
        path = f"{self.ticker_folder}\\enterprise_value.csv"
        try:
            df = pd.read_csv(path).set_index("index")
            return df
        except FileNotFoundError:
            df = self._scrape_enterprise_value()
            df.to_csv(path)
            return df

    def update_enterprise_value(self):
        path = f"{self.ticker_folder}\\enterprise_value.csv"
        df = self._scrape_enterprise_value()
        df.to_csv(path)
        return df

    """----------------------------------- Scrape Multiples  -----------------------------------"""

    def _scrape_multiples(self):
        self._create_browser(f"{self.base_url}/ratios")
        row_index = 1
        col_index = 3
        row_label_xpath = "/html/body/div[1]/div/div[2]/div[3]/div[6]/div/div/div/table/tbody/tr[{}]/td[1]/div/div[2]/span"
        col_label_xpath = "/html/body/div[1]/div/div[2]/div[3]/div[6]/div/div/div/table/thead/tr/th[{}]/div/span"
        data_xpath = "/html/body/div[1]/div/div[2]/div[3]/div[6]/div/div/div/table/tbody/tr[{}]/td[{}]/div/span"
        labels = self._get_table_labels(
            row_label_xpath, col_label_xpath, row_index, col_index
        )
        df = self._get_table_data(data_xpath, row_index, col_index, labels)
        self._clean_close()
        return df

    def get_multiples(self):
        path = f"{self.ticker_folder}\\multiples.csv"
        try:
            df = pd.read_csv(path).set_index("index")
            return df
        except FileNotFoundError:
            df = self._scrape_multiples()
            df.to_csv(path)
            return df

    def update_multiples(self):
        path = f"{self.ticker_folder}\\multiples.csv"
        df = self._scrape_multiples()
        df.to_csv(path)
        return df

    """----------------------------------- Scrape Per Share Data-----------------------------------"""

    def _scrape_per_share_data(self):
        self._create_browser(f"{self.base_url}/ratios")
        row_index = 1
        col_index = 3
        row_label_xpath = "/html/body/div[1]/div/div[2]/div[3]/div[7]/div/div/div/table/tbody/tr[{}]/td[1]/div/div[2]/span"
        col_label_xpath = "/html/body/div[1]/div/div[2]/div[3]/div[7]/div/div/div/table/thead/tr/th[{}]/div/span"
        data_xpath = "/html/body/div[1]/div/div[2]/div[3]/div[7]/div/div/div/table/tbody/tr[{}]/td[{}]/div/span"
        labels = self._get_table_labels(
            row_label_xpath, col_label_xpath, row_index, col_index
        )
        df = self._get_table_data(data_xpath, row_index, col_index, labels)
        self._clean_close()
        return df

    def get_per_share_data(self):
        path = f"{self.ticker_folder}\\per_share_data.csv"
        try:
            df = pd.read_csv(path).set_index("index")
            return df
        except FileNotFoundError:
            df = self._scrape_per_share_data()
            df.to_csv(path)
            return df

    def update_per_share_data(self):
        path = f"{self.ticker_folder}\\per_share_data.csv"
        df = self._scrape_per_share_data()
        df.to_csv(path)
        return df

    """----------------------------------- Financial Statements Page -----------------------------------"""

    def get_all_financial_statements(self, update: bool = False) -> dict:

        if update:
            income_statement = self.update_income_statement()
            balance_sheet = self.update_balance_sheet()
            cash_flow = self.update_cash_flow()
        else:
            income_statement = self.get_income_statement()
            balance_sheet = self.get_balance_sheet()
            cash_flow = self.get_cash_flow()

        return {
            "income_statement": income_statement,
            "balance_sheet": balance_sheet,
            "cash_flow": cash_flow,
        }

    """----------------------------------- Ratios Page -----------------------------------"""

    def get_all_ratios_data(self, update: bool = False) -> dict:
        if update:
            profitability = self.update_profitability()
            credit = self.update_credit()
            liquidity = self.update_liquidity()
            working_capital = self.update_working_capital()
            enterprise_value = self.update_enterprise_value()
            multiples = self.update_multiples()
            per_share_data = self.update_per_share_data()
        else:
            profitability = self.get_profitability()
            credit = self.get_credit()
            liquidity = self.get_liquidity()
            working_capital = self.get_working_capital()
            enterprise_value = self.get_enterprise_value()
            multiples = self.get_multiples()
            per_share_data = self.get_per_share_data()

        return {
            "profitability": profitability,
            "credit": credit,
            "liquidity": liquidity,
            "working_capital": working_capital,
            "enterprise_value": enterprise_value,
            "multiples": multiples,
            "per_share_data": per_share_data,
        }

    """----------------------------------- Scraping Utilities -----------------------------------"""

    def _get_table_data(
        self, data_xpath: str, row_index: int, col_index: int, labels: dict
    ) -> pd.DataFrame:

        row_labels = labels["rows"]
        col_labels = labels["cols"]

        _start_col_index = col_index

        df = pd.DataFrame(columns=col_labels).set_index("index")
        for row in row_labels:
            for col in col_labels[1:]:  # Skip the 'index' element.
                xpath = data_xpath.format(row_index, col_index)
                data = self._read_data(xpath)
                if "," in data:
                    data = data.replace(",", "")
                df.loc[row, col] = data
                col_index += 1
            col_index = _start_col_index
            row_index += 1

        df.replace("- -", np.nan, inplace=True)
        return df

    def _get_table_labels(
        self, row_xpath: str, col_xpath: str, row_index: int, col_index: int
    ):

        # Scrape the row labels.
        row_scraping = True
        rows = []
        while row_scraping:
            row_data = self._read_data(row_xpath.format(row_index))
            if row_data != "N\\A":
                if "," in row_data:
                    row_data = row_data.replace(",", "")
                if "+" in row_data:
                    row_data = row_data.replace("+", "")
                if "-" in row_data:
                    row_data = row_data.replace("-", "")
                if row_data[0] == " ":
                    row_data = row_data[1:]  # Skip the empty space
                rows.append(row_data)
            else:
                row_scraping = False
            row_index += 1

        # Scrape the column labels
        col_scraping = True
        cols = ["index"]
        while col_scraping:
            col_data = self._read_data(col_xpath.format(col_index))
            if col_data != "N\\A":
                col_data = col_data.split(" ")[0]
                cols.append(col_data)
            else:
                col_scraping = False
            col_index += 1

        return {
            "rows": rows,
            "cols": cols,
        }

    """----------------------------------- Metric Calculations -----------------------------------"""

    def calc_growth(self, values: pd.Series) -> pd.Series:

        value_type = type(values.iloc[0])
        print(f"Values: {values}   {value_type}")

        if value_type == np.float64:
            change = values.pct_change()
            return change
        else:
            print(f"EDGE CASE: {value_type}")


if __name__ == "__main__":

    roic = RoicScraper("AAPL")
    df = roic.get_cash_flow()
    cols = df.columns.to_list()

    cols = cols[-5:]

    print(f"{df[cols]}")
    # roic.calc_growth(df.loc["Sales & Services Revenue"])
