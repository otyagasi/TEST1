import os
import sqlite3
import uuid
from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# --- 簡易デモ用データベース初期化 ----------------------------------------

def init_db():
    """SQLiteデータベースを初期化する関数"""
    conn = sqlite3.connect('demo.db')
    c = conn.cursor()

    # 食材の栄養情報テーブル
    c.execute('''
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            calories REAL,
            protein REAL,
            fat REAL,
            carb REAL
        )
    ''')

    # 食事履歴テーブル
    c.execute('''
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            calories REAL,
            protein REAL,
            fat REAL,
            carb REAL,
            date TEXT
        )
    ''')

    # 食材データがなければサンプルとして追加 (Apple, Banana, Orange のみ)
    sample_ingredients = [
        ("Apple",   52,  0.3,  0.2, 14),
        ("Banana",  89,  1.1,  0.3, 23),
        ("Orange",  47,  0.9,  0.1, 12)
    ]
    for ing in sample_ingredients:
        try:
            c.execute('INSERT INTO ingredients(name, calories, protein, fat, carb) VALUES (?,?,?,?,?)', ing)
        except sqlite3.IntegrityError:
            pass  # すでに存在する場合はスルー

    conn.commit()
    conn.close()


# --- 簡易分類ロジック（デモ用） ----------------------------------------
def mock_classify_image(image_path):
    """
    簡易的なデモ分類関数。
    本来は機械学習モデルを呼び出して推論する部分。
    ここではファイル名の中身(色や名前)に応じてダミーで返しているだけ。
    """
    # ファイル名に含まれる文字で判別するデモ
    # - "apple" があれば Apple
    # - "banana" があれば Banana
    # - "orange" があれば Orange
    # - それ以外は "Unknown"

    filename = os.path.basename(image_path).lower()
    if "apple" in filename:
        return "Apple"
    elif "banana" in filename:
        return "Banana"
    elif "orange" in filename:
        return "Orange"
    else:
        return "Unknown"


def allowed_file(filename):
    """アップロードされたファイルの拡張子チェック"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# --- ルーティング -----------------------------------------------------

@app.route('/')
def index():
    """トップページ: 画像アップロードフォーム"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_image():
    """画像をアップロードして分類結果を表示するルート"""
    if 'image' not in request.files:
        return "No file part", 400

    file = request.files['image']
    if file.filename == '':
        return "No selected file", 400

    if file and allowed_file(file.filename):
        # ファイルを保存
        unique_filename = str(uuid.uuid4()) + "_" + file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)

        # 簡易分類
        classified_name = mock_classify_image(filepath)

        # 栄養情報をDBから取得
        conn = sqlite3.connect('demo.db')
        c = conn.cursor()
        c.execute("SELECT calories, protein, fat, carb FROM ingredients WHERE name=?", (classified_name,))
        row = c.fetchone()
        conn.close()

        if row:
            calories, protein, fat, carb = row
        else:
            # DBに食材が無い場合、Unknown扱い
            classified_name = "Unknown"
            calories, protein, fat, carb = (0, 0, 0, 0)

        # 結果表示用HTMLへ
        return render_template('result.html',
                               filename=unique_filename,
                               food_name=classified_name,
                               calories=calories,
                               protein=protein,
                               fat=fat,
                               carb=carb)
    else:
        return "File not allowed", 400


@app.route('/save_meal', methods=['POST'])
def save_meal():
    """
    分類結果を実際の食事としてデータベースに登録する処理
    量や日付を入力させたりするとリアルなアプリに近づく
    """
    food_name = request.form.get('food_name')
    calories = request.form.get('calories')
    protein = request.form.get('protein')
    fat = request.form.get('fat')
    carb = request.form.get('carb')

    if not food_name:
        return "Invalid data", 400

    # デモ用: 日付は簡易的に文字列
    import datetime
    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect('demo.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO meals(name, calories, protein, fat, carb, date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (food_name, calories, protein, fat, carb, date_str))
    conn.commit()
    conn.close()

    return redirect(url_for('history'))


@app.route('/history')
def history():
    """
    登録した食事の一覧表示 + 簡易ランキング
    - 非常に単純な「栄養バランススコア」ロジックを例示
    """
    conn = sqlite3.connect('demo.db')
    c = conn.cursor()
    c.execute("SELECT name, calories, protein, fat, carb, date FROM meals")
    meals = c.fetchall()
    conn.close()

    # 簡易スコアリング例: 
    # ここでは (1) カロリーが400～600の範囲に近いほどスコアUP
    #           (2) P : F : C が 15% : 25% : 60% に近いほどスコアUP
    # といった超簡易例を計算
    meal_scores = []
    for m in meals:
        name, cal, prot, fat, carb, dt = m
        cal = float(cal)
        prot = float(prot)
        fat = float(fat)
        carb = float(carb)

        total = prot + fat + carb
        if total == 0:
            balance_score = 0
        else:
            p_ratio = prot / total
            f_ratio = fat / total
            c_ratio = carb / total
            # 目標比率との乖離を単純加算(絶対値)
            diff = abs(p_ratio - 0.15) + abs(f_ratio - 0.25) + abs(c_ratio - 0.60)
            balance_score = 1.0 - diff  # 差分が小さいほどスコア大

        # カロリー理想範囲中心(500)からの乖離
        cal_diff = abs(cal - 500) / 500.0
        cal_score = 1.0 - cal_diff  # 乖離が小さいほどスコア大

        # 総合スコア(超適当)
        total_score = (balance_score + cal_score) / 2
        meal_scores.append((name, cal, prot, fat, carb, dt, total_score))

    # スコアでソート(降順)
    meal_scores.sort(key=lambda x: x[-1], reverse=True)

    return render_template('history.html', meals=meal_scores)


# --- メインエントリーポイント -----------------------------------------
if __name__ == '__main__':
    # uploadsフォルダが無い場合は作成
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # DB初期化
    init_db()

    print("Starting Flask app...")
    app.run(debug=True)
