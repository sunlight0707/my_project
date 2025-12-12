# Project Root

## 📘 專案說明
此專案主要用於 **展示與參考 Python 專案的資料結構與處理流程**。  
內容包含程式碼、範例資料、模板及樣式檔，供他人作為學習或專案架構參考使用。  
> ⚠️ 本專案僅供瀏覽參考，並非可直接執行的應用程式。

---
## 📁 專案結構

project_root/
   │
   ├── .venv/                      # Python 虛擬環境（未上傳）
   ├── pre_pare/                   # 資料預處理腳本與原始資料
   │   ├── all_dc_data/            # 拆分後的 JSON 資料
   │   ├── cloudscraper_text.py
   │   ├── dcard_*.xlsx
   │
   ├── path_to_directory/          # JSON 結果資料
   │   ├── queries_0_content.json
   │   ├── queries_1_content.json
   │   └── queries_2_content.json
   │
   ├── static/                     # CSS 樣式
   ├── templates/                  # HTML 模板
   ├── app.py                      # 主程式架構展示（Flask 範例）
   ├── pn_pie_chart.py             # 圖表生成範例
   ├── rag_breeze.py               # RAG 模型範例
   └── README.md


## 💡 使用方式
1. **瀏覽專案架構**：  
   查看資料夾結構、程式邏輯與命名方式。

2. **參考程式碼**：  
   部分 `.py` 檔案展示了資料處理、分析與簡易網頁應用的範例結構。

3. **不需執行程式**：  
   專案主要用於展示，若需運行需自行建立虛擬環境與安裝依賴。

---

## ⚙️ 注意事項
- `.venv/` 未上傳（虛擬環境不包含在版本控制中）  
- 大型 JSON 檔案使用 **Git LFS** 管理，瀏覽時請先執行：
  ```bash
  git lfs install
  git lfs pull
GitHub 對單檔大小限制為 100MB，因此部分資料拆分存放於 /pre_pare/all_dc_data/

所有檔案僅供學術與程式結構參考，不建議直接應用於生產環境。






