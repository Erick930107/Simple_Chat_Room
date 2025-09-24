# Python Socket Chatroom with GUI

這是一個使用 **Python socket + Tkinter** 製作的聊天室系統，支援多人即時聊天、訊息回覆、輸入中提示，並且有簡單的圖形化介面。

## 功能特色
- 支援多人聊天室（TCP 連線）
- GUI 介面（Tkinter）
- 訊息靠左/靠右顯示（自己 vs 其他人）
- 即時「正在輸入…」提示
- 右鍵選單 → Reply，能回覆特定訊息
- 使用 UDP 廣播同步訊息給所有客戶端

## 專案結構
~~~
chatroom/
├─ server.py # 聊天伺服器
├─ client1.py # 聊天客戶端 (GUI)
├─ client2.py # 聊天客戶端 (GUI)
├─ client3.py # 聊天客戶端 (GUI)
└─ README.md 
~~~

## 使用方式

### 1. 啟動伺服器
在一個終端機執行：
```bash
python server.py
```
2. 啟動客戶端
開啟另一個終端機，執行：

```bash
python client1.py
```
程式會跳出 Tkinter 視窗，並要求輸入暱稱。
你也可以同時執行 client2.py、client3.py 來模擬多個使用者。

## 使用示範

1. 輸入暱稱後進入聊天室。

2. 在輸入框輸入訊息並按 Enter 或 Send 發送。

3. 若有人正在輸入，會顯示「xxx is typing…」。

4. 可以選取訊息後 右鍵 → Reply，在輸入框中自動帶入回覆內容。

## 使用技術

* 程式語言：Python

* 使用套件：

    * socket → TCP & UDP 傳輸
    
    * threading → 多執行緒處理 Client
    
    * tkinter → 圖形化介面

* 通訊協定：

    * TCP：Client ↔ Server 訊息傳遞
    
    * UDP：Server 廣播訊息給所有 Client
