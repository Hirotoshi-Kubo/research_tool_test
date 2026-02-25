import os
import csv

def setup_environment():
    # 1. inputフォルダの作成
    input_dir = "input"
    os.makedirs(input_dir, exist_ok=True)
    
    # 2. 正常なデータファイルの作成
    with open(os.path.join(input_dir, "data_normal.csv"), "w", encoding="utf-8") as f:
        f.write("timestamp,sensor_id,value,status\n")
        f.write("2026-02-23 10:00,S01,10.5kg,OK\n")
        f.write("2026-02-23 10:05,S02,2.3kg,OK\n")

    # 3. 異常を含むデータファイルの作成（エラー処理の確認用）
    with open(os.path.join(input_dir, "data_dirty.csv"), "w", encoding="utf-8") as f:
        f.write("timestamp,sensor_id,value,status\n")
        f.write("2026-02-23 11:00,S01,50.0kg,Error\n") # status='Error'なのでスキップされるはず
        f.write("2026-02-23 11:05,S03,invalid_val,OK\n") # 数値変換エラーになるはず
        f.write("2026-02-23 11:10,S01,5.0kg,OK\n")     # 正常に処理されるはず

    print(f"テスト環境を構築しました: {input_dir}/ にCSVを2つ作成しました。")

if __name__ == "__main__":
    setup_environment()