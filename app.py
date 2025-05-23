# 標準ライブラリを最初にインポート
import os
import sys
import logging
import http.client as http_client

# サードパーティライブラリをインポート
from dotenv import load_dotenv
import langchain
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from langchain.callbacks import get_openai_callback

# ログ設定
http_client.HTTPConnection.debuglevel = 1
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

# 環境変数の読み込み
load_dotenv()

# APIキー確認
if "OPENAI_API_KEY" not in os.environ:
    st.error("APIキーが設定されていません。.envファイルを確認してください。")
    print("エラー: OPENAI_API_KEYが設定されていません。.envファイルを確認してください。")
    st.stop()

# LangChainの詳細ログを有効化
langchain.verbose = True

# UI部分
st.title("LLM機能を搭載したWebアプリ")

st.write("##### WEB開発の専門家")
st.write("WEB開発について質問したい内容を入力してから「質問する」ボタンを押してください。")
st.write("##### 人事・採用の専門家")
st.write("人事・採用について質問したい内容を入力してから「質問する」ボタンを押してください。")

selected_item = st.radio(
    "聞きたい分野を選択してください。",
    ["WEB開発の専門家", "人事・採用の専門家"]
)

st.divider()

input_message = st.text_input(label="入力してください。")

if st.button("質問する"):
    if not input_message:
        # 入力がない場合のエラーメッセージ
        if selected_item == "WEB開発の専門家":
            st.error("WEB開発について質問したい内容を入力してから「質問する」ボタンを押してください。")
        else:
            st.error("人事・採用について質問したい内容を入力してから「質問する」ボタンを押してください。")
    else:
        st.divider()
        
        try:
            # LangChainのChatOpenAIクライアントの初期化
            llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5)
            
            # メッセージの準備
            if selected_item == "WEB開発の専門家":
                system_content = "あなたはWEB開発の専門家です。WEB開発に関する質問に詳細かつ正確に回答してください。HTML、CSS、JavaScript、バックエンド技術など幅広い知識を持っています。"
            else:  # 人事・採用の専門家
                system_content = "あなたは人事・採用の専門家です。採用プロセス、人材評価、組織開発、労務管理などについて詳しく、実務的なアドバイスを提供します。"
                
            messages = [
                SystemMessage(content=system_content),
                HumanMessage(content=input_message),
            ]
            
            # API接続とレスポンス取得
            with st.spinner("OpenAI APIに接続中..."):
                with get_openai_callback() as cb:
                    # LLMにメッセージを送信し、結果を取得
                    result = llm(messages)
                    
                    # レスポンスの表示
                    st.subheader("回答:")
                    st.write(result.content)
                    
                    # リクエスト情報の表示
                    st.subheader("リクエスト情報")
                    st.text(f"モデル: {llm.model_name}")
                    st.text(f"トークン使用量: {cb.total_tokens}")
                    st.text(f"プロンプトトークン: {cb.prompt_tokens}")
                    st.text(f"完了トークン: {cb.completion_tokens}")
                    st.text(f"コスト (USD): ${cb.total_cost:.6f}")
            
            # デバッグ用のログ
            print("\n--- 生のレスポンスオブジェクト ---")
            print(result)
            print(type(result))
            print(dir(result))
            
        except Exception as e:
            error_msg = f"APIへの接続中に問題が発生しました: {e}"
            st.error(error_msg)
            print(f"エラー: {error_msg}")