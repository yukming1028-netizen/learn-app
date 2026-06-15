# 親子學習互動平台 (LearnApp)

家長管控 + 子女使用的兒童學習 App，涵蓋 V1（QR綁定、基礎答題、題庫）和 V2（登入系統、錯題本 SM-2、PDF報告）。

## 技術棧

- **後端**: FastAPI + SQLAlchemy + SQLite (WAL mode)
- **前端**: Vue3 + Vite (家長端 + 子女端)
- **認證**: JWT + bcrypt (家長端), device UUID (子女端)
- **演算法**: 簡化版 IRT 動態難度 + SM-2 間隔重複
- **部署**: Docker Compose + Nginx

## 快速開始

### 本地開發

```bash
# 後端
cd backend
pip install -r requirements.txt
bash run.sh    # 初始化 DB + 載入 64 題種子數據 + 啟動

# 家長端
cd frontend-parent
npm install
npm run dev    # http://localhost:5173

# 子女端
cd frontend-child
npm install
npm run dev    # http://localhost:5174
```

### Docker 部署

```bash
docker compose up -d
# 家長端: http://localhost:8080
# 子女端: http://localhost:8081
# API:    http://localhost:8000
```

## 項目結構

```
learn_app-main/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models/        # Parent, Child, Question, Plan, AnswerRecord, ReviewSchedule
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── routers/       # auth, binding, children, questions, plans, progress, review, reports
│   │   ├── services/      # auth_service, adaptive_engine, review_engine, report_service
│   │   ├── middleware/    # rate_limit
│   │   ├── utils/         # qr
│   │   └── seed/          # 64 題種子數據
│   ├── tests/             # 42 tests (pytest)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend-parent/       # 家長端 Vue3
│   ├── src/
│   ├── Dockerfile
│   └── nginx.conf
├── frontend-child/        # 子女端 Vue3
│   ├── src/
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
└── docs/                  # 需求文檔, Figma腳本, Notion結構, 路線圖
```

## 核心功能

### V1
- 家長註冊/登入 (JWT)
- QR Code 綁定子女裝置 (5分鐘過期, HMAC-SHA256)
- 每家長最多 3 名子女
- 題庫: 64題 (小一至小三, 4學科, 難度1-5)
- 子女答題 + 動態難度 (簡化版 IRT)
- 學習計劃管理
- 家長 Dashboard (每日/每週趨勢, 學科分布)
- 遊戲化: 星星 + 成就

### V2
- 錯題本 + SM-2 間隔重複算法
- PDF 學習報告下載 (ReportLab)
- 答題統計分析

## 測試

```bash
cd backend
python3 -m pytest tests/ -v    # 42 tests
```
