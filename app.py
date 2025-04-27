
from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

def load_products():
    if os.path.exists('products.csv'):
        return pd.read_csv('products.csv', dtype=str).to_dict('records')
    else:
        return []

def load_linked_products():
    if os.path.exists('linked_products.csv'):
        df = pd.read_csv('linked_products.csv', dtype=str)
        return df.to_dict('records')
    else:
        return []

products = load_products()
linked_products = load_linked_products()
summary = {}

@app.route('/')
def index():
    return render_template('index.html', products=products)

@app.route('/search', methods=['POST'])
def search():
    keyword = request.json['keyword'].lower()
    matched = []
    matched_codes = set()
    for p in products:
        if keyword in p['品號'].lower() or keyword in p['品名'].lower():
            matched.append(p)
            matched_codes.add(p['品號'])
    extra_codes = set()
    for link in linked_products:
        main_code = link['主品號']
        related_code = link['關聯品號']
        if related_code in matched_codes:
            extra_codes.add(main_code)
        elif main_code in matched_codes:
            extra_codes.add(related_code)
    for p in products:
        if p['品號'] in extra_codes and p['品號'] not in matched_codes:
            matched.append(p)
    return jsonify(matched)

@app.route('/record', methods=['POST'])
def record():
    data = request.json
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for item in data:
        code = item['品號']
        name = item['品名']
        qty = int(item['數量'])
        if code in summary:
            summary[code]['數量'] += qty
            summary[code]['記錄時間'] = now
        else:
            summary[code] = {'品名': name, '數量': qty, '記錄時間': now}
    return jsonify({"status": "ok"})

@app.route('/summary')
def get_summary():
    result = [{'品號': code, '品名': data['品名'], '數量': data['數量'], '記錄時間': data['記錄時間']} for code, data in summary.items()]
    return jsonify(result)

@app.route('/clear', methods=['POST'])
def clear():
    summary.clear()
    return jsonify({"status": "cleared"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
