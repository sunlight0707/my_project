import json
import numpy as np
from ckip_transformers.nlp import CkipWordSegmenter
from snownlp import SnowNLP
import matplotlib
import matplotlib.pyplot as plt
# matplotlib.use('Agg')  # 使用不需要 GUI 的後端
import base64
from io import BytesIO
from ckip_transformers.nlp import CkipWordSegmenter

# 初始化 CKIP 分詞器
word_segmenter = CkipWordSegmenter(model="bert-base")

# CKIP 分詞函數
def ckip_cut(text):
    result = word_segmenter([text])  # CKIP 分詞輸入需為列表
    return result[0]  # 返回分詞結果

# 自定義 SnowNLP
class SnowNLPWithCkip(SnowNLP):
    def __init__(self, text):
        # 使用 CKIP 分詞後重新組合文本
        words = ckip_cut(text)
        processed_text = " ".join(words)  # 合併為新的分詞結果
        super().__init__(processed_text)

# 讀取資料檔案
with open('pre_pare/all_dc_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

results = []

# 設置圖片格式
fig = plt.figure(figsize=(4,4))
x_edges = ['-1~-0.6', '-0.6~-0.2', '-0.2~0.2', '0.2~0.6', '0.6~1']

ax = plt.subplot()
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']  # 設置中文字體
plt.setp(ax.get_xticklabels(),
          color='#00f',
          fontsize=8,
          rotation=30)  
plt.xlabel("分數組距")
plt.ylabel("數量")

buffer = BytesIO()  # 創建 BytesIO 物件來儲存圖片數據

for post in data:
    # 標題分數
    title_score = SnowNLPWithCkip(post["標題"]).sentiments*2-1 if post["標題"] else 0
    # 內容分數
    content_score = SnowNLPWithCkip(post["內容"]).sentiments*2-1 if post["內容"] else 0
    #標題內容平均數
    title_content_average = (title_score + content_score) / 2

    # 留言的情感分數
    if "留言" in post and post["留言"]:
        comment_plus_score = [(comment,(SnowNLPWithCkip(comment).sentiments)*2-1) for comment in post["留言"] if comment]
    else:
        pass
    comment_scores = [score for _, score in comment_plus_score]
    if len(comment_scores)==0:
        comments_average = 0
    else:
        comments_average = sum(comment_scores) / len(comment_scores)
    
    # 總平均情感分數（加權計算）
    average = (title_content_average*3 + comments_average*2)/5
    
    # 計算每個情感範圍內的留言數量
    first=second=third=forth=fifth=0
    sent_score=[]
    for i in range(len(comment_scores)):
        if -1<= comment_scores[i] and comment_scores[i]<-0.6:
            first = first+1
        elif -0.6<= comment_scores[i] and comment_scores[i]<-0.2:
            second = second+1    
        elif -0.2<= comment_scores[i] and comment_scores[i]<0.2:
            third =third+1
        elif 0.2<= comment_scores[i] and comment_scores[i]<0.6:
            forth =forth+1
        elif 0.6<= comment_scores[i] and comment_scores[i]<=1:
            fifth = fifth+1
    sent_score.extend([first,second,third,forth,fifth])
    
    # 繪製情感分布圖
    y_values = sent_score
    plt.bar(x_edges, 
        y_values, 
        width=0.4, 
        align='center', 
        color=['lightsteelblue', 
               'cornflowerblue', 
               'royalblue', 
               'midnightblue', 
               'navy',  
               ])
    plt.savefig(buffer, format="png") 
    plt.close()  # 關閉繪圖

    # 將圖片轉換為 Base64 字串
    buffer.seek(0) 
    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    
    # 將每篇文章的結果儲存到結果列表中
    results.append({
        "標題": (post["標題"],title_score),
        "日期": post["日期"],
        "心情": post["心情"],
        "內容": (post["內容"],content_score),
        "標題和內容的平均":title_content_average,
        "留言平均":comments_average,
        "總平均": average,
        "留言分布":sent_score,
        "留言分布圖":image_base64,
        "留言": comment_plus_score
    })


# 將處理結果寫入 JSON 檔案
with open(f'all_dc_ckip.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=4,sort_keys=False, ensure_ascii=False)
    