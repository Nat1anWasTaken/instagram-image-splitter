# Instagram Image Splitter

一個簡單的腳本，讓美宣不用為了裁切圖片哀號

## 這能幹嘛？

你給它一個大圖，然後它會幫你分成很多個小圖讓你可以一個個上傳上 Instagram

## 特色

- 📸 **將大圖切割成 Instagram 網格貼文**  
  將一張大圖片切割為多張小圖，打造個人主頁上的整體視覺效果
- 🧠 **自動命名對應貼文順序**  
  圖片會以 `tile_1.jpg`、`tile_2.jpg` 的格式命名，方便上傳時保持順序
- 🧊 **左右安全區使用模糊延伸處理**  
  每張小圖左右各加上 32px 的安全線，避免 Instagram 自動裁切內容
- 📏 **符合 Instagram 建議尺寸**  
  每張輸出圖片皆為 1080 × 1350 像素，符合 Instagram 的直式貼文比例
- 🔧 **智慧判斷圖片大小不足時的處理方式**  
  若圖片尺寸小於網格需求，可選擇放大圖片或上下補黑邊，自由彈性
- 📐 **超出尺寸時自動以中心裁切**  
  圖片太大時會自動以畫面正中心為基準進行裁切，主體永遠不被切掉
- 🧭 **互動式指令列介面**  
  採用 [Inquirer](https://pypi.org/project/inquirer/)，以簡潔友善的問答介面引導操作流程。

## 使用方法

使用前，確保 [uv](https://github.com/astral-sh/uv) 和 [Python](https://www.python.org) 已經安裝在你的電腦上

### 1. 複製這個 Repository
```bash
git clone https://github.com/Nat1anWasTaken/instagram-image-splitter.git
```

### 2. 創建虛擬環境並安裝依賴
  ```bash
uv venv
uv pip install .
```

### 3. 啟用虛擬環境
#### Windows
```powershell
.venv\Scripts\activate
```
#### macOS and Linux
```bash
source .venv/bin/activate
```

### 4. 運行腳本
```bash
python main.py
```