import os
import requests
import csv
import json
import numpy as np

from datetime import datetime, timedelta
from requests import HTTPError, RequestException


class CurrencyDataManager:

    @staticmethod
    def update_exchange_rates():
        try:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

            currency_codes = ['USD', 'EUR', 'CHF']
            urls = [f"http://api.nbp.pl/api/exchangerates/rates/A/{code}/{start_date}/{end_date}/" for code in
                    currency_codes]
            exchange_rates_data = {}

            for i, url in enumerate(urls):
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                except HTTPError as http_err:
                    update_error = f"HTTP error occurred while fetching data for {currency_codes[i]}: {http_err}"
                    continue
                except ConnectionError as conn_err:
                    update_error = f"Connection error occurred while fetching data for {currency_codes[i]}: {conn_err}"
                    continue
                except json.JSONDecodeError as json_err:
                    update_error = f"JSON decoding error occurred: {json_err}"
                    continue
                except RequestException as req_err:
                    update_error = f"Request error occurred while fetching data for {currency_codes[i]}: {req_err}"
                    continue

                try:
                    data = json.loads(response.content.decode('utf-8'))

                    if 'rates' in data:
                        rates = data['rates']
                        for rate in rates:
                            rate['effectiveDate'] = datetime.strptime(rate['effectiveDate'], "%Y-%m-%d").date()

                        exchange_rates_data[currency_codes[i]] = rates
                    else:
                        update_error = f"No data about exchange rates for: {currency_codes[i]}."

                except json.JSONDecodeError as json_err:
                    update_error = f"JSON decoding error occurred for {currency_codes[i]}: {json_err}"

            for currency_code_to_calculate in ['CHF', 'EUR']:
                if 'USD' in exchange_rates_data and currency_code_to_calculate in exchange_rates_data:
                    for rate_usd in exchange_rates_data['USD']:
                        date_usd = rate_usd['effectiveDate']
                        rate_currency = next(
                            (d['mid'] for d in exchange_rates_data[currency_code_to_calculate] if
                             d['effectiveDate'] == date_usd),
                            None)
                        if rate_currency is not None:
                            rate_usd[f'{currency_code_to_calculate}_USD'] = rate_currency / rate_usd['mid']

            all_dates = sorted(set(rate['effectiveDate'] for rates in exchange_rates_data.values() for rate in rates),
                               reverse=True)

            with open('all_currency_data.csv', 'w', newline='') as csvfile:
                fieldnames = ['date', 'USD/PLN', 'EUR/PLN', 'CHF/PLN', 'CHF/USD', 'EUR/USD']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for date in all_dates:
                    row = {'date': date.strftime("%Y-%m-%d")}

                    for code in currency_codes:
                        rate = next((d['mid'] for d in exchange_rates_data[code] if d['effectiveDate'] == date), None)
                        row[f'{code}/PLN'] = rate

                    for rate_usd in exchange_rates_data['USD']:
                        date_usd = rate_usd['effectiveDate']

                        if date_usd == date:
                            chf_usd_rate = rate_usd.get('CHF_USD')
                            eur_usd_rate = rate_usd.get('EUR_USD')

                            if chf_usd_rate is not None and eur_usd_rate is not None:
                                row['CHF/USD'] = round(chf_usd_rate, 4)
                                row['EUR/USD'] = round(eur_usd_rate, 4)
                            break

                    writer.writerow(row)

        except Exception as e:
            update_error = f"An unexpected error occurred: {e}"

        if 'update_error' in locals():
            return update_error

    @staticmethod
    def save_selected_columns(selected_columns):
        script_dir = os.path.dirname(os.path.realpath(__file__))
        input_file = os.path.join(script_dir, 'all_currency_data.csv')
        output_file = os.path.join(script_dir, 'selected_currency_data.csv')

        try:
            with open(input_file, 'r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                selected_data = [{col: row[col] for col in selected_columns + ['date']} for row in reader]

            statistics = CurrencyDataManager.__calculate_statistics(selected_columns, selected_data)

            with open(output_file, 'w', newline='') as csvfile:
                fieldnames = ['date'] + selected_columns
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(selected_data)
            return statistics

        except FileNotFoundError:
            saving_error = f"Input file not found: {input_file}"
        except Exception as e:
            saving_error = f"An unexpected error occurred: {e}"

        if 'saving_error' in locals():
            return saving_error

    @staticmethod
    def __calculate_statistics(columns, data):
        stats = {}
        for col in columns:
            values = [float(row[col]) for row in data if row[col].replace('.', '', 1).isdigit()]
            if values:
                stats[col + '_mean'] = np.mean(values)
                stats[col + '_median'] = np.median(values)
                stats[col + '_min'] = np.min(values)
                stats[col + '_max'] = np.max(values)
            else:
                stats[col + '_mean'] = stats[col + '_median'] = stats[col + '_min'] = stats[col + '_max'] = None
        return stats
CurrencyDataManager.update_exchange_rates()