import pandas as pd
import requests
from pathlib import Path

def download_and_convert_all_sheets_to_csv(url, output_dir="excel_sheets"):
    """
    指定されたURLからExcelファイルをダウンロードし、全シートを個別のCSVファイルに変換する関数
    
    Parameters:
    url (str): ダウンロードするExcelファイルのURL
    output_dir (str): CSVファイルを保存するディレクトリ
    """
    try:
        # 出力ディレクトリの作成
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # URLからファイルをダウンロード
        print("ファイルをダウンロード中...")
        response = requests.get(url)
        response.raise_for_status()
        
        # 一時的なExcelファイルを保存
        temp_excel = "temp.xlsx"
        with open(temp_excel, "wb") as f:
            f.write(response.content)
        
        # Excelファイルの全シートを読み込み
        print("Excelファイルの全シートを処理中...")
        excel_file = pd.ExcelFile(temp_excel)
        sheet_names = excel_file.sheet_names
        
        # 各シートを処理
        for sheet_name in sheet_names:
            print(f"シート '{sheet_name}' を処理中...")
            # シートを読み込み
            df = pd.read_excel(temp_excel, sheet_name=sheet_name)
            
            # ファイル名に使用できない文字を置換
            safe_sheet_name = "".join([c if c not in r'<>:"/\|?*' else '_' for c in sheet_name])
            
            # CSVファイルとして保存
            output_path = Path(output_dir) / f"{safe_sheet_name}.csv"
            df.to_csv(output_path, index=False, encoding='utf-8-sig')  # BOM付きUTF-8で保存
            print(f"シート '{sheet_name}' を {output_path} として保存しました")
        
        # 一時ファイルを削除
        Path(temp_excel).unlink()
        
        print(f"\n変換が完了しました。出力ディレクトリ: {output_dir}")
        print(f"変換されたシート: {', '.join(sheet_names)}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"ダウンロードエラー: {e}")
        return False
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return False

# 使用例
url = "https://www.jpx.co.jp/markets/statistics-equities/misc/tvdivq0000001vg2-att/data_j.xls"
download_and_convert_all_sheets_to_csv(url, "mof_sheets")