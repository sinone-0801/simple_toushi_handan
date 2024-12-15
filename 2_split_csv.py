import pandas as pd
import os

def process_stock_data(input_file, interim_file='domestic_stocks.csv', output_dir='industry_categories'):
    """
    1. 内国株式のデータを抽出
    2. 33業種区分ごとにファイルを分割
    
    Parameters:
    input_file (str): 入力CSVファイルのパス
    interim_file (str): 中間ファイル（内国株式のみ）のパス
    output_dir (str): 業種別ファイルの出力ディレクトリ
    """
    try:
        # CSVファイルを読み込む
        df = pd.read_csv(input_file)
        
        # 内国株式のデータのみを抽出
        domestic_stocks = df[df['市場・商品区分'].str.contains('内国株式', na=False)]
        
        # 中間ファイルとして保存
        domestic_stocks.to_csv(interim_file, index=False, encoding='utf-8-sig')
        print(f'内国株式のデータを抽出しました: {len(domestic_stocks)}件')
        
        # 出力ディレクトリを作成
        os.makedirs(output_dir, exist_ok=True)
        
        # 33業種区分の一覧を取得（'-'を除外）
        industries = domestic_stocks['33業種区分'].unique()
        industries = [ind for ind in industries if ind != '-']
        
        # 各業種ごとにファイルを作成
        for industry in industries:
            # 業種でフィルタリング
            industry_df = domestic_stocks[domestic_stocks['33業種区分'] == industry]
            
            # ファイル名から不正な文字を除去
            safe_industry_name = "".join([c if c.isalnum() or c in ['-', '_'] else '_' for c in industry])
            
            # 出力ファイル名を設定
            output_file = os.path.join(output_dir, f'{safe_industry_name}.csv')
            
            # CSVとして保存
            industry_df.to_csv(output_file, index=False, encoding='utf-8-sig')
            
            print(f'業種「{industry}」のファイルを作成しました: {output_file}')
            print(f'件数: {len(industry_df)}件')
        
        print('\n処理が完了しました。')
        return True
        
    except Exception as e:
        print(f'エラーが発生しました: {e}')
        return False

# 使用例
input_file = 'mof_sheets/Sheet1.csv'
process_stock_data(input_file)