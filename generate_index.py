import pandas as pd
import os

def generate_industry_page(csv_path):
    # CSVファイルを読み込む
    df = pd.read_csv(csv_path)
    
    # 業種ごとの企業数をカウント
    industry_counts = df['33業種区分'].value_counts()
    
    # HTMLのヘッダー部分
    html_content = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>シンプル投資判断</title>
    <style>
        body {
            font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', Meiryo, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
            font-size: 24px;
        }
        .industry-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
            padding: 20px;
        }
        .industry-card {
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s ease-in-out;
        }
        .industry-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        a {
            color: #2c3e50;
            text-decoration: none;
            display: block;
            font-size: 16px;
        }
        a:hover {
            color: #3498db;
        }
        .stock-count {
            color: #666;
            font-size: 12px;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <h1>33業種区分別 株式投資判断</h1>
    <div class="industry-grid">
"""

    # 各業種のカードを生成
    for industry, count in industry_counts.items():
        # ファイル名用に業種名を処理（スラッシュをアンダースコアに変換）
        file_name = industry.replace('/', '_')
        card_html = f"""        <div class="industry-card">
            <a href="industry/{file_name}.html">{industry}</a>
            <div class="stock-count">銘柄数: {count}社</div>
        </div>
"""
        html_content += card_html

    # HTMLのフッター部分
    html_content += """    </div>
</body>
</html>
"""

    # HTMLファイルを保存
    output_path = "index.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Generated {output_path} with {len(industry_counts)} industries")
    return industry_counts

# スクリプトを実行
if __name__ == "__main__":
    csv_path = "mof_sheets/Sheet1.csv"
    if os.path.exists(csv_path):
        industry_counts = generate_industry_page(csv_path)
        print("\n業種別企業数:")
        for industry, count in industry_counts.items():
            print(f"{industry}: {count}社")
    else:
        print(f"Error: File {csv_path} not found")