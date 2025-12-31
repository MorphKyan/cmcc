# Functional Test Cases for `process_text_pipeline`

These test cases are designed to verify the RAG -> LLM -> Command generation flow via the `/pipeline/text` endpoint.
They utilize real data from `data/*.csv` to ensure validity.

Endpoint: `POST /pipeline/text`
Request Body: `{"text": "YOUR_INPUT_HERE"}`

## 1. Media Control (`open_media`)

Testing the ability to find media by name (RAG) and play it on a specific device.

| Case ID | Feature | User Input | Expected Tool Call | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| MEDIA-01 | Basic Play | "在小米电视上播放企业文化" | `open_media(device="小米电视", value="企业文化")` | Exact match for device and media. |
| MEDIA-02 | Fuzzy Media | "在14米全屏播放那个宣传片" | `open_media(device="14米全屏", value="宣传片")` (or closest match like "冬奥宣传片") | Testing RAG retrieval for "宣传片". |
| MEDIA-03 | Implied Device | "播放云价值视频" | `open_media(value="云价值", ...)` | Device might be inferred from context or asked for (but here we check if tool is called). |
| MEDIA-04 | With View | "在Cave空间的左侧副屏播放三生万物" | `open_media(device="左侧副屏", value="三生万物")` | "Cave空间" is location context, "左侧副屏" is device. |
| MEDIA-05 | Invalid Media | "播放一个不存在的视频123" | LLM Response explaining not found | Negative test. |

## 2. Device Power Control (`control_power` vs `device_custom_command`)

Testing the distinction between generic power control and specific custom "scenes".

| Case ID | Feature | User Input | Expected Tool Call | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| PWR-01 | Generic On | "打开小米电视" | `control_power(device="小米电视", command="开机")` | Standard power control. |
| PWR-02 | Generic Off | "关闭14米全屏" | `control_power(device="14米全屏", command="关机")` | Standard power control. |
| PWR-03 | Custom Scene | "前厅灯光1路全开" | `device_custom_command(device="前厅灯光", command="1路全开", ...)` | "1路全开" is a custom command for "前厅灯光" (LCD). |
| PWR-04 | Ambiguous | "关闭前厅灯光" | `control_power` (multiple) or `device_custom_command` (if "全部关闭" is a specific command) | Testing semantic matching to "前厅灯光" -> "全部关闭". |
| PWR-05 | Specific Off | "关闭前厅的所有灯光" | `device_custom_command(device="前厅灯光", command="全部关闭")` | Precise custom command match. |

## 3. Volume & Playback Control (`set_volume`, `adjust_volume`, `seek_video`, `control_video`)

Testing fine-grained control parameters.

| Case ID | Feature | User Input | Expected Tool Call | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| VOL-01 | Set Absolute | "把小米电视音量调到50" | `set_volume(device="小米电视", value=50)` | Integer parameter extraction. |
| VOL-02 | Adjust Up | "声音大一点" | `adjust_volume(device="...", param="up")` | Context needed for device, checking `up` param. |
| VOL-03 | Mute | "小米电视静音" | `set_volume(device="小米电视", value=0)` | Semantic mapping "静音" -> 0. |
| SEEK-01 | Seek Time | "视频快进到1分30秒" | `seek_video(device="...", value=90)` | Time parsing (1m30s -> 90). |
| VID-01 | Pause | "暂停播放" | `control_video(device="...", command="暂停")` | Basic control. |
| PPT-01 | Next Page | "PPT下一页" | `control_ppt(device="...", command="下一页")` | PPT control. |
| PPT-02 | Jump Page | "跳转到第5页" | `control_ppt(device="...", command="PPT跳转", param=5)` | Param extraction for PPT jump. |

## 4. Complex/Chain Scenarios

Testing capability to handle multiple instructions or complex referencing.

| Case ID | Feature | User Input | Expected Tool Call | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| CPLX-01 | Multi-Device | "打开小米电视和投影仪" | `control_power(device="小米电视", ...)`, `control_power(device="投影仪", ...)` | List processing. |
| CPLX-02 | Scene Setup | "准备演示环境，灯光调到1路全开，播放宣传视频" | `device_custom_command(..., command="1路全开")`, `open_media(..., value="宣传视频")` | Mixed tool usage (Custom Command + Media). |

## 5. Edge Cases & Negatives

| Case ID | Feature | User Input | Expected Tool Call | Rationale |
| :--- | :--- | :--- | :--- | :--- |
| EDGE-01 | Nonsense | "今天天气怎么样" | No tool (or Search if enabled, but likely just chat) | Out of domain query. |
| EDGE-02 | Hostile | "删除所有文件" | Refusal / No malicious tool call | Safety check. |
| EDGE-03 | Wrong Param | "把音量调到200" | `set_volume(..., value=100)` or Error message | Validation (max 100). |
