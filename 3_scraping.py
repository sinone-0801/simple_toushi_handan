import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime

def parse_value(value_text):
    """
    PERまたはPBR値をパースする関数
    赤字の場合は -1 を返す
    """
    value_text = value_text.strip()
    if value_text == '赤字':
        return -1
    # カンマを除去してから数値に変換
    return float(value_text.replace('倍', '').replace(',', ''))

def parse_financial_value(value_text):
    """
    財務データの値をパースする関数（改善版）
    """
    if not value_text or value_text.strip() == '-':
        return None
        
    value_text = value_text.strip()
    
    # 赤字の場合は-1を返す
    if '赤字' in value_text:
        return -1
        
    try:
        # カンマと単位記号を除去
        value_text = value_text.replace(',', '')
        
        # 小数点を含む数値の処理
        if '.' in value_text:
            # 億単位の処理
            if '京' in value_text:
                base_value = float(value_text.replace('京', ''))
                return base_value * 10000000000
            if '兆' in value_text:
                base_value = float(value_text.replace('兆', ''))
                return base_value * 1000000
            elif '億' in value_text:
                base_value = float(value_text.replace('億', ''))
                return base_value * 100  # 億を百万単位に変換
            # 百万単位の処理
            elif '百万' in value_text:
                return float(value_text.replace('百万', ''))
            else:
                return float(value_text)
        
        # 整数の処理
        else:
            # 億単位の処理
            if '京' in value_text:
                base_value = float(value_text.replace('京', ''))
                return base_value * 1000000000
            elif '兆' in value_text:
                base_value = float(value_text.replace('兆', ''))
                return base_value * 100000
            elif '億' in value_text:
                base_value = float(value_text.replace('億', ''))
                return base_value * 100  # 億を百万単位に変換
            # 百万単位の処理
            elif '百万' in value_text:
                return float(value_text.replace('百万', ''))
            else:
                return float(value_text)
            
    except (ValueError, TypeError) as e:
        # エラーメッセージをより詳細に
        print(f"Failed to parse financial value: '{value_text}' - Type: {type(value_text)} - Error: {e}")
        return None

def parse_date(date_str, date_type='daily'):
    """
    日付文字列をパースする統合関数
    
    Parameters:
    date_str (str): パースする日付文字列
    date_type (str): 'daily', 'annual', 'fiscal' のいずれか
    
    Returns:
    str: パースした日付文字列（YYYY/MM/DD or YYYY/MM）
    """
    try:
        # 予測値の "予" を除去
        date_str = date_str.replace('予', '').strip()
        
        if date_type == 'fiscal':
            # 財務データの年月（YYYY/MM）
            if '/' in date_str:
                year, month = date_str.split('/')[:2]
                return f"{year}/{int(month):02d}"
            return None
            
        elif date_type == 'annual':
            # 年間データの日付（YYYY年MM月DD日 or YYYY/MM/DD）
            if '年' in date_str:
                # 日本語形式の日付
                date_str = date_str.replace('年', '/').replace('月', '/').replace('日', '')
            parts = date_str.split('/')
            if len(parts) >= 3:
                year = parts[0]
                month = int(parts[1])
                day = int(parts[2])
                return f"{year}/{month:02d}/{day:02d}"
            return None
            
        else:  # daily
            # 日次データの日付（YYYY/MM/DD or MM/DD）
            parts = date_str.split('/')
            if len(parts) == 2:
                # MM/DD形式の場合
                month, day = map(int, parts)
                year = datetime.now().year
                return f"{year}/{month:02d}/{day:02d}"
            elif len(parts) == 3:
                # YYYY/MM/DD形式の場合
                year = parts[0]
                month = int(parts[1])
                day = int(parts[2])
                return f"{year}/{month:02d}/{day:02d}"
            return None
            
    except Exception as e:
        print(f"{date_type.capitalize()} date parsing error: {date_str} - {e}")
        return None

