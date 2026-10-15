@echo off
echo ========================================================
echo   Restoring Previous BTC Backtesting Chat Session
echo   Session ID: 43ef7b14-be10-4620-9856-02fcb8643b0e
echo ========================================================

python -c "import sqlite3, json; p = r'C:\Users\Jay Patel\AppData\Roaming\Antigravity IDE\User\profiles\5be2226b\globalStorage\state.vscdb'; conn = sqlite3.connect(p); cur = conn.cursor(); cur.execute(\"SELECT value FROM ItemTable WHERE key='google.antigravity'\"); d = json.loads(cur.fetchone()[0]); d['antigravity.workspaceCascadeMap']['file:///f%3A/multi%20agent'] = '43ef7b14-be10-4620-9856-02fcb8643b0e'; cur.execute(\"UPDATE ItemTable SET value=? WHERE key='google.antigravity'\", (json.dumps(d),)); conn.commit(); conn.close(); print('[?] Active conversation successfully reset to 43ef7b14-be10-4620-9856-02fcb8643b0e')"

echo.
echo [?] Done! You can now launch Antigravity IDE and it will open into your old chat!
pause
