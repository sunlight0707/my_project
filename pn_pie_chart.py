import matplotlib
import matplotlib.pyplot as plt
import io
import base64
import numpy as np 

# 設定 matplotlib 使用不需 GUI 的後端，適合在伺服器環境產圖
matplotlib.use('Agg')  

def sentent_np(results):
    data = results  # 將輸入的資料 results 存入變數 data
    ranges = [0, 0, 0, 0, 0]    # 用來統計五個情緒區間的數量

    # 根據每則貼文的「總平均」分數進行情緒分類
    for post in data:
        score = post['總平均']
        if -1 <= score < -0.6:
            ranges[0] += 1
        elif -0.6 <= score < -0.2:
            ranges[1] += 1
        elif -0.2 <= score < 0.2:
            ranges[2] += 1
        elif 0.2 <= score < 0.6:
            ranges[3] += 1
        elif 0.6 <= score <= 1:
            ranges[4] += 1
    
    # 定義每個區塊的顏色
    colors=['royalblue', 
               'cornflowerblue', 
               'navajowhite', 
               'lightcoral', 
               'indianred',  
               ]
    # 定義每個區塊對應的標籤，顯示分類與數量
    labels = [
        f'強烈負面情緒: {ranges[0]}',
        f'負面情緒: {ranges[1]}',
        f'中性情緒: {ranges[2]}',
        f'正面情緒: {ranges[3]}',
        f'強烈正面情緒: {ranges[4]}'
    ]
    # 設定中文字體與顯示負號
    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']  # 設置中文字體
    plt.rcParams['axes.unicode_minus'] = False  # 顯示負號


    # 為了讓 pie chart 不會因為某些區塊數量為 0 而繪圖異常，將 0 調整為 0.01
    adjusted_values = [0.01 if x == 0 else x for x in ranges]
    
    # 設定 pie chart 中百分比的格式
    def autopct_format(pct, allvalues):
        absolute = int(np.round(pct / 100. * np.sum(allvalues)))
        return f'{pct:.1f}%' if absolute != 0 else ''

    # 畫圓餅圖
    plt.figure(figsize=(5, 2.5), dpi=150)
    plt.pie(
        adjusted_values,
        textprops={'fontsize': 8, 'color': 'black'},
        colors=colors,
        pctdistance=0.8,
        radius=1.0,
        wedgeprops={'linewidth': 1.5, 'edgecolor': 'w'},
        startangle=90,
        autopct=lambda pct: autopct_format(pct, ranges)
    )

    # 顯示圖例
    plt.legend(labels, loc='best', fontsize=7)
    plt.axis('equal')
    plt.tight_layout()

     # 將圖存入記憶體中的 BytesIO 並轉成 base64 編碼，供 HTML 使用
    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=150)  # **DPI 控制在 150**
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    plt.clf()  # 清除當前圖形，避免重疊

    return plot_url # 回傳 base64 圖片字串（可嵌入 HTML）
