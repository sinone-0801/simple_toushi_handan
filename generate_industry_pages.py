import pandas as pd
import os
import json

def safe_number(value):
    """数値を安全に変換する関数"""
    try:
        return float(value) if value is not None else 0
    except (ValueError, TypeError):
        return 0

# HTMLテンプレートを追加
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
                        <div class="metric-label">ROE</div>
                        <div class="metric-value">${{formatRatio(company.roe)}}%</div>
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

def generate_industry_pages(json_path, csv_path):
    # JSONファイルを読み込む
    with open(json_path, 'r', encoding='utf-8') as f:
        stock_data = json.load(f)
    
    # 業種情報を追加
    stock_data = add_industry_info(stock_data, csv_path)
    
    # 業種ごとの企業データを整理
    industry_data = {}
    for company in stock_data:
        industry = company.get('industry', 'その他')
        if industry not in industry_data:
            industry_data[industry] = []
        
        # 最新の財務データを取得
        annual_data = company.get('annual_data', [])
        latest_annual = annual_data[-1] if annual_data else {}
        
        financial_data = company.get('financial_data', [])
        latest_financial = financial_data[-1] if financial_data else {}
        
        company_info = {
            'code': company['code'],
            'name': company['name'],
            'per': latest_annual.get('per', 0),
            'pbr': latest_annual.get('pbr', 0),
            'eps': latest_financial.get('eps', None),
            'roe': latest_financial.get('roe', None)
        }
        
        industry_data[industry].append(company_info)

    # 業種ごとにページを生成
    for industry, companies in industry_data.items():
        file_name = industry.replace('/', '_')
        html_content = html_template.format(
            industry,
            json.dumps(companies, ensure_ascii=False)
        )
        
        os.makedirs('industry', exist_ok=True)
        output_path = f"industry/{file_name}.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
    return {industry: len(companies) for industry, companies in industry_data.items()}

# メインの実行部分
if __name__ == "__main__":
    json_path = "stock_data.json"
    csv_path = "mof_sheets/Sheet1.csv"
    
    if os.path.exists(json_path) and os.path.exists(csv_path):
        industry_counts = generate_industry_pages(json_path, csv_path)
        print(f"\n生成された業種別ページ:")
        for industry, count in industry_counts.items():
            print(f"{industry}: {count}社")
    else:
        print(f"Error: Required files not found")