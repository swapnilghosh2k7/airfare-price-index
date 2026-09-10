# VS Code Setup Guide for APIx Real‑time Airfare Price Index Platform

This guide walks you through opening the project in Visual Studio Code and configuring it to run both the **FastAPI backend** and the **React + Vite frontend** directly from the editor.

---

## Prerequisites

- **Windows 10/11** (you are on Windows).
- **VS Code** installed (latest stable version).
- **Python 3.11+** installed and added to `PATH`.
- **Node 20+** and **npm** installed (comes with Node).
- Optional but recommended: the **Python** and **Node.js** extensions for VS Code.

---

## 1️⃣ Open the Project Folder

1. Launch VS Code.
2. Choose **File → Open Folder…**.
3. Navigate to the project directory:
   ```
   C:/Users/kumar/.gemini/antigravity/scratch/apix_platform
   ```
4. Click **Select Folder**. VS Code will treat this as `${workspaceFolder}`.

---

## 2️⃣ Select a Python Interpreter

1. Press <kbd>Ctrl+Shift+P</kbd> → type **Python: Select Interpreter**.
2. Choose the interpreter you want to use (e.g., a virtual‑env or the global Python). If you prefer an isolated environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
   Then run **Python: Select Interpreter** and pick the `venv\Scripts\python.exe`.

---

## 3️⃣ Install Project Dependencies

### Backend (Python)
Open a terminal (**Terminal → New Terminal**) and run:
```bash
pip install -r backend/requirements.txt
```

### Frontend (Node)
In the same terminal (or a new one) run:
```bash
cd frontend
npm install
```

> The VS Code **Tasks** defined in `.vscode/tasks.json` can automate these steps (see below).

---

## 4️⃣ VS Code Debug/Run Configurations

The project ships with ready‑to‑use launch configurations located in `.vscode/launch.json`. They provide three ways to run the stack:

| Configuration | What it does |
|--------------|--------------|
| **Backend: FastAPI** | Starts `uvicorn backend.main:app --reload` on `http://127.0.0.1:8000`. |
| **Frontend: Vite Dev Server** | Runs `npm run dev` inside the `frontend` folder (React hot‑reload). |
| **Run Full Stack** (compound) | Launches both of the above simultaneously. |

### How to start a configuration
1. Open the **Run and Debug** view (<kbd>Ctrl+Shift+D</kbd>).
2. Select the desired configuration from the drop‑down at the top.
3. Press **F5** or click **Start Debugging**.

---

## 5️⃣ Using the Compound Launch (run both at once)

Select **Run Full Stack** in the drop‑down and press **F5**. VS Code will open two debug consoles:
- One for the FastAPI backend.
- One for the Vite dev server.

Both services will stay alive until you stop the debug session (press **Shift+F5** or click the red **Stop** button).

---

## 6️⃣ Alternative: One‑click Scripts

If you prefer not to use the VS Code debugger, the repository also includes two helper scripts:
- `scripts/run_app.bat` – launches the backend and the frontend in separate console windows.
- `scripts/run_app.ps1` – same as above for PowerShell.

You can run them directly from a terminal:
```bash
./scripts/run_app.bat   # CMD / batch
# or
./scripts/run_app.ps1   # PowerShell
```

---

## 7️⃣ Verify the Setup

1. After the backend starts, open a browser and go to `http://127.0.0.1:8000/health`. You should see a JSON `{ "status": "ok" }`.
2. The Vite dev server serves the UI at `http://127.0.0.1:5173`. It will proxy API calls to the FastAPI server (see `frontend/vite.config.js`).
3. The integrated UI should load the KPI dashboard and allow you to manually trigger the scraper via the **Header** component.

---

## 8️⃣ Tips & Gotchas

- **Port conflicts** – If another process is already using `8000` or `5173`, change the ports in `launch.json` (backend `--port` argument) and `frontend/vite.config.js` (the dev server `port` option).
- **Environment variables** – The current code does not require any special env vars. If you add secrets later, place them in a `.env` file at the project root and reference them in `backend/main.py` with `python‑dotenv`.
- **Automatic reload** – The `--reload` flag in the FastAPI launch config watches Python files and restarts the server on change. The Vite dev server already provides hot‑module replacement for the React UI.

---

## 9️⃣ Summary

1. Open the folder in VS Code.
2. Pick a Python interpreter.
3. Install backend (`pip install -r backend/requirements.txt`).
4. Install frontend (`cd frontend && npm install`).
5. Use **Run → Start Debugging** (F5) with **Backend: FastAPI**, **Frontend: Vite Dev Server**, or **Run Full Stack**.
6. Verify endpoints and UI.

You now have a fully integrated development environment for the APIx platform inside VS Code! 🎉
