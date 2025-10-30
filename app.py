from flask import Flask, request, render_template, redirect, url_for, session  
import json
import time
import matplotlib
import matplotlib.pyplot 
matplotlib.use('Agg')  # 使用不需要 GUI 的後端

# 匯入LLM模組及sentment analiysis模組
from rag_breeze import del_num,text_Loader,splitting,embedding,db
from rag_breeze import LAM_RAG,RAG_LLM
from pn_pie_chart import sentent_np


# 初始化 Flask 應用
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 設定密鑰來保護session資料

# 讀取 JSON 檔案
file_path = 'all_dc_data_test_0.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 頁面導向到首頁
@app.route('/') 
def first():
    return redirect(url_for('home'))

# 顯示首頁
@app.route('/home')
def home():
    return render_template('home.html')

# 處理查詢關鍵字提交
@app.route('/search', methods=['GET','POST'])
def search():
    
    # 獲取用戶輸入的三個查詢關鍵字
    query1 = request.form['query1']
    query2 = request.form.get('query2', '').strip()
    query3 = request.form.get('query3', '').strip()
    
    # 將查詢關鍵字分別存入session，只有在不為空時才存取 query2 和 query3
    session['query1'] = query1
    if query2:
        session['query2'] = query2
    else:
        session.pop('query2', None)
    if query3:
        session['query3'] = query3
    else:
        session.pop('query3', None)

    # 重定向到result頁面
    return redirect(url_for('result'))

# 查詢結果處理（query1 對應的結果）
@app.route('/result', methods=['GET', 'POST'])
def result():
    
    question = request.form.get('question', '').strip()
    
    # 從 session 取得使用者的查詢關鍵字
    query1 = session.get('query1', '')  # 從session中取得query1資料
    query2 = session.get('query2', None)  # 從session中取得query2資料
    query3 = session.get('query3', None)  # 從session中取得query3資料
    
    results = []

    # 根據 query1 關鍵字篩選資料   
    keywords = [k.strip() for k in query1.split()]
    results = [
            record for record in data
            if any(keyword.lower() in record['標題'][0].lower() for keyword in keywords)
        ]
    # 依據「心情」欄位排序資料（由大到小）
    results = sorted(results, key=lambda x: int(x['心情']), reverse=True)

    # 產生情感圓餅圖
    plot_url = sentent_np(results)

    # 若沒有輸入問題，只儲存結果 JSON，不進行問答
    if not question:  
        with open('path_to_directory/queries_0_content.json', 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=4, sort_keys=False)      
        answer =''
        result_context = ''
    
    elif question:
        del_num('path_to_directory/queries_0_content.json')
        time.sleep(1)
        docs = text_Loader('queries_0_content_llm_ver.json')
        all_splits = splitting(docs)
        embeddings = embedding()
        retriever,vectorstore = db(embeddings, all_splits)
        time.sleep(3)
        chain_v2,format_docs = LAM_RAG(retriever)
        time.sleep(3)
        result_context ,answer = RAG_LLM(chain_v2, question,retriever,format_docs)
        
        vectorstore.delete_collection()
        
    # 將結果傳遞回模板
    return render_template('index.html', active_page='result', results=results, query1=query1, query2=query2, query3=query3, question=question,result_context =result_context, answer=answer,plot_url=plot_url)

# 第二層查詢結果處理（query2 對應）
@app.route('/result_1', methods=['GET', 'POST'])
def result_1():

    question = request.form.get('question', '').strip()
    query1 = session.get('query1', '')  
    query2 = session.get('query2', None)  
    query3 = session.get('query3', None)  
    
    results = []
    if query2:
        keywords = [k.strip() for k in query2.split()]
        results = [
                record for record in data
                if any(keyword.lower() in record['標題'][0].lower() for keyword in keywords)
            ]
        
        results = sorted(results, key=lambda x: int(x['心情']), reverse=True)

       
        plot_url = sentent_np(results)


        if not question:  
            with open('path_to_directory/queries_0_content.json', 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=4, sort_keys=False)      
            answer =''
            result_context = ''
        
        elif question:
            del_num('path_to_directory/queries_0_content.json')
            time.sleep(1)
            docs = text_Loader('queries_0_content_llm_ver.json')
            all_splits = splitting(docs)
            embeddings = embedding()
            retriever,vectorstore = db(embeddings, all_splits)
            time.sleep(3)
            chain_v2,format_docs = LAM_RAG(retriever)
            time.sleep(3)
            result_context ,answer = RAG_LLM(chain_v2, question,retriever,format_docs)
            
            vectorstore.delete_collection()
        
   
    return render_template('index_1.html', active_page='result_1', results=results, query1=query1, query2=query2, query3=query3, question=question,result_context =result_context, answer=answer,plot_url=plot_url)

# 第三層查詢結果處理（query3 對應）
@app.route('/result_2', methods=['GET', 'POST'])
def result_2():

    question = request.form.get('question', '').strip()
    query1 = session.get('query1', '')  
    query2 = session.get('query2', None)  
    query3 = session.get('query3', None)  
    
    results = []
    
    if query3:
        keywords = [k.strip() for k in query3.split()]
        results = [
                record for record in data
                if any(keyword.lower() in record['標題'][0].lower() for keyword in keywords)
            ]
        
        results = sorted(results, key=lambda x: int(x['心情']), reverse=True)

       
        plot_url = sentent_np(results)


        if not question:  
            with open('path_to_directory/queries_0_content.json', 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=4, sort_keys=False)      
            answer =''
            result_context = ''
        
        elif question:
            del_num('path_to_directory/queries_0_content.json')
            time.sleep(1)
            docs = text_Loader('queries_0_content_llm_ver.json')
            all_splits = splitting(docs)
            embeddings = embedding()
            retriever,vectorstore = db(embeddings, all_splits)
            time.sleep(3)
            chain_v2,format_docs = LAM_RAG(retriever)
            time.sleep(3)
            result_context ,answer = RAG_LLM(chain_v2, question,retriever,format_docs)
            
            vectorstore.delete_collection()
        
   
    return render_template('index_2.html', active_page='result_2', results=results, query1=query1, query2=query2, query3=query3, question=question,result_context =result_context, answer=answer,plot_url=plot_url)

# 啟動 Flask 應用（開發模式）
if __name__ == '__main__':
    app.run()

