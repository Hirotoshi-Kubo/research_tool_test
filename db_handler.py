import sqlite3
import os
from datetime import datetime

# データベースファイル名
DB_NAME = "research_data.db"

def get_connection():
    """データベースへの接続を確立するヘルパー関数"""
    return sqlite3.connect(DB_NAME)

def init_db():
    """
    データベースとテーブルの初期化を行う。
    システム起動時に必ず1回実行する。
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # テーブル作成（存在しない場合のみ）
    # 研究データに必要なカラムを定義
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sensor_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        sensor_id TEXT,
        value_lb REAL,
        original_value TEXT,
        source_file TEXT,
        processed_at TEXT
    )
    ''')
    
    conn.commit()
    conn.close()

def save_data(data_list):
    """
    加工済みの辞書リストをまとめてデータベースに保存する。
    
    Args:
        data_list (list): data_processorで作成された辞書のリスト
    """
    if not data_list:
        return

    conn = get_connection()
    cursor = conn.cursor()
    
    # 現在時刻（処理実行時刻）を取得
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 一括挿入用データの準備
    insert_data = []
    for item in data_list:
        insert_data.append((
            item.get('timestamp'),
            item.get('sensor_id'),
            item.get('value_lb'),
            item.get('original_value'),
            item.get('source_file'),
            current_time
        ))

    try:
        # プレースホルダー(?)を使ってSQLインジェクション対策
        cursor.executemany('''
        INSERT INTO sensor_logs (timestamp, sensor_id, value_lb, original_value, source_file, processed_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', insert_data)
        
        conn.commit()
        print(f"  -> DB保存完了: {len(insert_data)}件")
        
    except sqlite3.Error as e:
        print(f"  [!] DB保存エラー: {e}")
        
    finally:
        conn.close()