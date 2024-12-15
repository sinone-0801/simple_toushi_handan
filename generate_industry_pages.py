import pandas as pd
import os
import json

def safe_number(value):
    """数値を安全に変換する関数"""
    try:
        return float(value) if value is not None else 0
    except (ValueError, TypeError):
        return 0

def generate_industry_pages(csv_path):
    # CSVファイルを読み込む
    df = pd.read_csv(csv_path)
    
    # HTMLテンプレートを文字列として定義
    html_template = '''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{0} - シンプル投資判断</title>
    <style>
        body {{
            font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', Meiryo, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .stock-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        h1 {{
            font-size: 24px;
            margin-bottom: 20px;
            color: #333;
        }}
        .companies-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .company-card {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .company-name {{
            font-size: 18px;
            margin-bottom: 10px;
            color: #333;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }}
        .metric {{
            background: #f8f9fa;
            padding: 8px;
            border-radius: 4px;
        }}
        .metric-label {{
            font-size: 12px;
            color: #666;
        }}
        .metric-value {{
            font-size: 14px;
            font-weight: bold;
            color: #333;
            margin-top: 2px;
        }}
        .back-link {{
            display: inline-block;
            margin-top: 20px;
            color: #3498db;
            text-decoration: none;
        }}
        .back-link:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="stock-card">
        <h1>{0}</h1>
        <div class="companies-grid" id="companiesGrid">
        </div>
    </div>
    <a href="../index.html" class="back-link">← 業種一覧に戻る</a>

    <script>
    const companiesData = {1};

    function formatNumber(value) {{
        if (value === null || value === undefined || isNaN(value)) {{
            return 'N/A';
        }}
        return Number(value).toLocaleString();
    }}

    function formatRatio(value) {{
        if (value === null || value === undefined || isNaN(value)) {{
            return 'N/A';
        }}
        return Number(value).toFixed(2);
    }}

    function calculateMixFactor(per, pbr) {{
        if (per === null || per === undefined || isNaN(per) || 
            pbr === null || pbr === undefined || isNaN(pbr)) {{
            return 'N/A';
        }}
        return (per * pbr).toFixed(2);
    }}

    function renderCompanies() {{
        const grid = document.getElementById('companiesGrid');
        companiesData.forEach(company => {{
            const card = document.createElement('div');
            card.className = 'company-card';
            
            const per = Number(company.per) || 0;
            const pbr = Number(company.pbr) || 0;
            
            card.innerHTML = `
                <div class="company-name">${{company.code}} - ${{company.name}}</div>
                <div class="metrics">
                    <div class="metric">
                        <div class="metric-label">PER</div>
                        <div class="metric-value">${{formatRatio(per)}}倍</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">PBR</div>
                        <div class="metric-value">${{formatRatio(pbr)}}倍</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">EPS</div>
                        <div class="metric-value">${{formatNumber(company.eps)}}円</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">ミックス係数</div>
                        <div class="metric-value">${{calculateMixFactor(per, pbr)}}</div>
                    </div>
                </div>
            `;
            grid.appendChild(card);
        }});
    }}

    renderCompanies();
    </script>
</body>
</html>
'''

    # 業種ごとにページを生成
    industry_counts = {}
    
    # industryディレクトリがなければ作成
    os.makedirs('industry', exist_ok=True)
    
    # 業種ごとにデータを処理
    for industry in df['33業種区分'].unique():
        # その業種の企業を抽出
        industry_df = df[df['33業種区分'] == industry]
        industry_counts[industry] = len(industry_df)
        
        # 企業データを準備
        companies = []
        for _, row in industry_df.iterrows():
            annual_data = row.get('annual_data', [])
            if annual_data and len(annual_data) > 0:
                latest = annual_data[-1]  # 最新のデータを使用
                companies.append({
                    'code': row['コード'],
                    'name': row['銘柄名'],
                    'per': safe_number(latest.get('per', 0)),
                    'pbr': safe_number(latest.get('pbr', 0)),
                    'eps': safe_number(latest.get('eps', None))
                })
            else:
                # データがない場合のフォールバック
                companies.append({
                    'code': row['コード'],
                    'name': row['銘柄名'],
                    'per': 0,
                    'pbr': 0,
                    'eps': None
                })
        
        # ファイル名用に業種名を処理
        file_name = industry.replace('/', '_')
        
        # HTMLを生成
        html_content = html_template.format(
            industry,
            json.dumps(companies, ensure_ascii=False)
        )
        
        # HTMLファイルを保存
        output_path = f"industry/{file_name}.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
    return industry_counts

# メインの実行部分
if __name__ == "__main__":
    csv_path = "mof_sheets/Sheet1.csv"
    if os.path.exists(csv_path):
        industry_counts = generate_industry_pages(csv_path)
        print(f"\n生成された業種別ページ:")
        for industry, count in industry_counts.items():
            print(f"{industry}: {count}社")
    else:
        print(f"Error: File {csv_path} not found")