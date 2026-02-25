import os
import glob
import data_processor
import db_handler
import reporter

def main():
    print("=== 研究支援自動化ツール 起動 ===")

    # 1. データベースの初期化（システムの保守・運用）
    db_handler.init_db()

    #1 仕様の把握：入力データ確認
    input_dir = "input"
    files = glob.glob(os.path.join(input_dir, "*.csv"))

    if not files:
        print("エラー: 入力データが見つかりませんでした。")
        return

    for file in files:
        print(f"処理中: {os.path.basename(file)}")

        #2 データ加工
        data, errors = data_processor.process_file(file)
        
        # DB保存
        if data:
            db_handler.save_data(data)
            print(f"  {os.path.basename(file)}: {len(data)}件 保存完了")
        
        # エラー表示
        if errors:
            print(f"  [!] {os.path.basename(file)} で {len(errors)} 件のスキップが発生")

 # 4. 統計レポートの作成（ここが最後の一押し！）
    print("\n--- レポート生成 ---")
    reporter.generate_report()

    print("\n=== 全工程完了 ===")
        

if __name__ == "__main__":
    main()