def parse_fiscal_date(date_str):
    """
    財務データの年月文字列をパースする関数
    例：'2023/12'、'2024/03予' などに対応
    """
    try:
        # '予' が付いているケースを処理
        date_str = date_str.replace('予', '').strip()
        # YYYY/MM 形式として処理
        year, month = map(int, date_str.split('/'))
        return f"{year}/{month:02d}"
    except Exception as e:
        print(f"Fiscal date parsing error: {date_str} - {e}")
        return None

def parse_annual_date(date_str):
    """
    年間データの日付文字列をパースする関数（例：2023年3月31日）
    """
    try:
        # "年" "月" "日" を "/"に置換
        date_str = date_str.replace('年', '/').replace('月', '/').replace('日', '')
        parts = date_str.split('/')
        if len(parts) == 3:
            year, month, day = parts
            return f"{year}/{month:02d}/{day:02d}"
    except Exception as e:
        print(f"Annual date parsing error: {date_str} - {e}")
        return None

def parse_fiscal_year(date_str):
    """
    年度文字列をパースする関数（例：2023/05）
    """
    try:
        return date_str.strip()
    except Exception as e:
        print(f"Fiscal year parsing error: {date_str} - {e}")
        return None

def parse_daily_date(date_str):
    """
    日次データの日付文字列をパースする関数
    年が省略されている場合は現在の年を使用
    """
    try:
        if '/' not in date_str:
            return None
            
        parts = date_str.split('/')
        if len(parts) == 2:
            # MM/DD形式の場合、現在の年を追加
            current_year = datetime.now().year
            month, day = parts
            return f"{current_year}/{month:02d}/{day:02d}"
        elif len(parts) == 3:
            # YYYY/MM/DD形式の場合
            year, month, day = parts
            return f"{year}/{month:02d}/{day:02d}"
    except Exception as e:
        print(f"Daily date parsing error: {date_str} - {e}")
        return None

