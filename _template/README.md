# 保障現況分析（保戶版）範本

財顧芸 陳芸琪 專用範本庫。**人物與數字全部虛構（示範：小安）**，不含任何客戶資料。

- `v4.13/`：同 v4.12，通行碼頁個資告知與網路版總目錄拿掉「且設定不被搜尋引擎收錄」（noindex 保護保留）（2026/10/03）
- `v4.12/xiaoan-review.html`：客戶版報告書範本（通行碼 xiaoan0929）
- `v4.12/xiaoan-plans.html`：方案第二頁範本
- `v4.12/index.html`：網路版總目錄範本
- `v4.12/00-總目錄-本機版.html`：顧問本機版總目錄範本

技能 annual-policy-review-report 在「沒附範本」時，會自動 `git clone https://github.com/angie26501-lgtm/private` 並使用本資料夾的最新版。
新版範本請另開資料夾（例：_template/v4.13/），並更新下方「最新版」。

最新版：v4.13

## index-flow/（2026/10/07 新增，母指令 v3.6 §7-1）
- 網路版總目錄「觀看流程版」範例（小安・全虛構）：`index-flow/index.html`；設定檔 `index-flow/config-example.json`。
- 一案 2 份以上報告時用 `python3 tools/index_flow.py 設定.json {代號}/index.html` 產生（版型取自 WISH 定稿）。
- 新案底稿：以最新上架案解密後為底（見 tools/README.md）；v4.13 為備援。

## 停用右鍵與複製（顧問 2026/10/10 確認）
- 所有上架的報告書頁面（客戶資料夾、_template、加密外殼 tools/gate_*）在 `</body>` 前加入 `tools/nocopy_snippet.html`（標記 `<!--nocopy:v1-->`）。
- 停用：右鍵選單、複製／剪下、拖曳、選取文字、Ctrl/Cmd＋C／X／A／S／U、F12、開發者工具快捷鍵。
- 不影響：輸入框與文字框（通行碼、回覆表單可正常輸入與貼上）、列印（報告書原本的列印權限照舊）、程式內的一鍵複製按鈕。
- 管理者版（檔名含 admin）與 course/ 公開頁不自動套用；course/blueprint-example.html 已個別套用。
- 這是防君子措施：擋得住一般使用者，擋不住截圖或懂技術的人。
