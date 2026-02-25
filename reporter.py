import sqlite3
import pandas as pd
from datetime import datetime
import db_handler  # DB接続設定を共有

REPORT_FILE = f"report{datetime.now().strftime('%Y%m%d')}.txt"

def generate_report():
    """
    データベースの全データを読み込み、統計レポートを作成する。
    """
    conn = db_handler.get_connection()
    
    try:
        # SQLでデータを一括取得（CSVを1つずつ開くより圧倒的に高速）
        df = pd.read_sql("SELECT * FROM sensor_logs", conn)
        
        if df.empty:
            print("  [!] データがないためレポート作成をスキップします。")
            return

        # --- 統計計算 (Pandasの力) ---
        total_count = len(df)
        avg_val = df['value_lb'].mean()
        max_val = df['value_lb'].max()
        min_val = df['value_lb'].min()
        
        # センサーごとの平均値も算出（実務でよくある要望）
        sensor_summary = df.groupby('sensor_id')['value_lb'].mean().to_string()

        # --- レポート本文の作成 ---
        report_content = f"""
========================================
  研究支援自動化ツール 実行レポート
  作成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
========================================

【全体統計】
  - 総データ数 : {total_count} 件
  - 平均値     : {avg_val:.2f} lb
  - 最大値     : {max_val:.2f} lb
  - 最小値     : {min_val:.2f} lb

【センサー別平均値】
{sensor_summary}

【判定】
  ステータス: {'正常 (PASS)' if avg_val >= 50 and avg_val <= 80 else '要確認 (WARN)'}

========================================
※このレポートはシステムにより自動生成されました。
"""

        # ファイルに出力
        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            f.write(report_content)
            
        print(f"  -> レポート生成完了: {REPORT_FILE}")
        print(f"     (全体平均: {avg_val:.2f} lb)")

    except Exception as e:
        print(f"  [!] レポート作成エラー: {e}")
        
    finally:
        conn.close()

if __name__ == "__main__":
    # 単体テスト用
    generate_report()