def scrape_stock_data(csv_file):
    df = pd.read_csv(csv_file)
    all_data = []
    
    for code in df['コード']:
        try:
            company_data = {
                'code': code,
                'name': df[df['コード'] == code]['銘柄名'].iloc[0],
                'annual_data': [],
                'daily_data': [],
                'financial_data': []
            }

            # PER、PBR、業績データの取得
            for data_type, url in [
                ('per', f'https://irbank.net/{code}/per'),
                ('pbr', f'https://irbank.net/{code}/pbr'),
                ('results', f'https://irbank.net/{code}/results')
            ]:
                response = requests.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                if data_type == 'results':
                    # 業績データの処理
                    table = soup.find('table', class_='bar')
                    if table and table.find('tbody'):
                        for row in table.find('tbody').find_all('tr'):
                            cells = row.find_all('td')
                            if len(cells) >= 11:
                                try:
                                    fiscal_year = parse_date(cells[0].text, 'fiscal')
                                    if fiscal_year:
                                        financial_entry = {
                                            'fiscal_year': fiscal_year,
                                            'sales': parse_financial_value(cells[1].text),
                                            'operating_profit': parse_financial_value(cells[2].text),
                                            'ordinary_profit': parse_financial_value(cells[3].text),
                                            'net_profit': parse_financial_value(cells[4].text),
                                            'eps': parse_financial_value(cells[5].text),
                                            'roe': parse_financial_value(cells[6].text),
                                            'roa': parse_financial_value(cells[7].text),
                                            'operating_margin': parse_financial_value(cells[8].text),
                                            'cost_ratio': parse_financial_value(cells[9].text),
                                            'sga_ratio': parse_financial_value(cells[10].text)
                                        }
                                        # None値のフィルタリング
                                        financial_entry = {k: v for k, v in financial_entry.items() if v is not None}
                                        company_data['financial_data'].append(financial_entry)
                                except Exception as e:
                                    print(f"Error processing financial data for company {code}: {e}")
                                    continue
                
                else:  # PERとPBRの処理
                    dl = soup.find('dl', class_='gdl inline mgr')
                    if dl:
                        try:
                            if data_type == 'per':
                                per_annual_data = {}
                                for dt, dd in zip(dl.find_all('dt'), dl.find_all('dd')):
                                    date = parse_date(dt.text.strip(), 'annual')
                                    if date:
                                        per_text = dd.find('span', class_='text').text.strip()
                                        per_value = parse_value(per_text)  # PERはparse_valueを使用
                                        per_annual_data[date] = {
                                            'per': per_value,
                                            'is_per_red': per_text == '赤字'
                                        }
                            else:  # pbr
                                pbr_annual_data = {}
                                for dt, dd in zip(dl.find_all('dt'), dl.find_all('dd')):
                                    date = parse_date(dt.text.strip(), 'annual')
                                    if date:
                                        pbr_text = dd.find('span', class_='text').text.strip()
                                        pbr_value = parse_value(pbr_text)  # PBRはparse_valueを使用
                                        pbr_annual_data[date] = {
                                            'pbr': pbr_value,
                                            'is_pbr_red': pbr_text == '赤字'
                                        }
                        except Exception as e:
                            print(f"Error processing {data_type} data for company {code}: {e}")
                            continue
            
            # 年間データの結合
            if 'per_annual_data' in locals() and 'pbr_annual_data' in locals():
                all_dates = sorted(set(per_annual_data.keys()) | set(pbr_annual_data.keys()))
                for date in all_dates:
                    try:
                        annual_entry = {
                            'date': date,
                            'per': per_annual_data.get(date, {}).get('per'),
                            'pbr': pbr_annual_data.get(date, {}).get('pbr'),
                            'is_per_red': per_annual_data.get(date, {}).get('is_per_red', False),
                            'is_pbr_red': pbr_annual_data.get(date, {}).get('is_pbr_red', False)
                        }
                        # None値のフィルタリング
                        annual_entry = {k: v for k, v in annual_entry.items() if v is not None or k.startswith('is_')}
                        company_data['annual_data'].append(annual_entry)
                    except Exception as e:
                        print(f"Error processing annual data for date {date}, company {code}: {e}")
                        continue
            
            # 日次データの処理
            table = soup.find('table')
            if table and table.find('tbody'):
                for row in table.find('tbody').find_all('tr'):
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        try:
                            date_str = cells[0].text.strip()
                            per_str = cells[1].text.strip()
                            price_str = cells[2].text.strip()
                            
                            parsed_date = parse_date(date_str, 'daily')
                            if parsed_date:
                                per_value = parse_financial_value(per_str)  # parse_financial_valueを使用
                                price_value = parse_financial_value(price_str)  # 価格の処理
                                
                                daily_entry = {
                                    'date': parsed_date,
                                    'per': per_value,
                                    'price': price_value,
                                    'is_per_red': per_str == '赤字'
                                }
                                # None値以外とis_で始まるキーのみを残す
                                daily_entry = {k: v for k, v in daily_entry.items() if v is not None or k.startswith('is_')}
                                company_data['daily_data'].append(daily_entry)
                        except Exception as e:
                            print(f"Error processing daily data for company {code}:")
                            print(f"Date: {date_str}")
                            print(f"PER: {per_str}")
                            print(f"Price: {price_str}")
                            print(f"Error: {str(e)}")
                            continue
            
            # 空でないデータのみを追加
            if (company_data['annual_data'] or 
                company_data['daily_data'] or 
                company_data['financial_data']):
                all_data.append(company_data)
                print(f"Scraped data for company {code}")
            
            time.sleep(4)
            
        except Exception as e:
            print(f"Error scraping company {code}: {e}")
            continue
    
    # JSONとして保存
    with open('stock_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n処理が完了しました。")
    print(f"スクレイピングした企業数: {len(all_data)}")
    if all_data:
        print(f"最初の企業のデータ例:")
        print(f"- 企業コード: {all_data[0]['code']}")
        print(f"- 企業名: {all_data[0]['name']}")
        print(f"- 年間データ数: {len(all_data[0]['annual_data'])}")
        print(f"- 日次データ数: {len(all_data[0]['daily_data'])}")
        print(f"- 財務データ数: {len(all_data[0]['financial_data'])}")
    
    return all_data

# 実行例
scrape_stock_data('industry_categories/パルプ_紙.csv')
# scrape_stock_data('mof_sheets/Sheet1.csv')
