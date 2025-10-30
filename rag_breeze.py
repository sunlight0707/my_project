# 移除所有情緒分析分數及情緒分析直方圖
def del_num(file_path):
    import json
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for item in data:
        item['標題'] = item['標題'][0]
        item['內容'] = item['內容'][0]
        if '留言' in item:
            item['留言'] = [text[0] for text in item['留言']]
        for key in ["留言分布圖", "留言分布","總平均","留言平均","標題和內容的平均"]:
            if key in item:
                del item[key]
   
   
    # 回傳為新的json
    with open('path_to_directory/queries_0_content_llm_ver.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 載入前處理後的檔案
def text_Loader(file_path_name):
    from langchain_community.document_loaders import JSONLoader
    
    loader = JSONLoader(
        file_path=f"path_to_directory/{file_path_name}",
        jq_schema='.',
        text_content=False,       
    )
    docs = loader.load()
    return docs


# 將文件切割為較小的段落，以利向量化與查詢
def splitting(docs):
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    
    # 使用 } 作為分隔符切割每段最多 100 字元。
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 100, 
        separators=["}"],  
        chunk_overlap=0,
        add_start_index=True
        )
    all_splits = text_splitter.split_documents(docs)

    # 將第一次切割的結果合併成每段 500 字元
    text_splitter_1 = RecursiveCharacterTextSplitter(
        chunk_size = 500, 
        chunk_overlap=0,
        add_start_index=True
        )
    all_splits_1 = text_splitter_1.split_documents(all_splits)
        
    return all_splits_1

# 轉換文本為向量
def embedding():
    from langchain_community.embeddings import OllamaEmbeddings

    embedding_name='chevalblanc/acge_text_embedding'
    embeddings = OllamaEmbeddings(model=embedding_name)  #(base_url=my_ollama_host,model=embedding_name)
    
    return embeddings

# 建立向量資料庫並產生 Retriever
def db(embeddings,all_splits_1):
    # 匯入 Chroma 向量資料庫與 shutil
    from langchain_community.vectorstores import Chroma
    import shutil

    # 資料夾存在則刪除，確保每次執行都是全新資料庫。
    persist_directory = f"./udn-db-acge" #'./udn-db'  #context/udn-db
    shutil.rmtree(persist_directory, ignore_errors=True)

    #建立 資料庫目錄
    vectorstore = Chroma.from_documents(documents=all_splits_1, embedding=embeddings, persist_directory=persist_directory)

    # 建立 retriever, 設定 top 1
    retriever = vectorstore.as_retriever(search_kwargs={"k":3},)# 查看DB筆數
    return retriever,vectorstore

# 設定 LLM, RAG
def LAM_RAG(retriever):
    from langchain_core.output_parsers import StrOutputParser
    from langchain_community.chat_models import ChatOllama 
    from langchain.prompts import ChatPromptTemplate
    from langchain_core.runnables import RunnableLambda, RunnablePassthrough

    # 選定 LLM 模組
    ollama_llm = "ycchen/breeze-7b-instruct-v1_0"
    model_local = ChatOllama(model=ollama_llm, temperature=0, num_predict=512, top_p=1, seed=42)
    
    # 自訂 Parser 移除換行符
    class SingleLineOutputParser(StrOutputParser):
        def parse(self, text: str) -> str:
            return text.replace("\n", " ")
        
    # Chain v2 (RAG+LLM)
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
    # 多份文件合併成一段文字作為上下文輸入
    template2 = """請根據以下參考資訊回答使用者提出的問題:
    ###
    參考資訊：{context}
    ###
    問題：{question}
    """
    # 設定 RAG 的提示模板：Context + 問題。
    prompt2 = ChatPromptTemplate.from_template(template2)
    chain_v2 = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt2
        | model_local
        | SingleLineOutputParser()
    )
    return chain_v2,format_docs
# 執行 RAG 問答，回傳 context 與生成結果
def RAG_LLM(chain_v2,user_question,retriever,format_docs):

    #獲取參考資訊（context）
    context_docs = retriever.invoke(user_question)
    context = format_docs(context_docs)

    # 執行chain_v2取得最終結果
    result = chain_v2.invoke(user_question)

    return context,result

