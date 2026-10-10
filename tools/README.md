# tools｜保障現況分析（保戶版）共用工具

母指令（技能 annual-policy-review-report）v3.9 對應。所有工具只處理本機檔案，不上傳任何東西。

| 檔案 | 用途 | 章節 |
|---|---|---|
| `encrypt.py` | 單組通行碼加密（舊案用） | §6 |
| `multi_enc.py` | 多組通行碼加密〔客戶, 教練一, 教練二…〕＋開啟紀錄＋教練聲明；`--ck` 把雲華陀金鑰只包進客戶 slot | §15 §21 §30 |
| `gate_shell_multi.html` | multi_enc 用的解密外殼（記住 30 天存 DEK） | §15 |
| `dec_multi.py` | 解密線上報告（多組／單組都可），全盤檢視、交叉核對、防覆蓋用 | §12 §20 §27 |
| `adv_notes.py` | 顧問筆記 📝、顧問版切換、筆記選單、🔒 列印、🔒 管理者專區（管理者密碼另一層加密） | §14 §16 §19 §23 |
| `review_kit.py` | 產生器共用元件：donut／card（四大支柱）、rows／tbody_replace（明細表）、tour_resize（導覽視窗調整大小）、cloud_link／remove_cloud（P4 雲華陀框） | §2 §30 §31 |
| `index_flow.py` | 網路版總目錄「觀看流程版」（WISH 定稿），範例設定在 `_template/index-flow/` | §7-1 |
| `cloud_pdf_page.py` + `gate_page.html` | 多份報告時的「健診分析規劃書（PDF）」附件頁，只用客戶碼加密 | §30-2 |
| `nocopy_snippet.html` | 停用右鍵與複製片段（`<!--nocopy:v1-->`），上架頁 `</body>` 前原文貼上；加密外殼已內建 | §32 |
| `check.py` | 上傳前檢查，全 ✅ 才上傳 | §8 |

底稿：新案以「最新上架案」解密後的內容為底（`dec_multi.py`），用 build.py＋`review_kit.py` 只換客戶資料；`_template/v4.13/` 為備援。
