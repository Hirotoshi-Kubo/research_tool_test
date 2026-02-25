import streamlit as st
import pandas as pd
import os
import db_handler
import data_processor

# ページの基本設定
st.set_page_config(page_title="研究データ管理システム", layout="wide")

def main():
    st.title("📊 研究支援データ管理ツール")

    # サイドバー：データのアップロード
    st.sidebar.header("データのアップロード")
    uploaded_file = st.sidebar.file_uploader("CSVファイルを選択してください", type="csv")

    # DB初期化
    db_handler.init_db()

    # --- 1. ファイルアップロード処理 ---
    if uploaded_file is not None:
        # 一時保存用のディレクトリ
        os.makedirs("input", exist_ok=True)
        # ファイル名サニタイズ（パストラバーサル対策）
        safe_name = os.path.basename(uploaded_file.name)
        file_path = os.path.join("input", safe_name)
        
        # アップロードされたファイルを保存
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.sidebar.success(f"アップロード完了: {uploaded_file.name}")
        
        # ボタンが押されたら処理開始
        if st.sidebar.button("データを処理して保存"):
            try:
                with st.spinner('処理中...'):
                    data, errors = data_processor.process_file(file_path)
                    
                    if data:
                        db_handler.save_data(data)
                        st.success(f"{len(data)}件のデータをデータベースに保存しました！")
                    
                    if errors:
                        st.error(f"{len(errors)}件のエラーが発生しました。")
                        st.write(errors)
            except Exception as e:
                st.error(f"データ処理中に予期しないエラーが発生しました: {e}")

    # --- 2. データベースの中身を表示（ダッシュボード機能） ---
    st.markdown("---")
    st.subheader("📈 蓄積データ・ダッシュボード")

    # DBからデータを読み込む
    try:
        conn = db_handler.get_connection()
        # 改善案: ページネーションまたはLIMIT付きクエリ
        df = pd.read_sql("SELECT * FROM sensor_logs ORDER BY timestamp DESC LIMIT 1000", conn)
        conn.close()
    except Exception as e:
        st.error(f"データベースの読み込みに失敗しました: {e}")
        df = pd.DataFrame()

    if not df.empty:
        # タブで表示を切り替え
        tab1, tab2 = st.tabs(["データ一覧", "統計グラフ"])
        
        with tab1:
            st.dataframe(df) # Excelのようにデータを表示
            
        with tab2:
            # センサーごとの平均値をグラフ化
            st.bar_chart(df.groupby("sensor_id")["value_lb"].mean())
            
            # 生データの推移
            st.line_chart(df["value_lb"])
    else:
        st.info("データはまだありません。CSVをアップロードしてください。")

if __name__ == "__main__":
    main()