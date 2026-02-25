import pandas as pd
import os

def process_file(file_path):
    """
    指定されたCSVファイルを読み込み、研究用ツール向けにデータを整形して返します。
    
    Args:
        file_path (str): 処理対象のCSVファイルパス
        
    Returns:
        tuple: (processed_data_list, error_log_list)
        - processed_data_list: 加工済みの辞書リスト
        - error_log_list: エラーが発生した行のログリスト
    """
    processed_data = []
    error_log = []
    
    # 係数定義（仕様変更に対応しやすいよう、定数は先頭に置く）
    KG_TO_LB = 2.20462

    try:
        # 1. データの読み込み (現行データの把握)
        # 実務ではヘッダーの有無やエンコーディング(utf-8/shift-jis)に注意が必要です
        df = pd.read_csv(file_path, encoding='utf-8')
        
        # データフレームを行ごとに処理
        for index, row in df.iterrows():
            try:
                # --- ここからデータ選定・加工ロジック ---
                
                # A. フィルタリング (必要な出力結果の選定)
                # 例: 'status'列が 'Error' の行は除外する
                if 'status' in df.columns and row['status'] == 'Error':
                    continue

                # B. データ加工 (自動化ツール作成)
                # 'value'列の "10.5kg" のような文字列を数値に変換
                raw_val = str(row['value'])
                val_lb = 0.0
                
                if 'kg' in raw_val:
                    # "kg" を削除して数値化し、ポンドに変換
                    clean_val = raw_val.replace('kg', '').strip()
                    val_lb = round(float(clean_val) * KG_TO_LB, 2)
                else:
                    # 単位がない、または別の単位の場合はエラーとして扱うか、仕様に従う
                    # ここでは数値変換できるかトライする
                    val_lb = float(raw_val)

                # C. 出力データの構築
                # データベースやレポートに使いやすい辞書形式にする
                record = {
                    'source_file': os.path.basename(file_path),
                    'timestamp': row.get('timestamp', 'N/A'), # 列がない場合の対策
                    'sensor_id': row.get('sensor_id', 'Unknown'),
                    'value_lb': val_lb,
                    'original_value': raw_val
                }
                processed_data.append(record)
                
            except Exception as row_err:
                # 行単位のエラー (システムの保守、運用)
                # どのファイルの何行目でエラーが出たか記録する
                error_msg = f"Skipped Row {index + 2}: {row_err} (Data: {raw_val})"
                error_log.append(error_msg)

    except Exception as file_err:
        # ファイル自体の読み込みエラー
        error_log.append(f"File Read Error: {os.path.basename(file_path)} - {file_err}")

    return processed_data, error_log

# テスト用コード（このファイル単体で動作確認するため）
if __name__ == "__main__":
    # ダミーのCSVを作ってテストする
    with open("test_dummy.csv", "w", encoding="utf-8") as f:
        f.write("timestamp,sensor_id,value,status\n")
        f.write("2026-02-23 10:00,S01,10.5kg,OK\n")
        f.write("2026-02-23 10:01,S02,invalid,OK\n") # エラーになる行
        f.write("2026-02-23 10:02,S01,5.0kg,Error\n") # フィルタされる行
    
    data, errors = process_file("test_dummy.csv")
    
    print("--- 加工データ ---")
    for d in data: print(d)
    
    print("\n--- エラーログ ---")
    for e in errors: print(e)
    
    # テストファイルを掃除
    os.remove("test_dummy.csv")