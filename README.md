# 资产出入库管理系统

一个轻量的资产出入库（库存收发）管理系统，包含 FastAPI + SQLite 后端和 React + Vite 前端。

## 功能

- **出入库管理**：登记入库 / 出库单，自动更新库存结存并记录流水
  - 出库时校验库存，不足自动拦截
  - 支持按关键字、类型、日期区间筛选，分页浏览
  - 每条流水留存操作人、单据号、备注与操作后结存，便于回溯对账
  - 出库登记「领用人」「出库放置地点」；入库登记「入库放置地点」
  - 支持「归还入库」：选择原出库单后自动套用领用人，并按未归还数量校验
- **资产台账**：维护资产编码、名称、类别、规格、位置、单价、安全库存
  - 低库存自动预警（库存 ≤ 安全库存）
  - 类别筛选、关键字搜索、新增、删除
- **统计看板**：资产种类、当前库存、库存总值、今日/本月出入库、低库存数量

## 目录结构

```
backend/            FastAPI 后端
  app/
    api/            HTTP 路由（assets、stock）
    core/           配置
    db/             引擎、会话、Base
    models/         资产、出入库模型
    schemas/        Pydantic 模型
    services/       业务逻辑（出入库、库存校验、统计）
    main.py         应用入口
frontend/           React + Vite 前端
  src/
    views/          出入库、资产台账页面
    components/     统计卡片、弹窗、表单
    api.ts          接口封装
scripts/            启动脚本
```

## 快速开始

### 后端

```bash
cd backend
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/uvicorn app.main:app --reload --port 8010
```

或使用脚本：`./scripts/dev-backend.sh`

首次启动会自动建表并写入 3 条示例资产。接口文档见 http://127.0.0.1:8010/docs 。

### 前端

```bash
cd frontend
npm install
npm run dev
```

或使用脚本：`./scripts/dev-frontend.sh`（需先启动后端）。

访问 http://localhost:5180 ，前端通过 Vite 代理将 `/api` 转发到后端 8010 端口。

## 主要接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/api/assets` | 资产列表（keyword / category / low_stock_only / 分页） |
| POST | `/api/assets` | 新增资产 |
| PUT | `/api/assets/{id}` | 更新资产 |
| DELETE | `/api/assets/{id}` | 删除资产 |
| GET | `/api/assets/categories` | 类别列表 |
| GET | `/api/stock/movements` | 出入库流水（keyword / type / start / end / 分页） |
| POST | `/api/stock/movements` | 新建入库 / 出库单（支持归还入库 return_of_id） |
| GET | `/api/stock/outstanding` | 某资产未全部归还的出库记录（归还选择用） |
| GET | `/api/stock/stats` | 库存统计 |

## 桌面应用（Linux / Windows）

桌面版使用本地 SQLite 数据库，不需要单独部署服务器；前端和后端会被打包进一个原生窗口应用。数据库会自动保存到当前用户的数据目录：

- Windows：`%APPDATA%\\AssetManagement\\asset_management.db`
- Linux：`~/.local/share/AssetManagement/asset_management.db`

### Windows 打包

在 Windows PowerShell 中执行（需要提前安装 Python、Node.js）：

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\\scripts\\build-desktop-windows.ps1
```

产物：`backend\\dist\\AssetManagement\\AssetManagement.exe`。将整个 `AssetManagement` 文件夹复制到目标 Windows 电脑，双击 exe 即可运行。

### Linux 打包

在 Linux 中执行：

```bash
./scripts/build-desktop-linux.sh
```

产物：`backend/dist/AssetManagement/AssetManagement`。可将整个 `AssetManagement` 文件夹复制到同发行版的 Linux 电脑运行。若系统缺少 Qt/WebEngine 运行库，请安装对应发行版的 Qt5 WebEngine 包。

### 本地桌面运行（开发调试）

```bash
./scripts/run-desktop.sh
```

Linux 和 Windows 的桌面安装包必须分别在对应系统上构建（PyInstaller 不支持在 Linux 上直接生成 Windows exe，反之亦然）。


后端通过环境变量（前缀 `AMS_`）覆盖默认配置，例如：

```bash
export AMS_DATABASE_URL="sqlite:////data/ams.db"
```
