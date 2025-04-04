# Instagram Image Splitter

一個簡單的腳本，讓美宣不用為了裁切圖片哀號

## 這能幹嘛？

你給它一個大圖，然後它會幫你分成很多個小圖讓你可以一個個上傳上 Instagram

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