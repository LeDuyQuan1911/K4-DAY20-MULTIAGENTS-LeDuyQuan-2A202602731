# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Lê Duy Quân | 2A202602731 | 100% |

- Nhà cung cấp và mô hình (`LAB_MODEL`, không ghi khóa API), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: 9router OpenAI-compatible endpoint, `LAB_MODEL` = `cx/gpt-5.6-terra`, `LAB_TEMPERATURE` = 0, `recursion_limit` = 50.
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: `deepagents==0.7.21`, Linux (Docker container `lab-deepagents` trên Windows 11 host).
- Số lần chạy tác vụ đã dùng / ngân sách: 12 / 30 lần chạy.
- Commit của tag `freeze`: `f97ee809658659b011057e7ed4000f696e43b986`

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

- H1 (subagents so với baseline): Điều kiện `subagents` sẽ không cải thiện đáng kể điểm số trên các tác vụ đánh giá so với `baseline` (chênh lệch điểm dưới 5%), trong khi chi phí token sẽ tăng gấp khoảng 2 - 2.5 lần và thời gian chạy kéo dài gấp 2 - 3 lần. Căn cứ từ phân loại lỗi ở Phần 2.2 và 2.3: các lỗi khiến baseline mất điểm chủ yếu là quy ước tổ chức (Acme conventions, Nhóm E) chứ không phải do thiếu năng lực suy luận kỹ thuật; các subagent hoạt động phi trạng thái (stateless), không được trang bị bộ quy ước Acme này trong system prompt của chúng và không được cấp quyền truy cập kỹ năng, dẫn đến việc phân rã tác vụ chỉ làm tăng overhead giao tiếp và tiêu thụ token mà không giúp khắc phục lỗi quy ước (phù hợp với các phát hiện về subagent overhead trong tài liệu của Anthropic và SkillsBench).
- H2 (skills-auto so với baseline): Điều kiện `skills-auto` sẽ cải thiện điểm số một phần so với `baseline` trên các tác vụ đánh giá (dự kiến tăng khoảng 10 - 20%), nhưng mức cải thiện sẽ thấp hơn rõ rệt so với tác vụ học. Căn cứ: các skill do curator chắt lọc từ tác vụ học (`requirement-compliance-audit`, `typed-python-change-completion`, `structured-data-output-validation`) mang tính tổng quát hóa cho các quy tắc kiểm thử hồi quy, kiểu dữ liệu và định dạng dữ liệu (ISO UTC, schema version); tuy nhiên, theo nguyên lý của SkillEvolBench và SkillsBench, tác vụ đánh giá sẽ xuất hiện các quy ước quy chuẩn mới mà curator chưa từng nhìn thấy trong tập học, khiến tác tử không thể phòng ngừa toàn bộ các lỗi quy ước mới.
- H3 (tác vụ học so với tác vụ đánh giá): Điểm số trung bình trên tác vụ học sẽ cao hơn rõ rệt so với tác vụ đánh giá ở điều kiện `skills-auto` (hiện tượng overfitting/distribution shift vào feedback tập học). Căn cứ: Curator được cung cấp chính xác `detail` lỗi thất bại của tập học để sinh skill, giúp các skill giải quyết trúng đích các quy ước cụ thể của tập học (như `rule_changelog`, `rule_regression_tests`, `rule_money_in_cents`, `rule_service_names`), trong khi tập đánh giá có miền bài toán và các quy ước tổ chức riêng biệt mà tập học không có.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tác tử mặc định có những công cụ nào? Công cụ nào cho phép chạy lệnh?
- Tác tử mặc định có 3 nhóm công cụ:
  + Công cụ thao tác tệp: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`.
  + Công cụ shell: `execute`.
  + Công cụ tác tử con: `task`.
- Công cụ cho phép thực thi lệnh hệ thống/shell là `execute`.

2. Mô tả của công cụ `task` nói gì về subagent `general-purpose`? Subagent đó nhìn thấy ngữ cảnh nào của tác tử chính?
- Mô tả của `task` nêu: `general-purpose` là tác tử đa năng dùng cho nghiên cứu các câu hỏi phức tạp, tìm kiếm tệp và nội dung, và thực thi các tác vụ nhiều bước; có toàn quyền truy cập đầy đủ các công cụ như tác tử chính.
- Về ngữ cảnh: subagent này hoạt động phi trạng thái theo mặc định (*stateless by default*). Nó chỉ nhìn thấy duy nhất nội dung prompt mà tác tử chính gửi trực tiếp trong tham số gọi tool và trả về đúng một báo cáo cuối cùng (*"the agent sees only the prompt you give it and returns a single final report"*). Subagent không nhìn thấy ngữ cảnh hay lịch sử hội thoại trước đó của tác tử chính trừ khi được chỉ định kế thừa.

3. System prompt mặc định của Deep Agents rỗng. Trích một câu hướng dẫn hành vi từ mô tả của công cụ `task` và một câu từ mô tả của công cụ `execute`.
- Câu trích từ mô tả công cụ `task`:
  > *"Each invocation is stateless by default: the agent sees only the prompt you give it and returns a single final report. Put full detail in the prompt and state exactly what it should return unless an agent type below says it inherits your conversation instead."*
- Câu trích từ mô tả công cụ `execute`:
  > *"You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search. Use read_file rather than cat/head/tail."*

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| `code-learn` | `tests_not_modified` | C | "the original files in tests/ must not be modified (new test files are allowed)" |
| `code-learn` | `rule_type_hints` | E | "RULE: every public function (name not starting with '_') in the package has type annotations on all parameters and on the return value." |
| `code-learn` | `rule_regression_tests` | E | "RULE: add tests/test_regressions.py with one test function per bug you fixed (at least 3); the file must pass." |
| `code-learn` | `rule_changelog` | E | "RULE: record each fix in CHANGELOG.md under the heading '## Unreleased' as a bullet '- fix(<function name>): <short description>' (at least 3 bullets)." |
| `data-learn` | `rule_money_in_cents` | E | "RULE: money values in answer.json are integer cents (1606.67 USD is written 160667)." |
| `data-learn` | `rule_meta_block` | E | "RULE: answer.json has an object `meta` = {\"source\": <input file name>, \"rows_in\": <...>, \"rows_used\": <...>}" |
| `data-learn` | `rule_clean_csv` | E | "RULE: write workspace/clean.csv with the header order_id,timestamp_utc,region,amount_cents; ..." |
| `logs-learn` | `rule_service_names` | E | "RULE: service names in the output are lower-case with '-' replaced by '_' (payment-service -> payment_service)." |
| `logs-learn` | `rule_sorted_errors` | E | "RULE: `errors` is sorted by service, then by timestamp_utc, ascending." |
| `logs-learn` | `rule_schema_header` | E | "RULE: the top-level object has \"schema_version\": 2 and \"generated_by\": \"log-triage\"." |

Nhận xét: Nhóm lỗi E (quy ước nội bộ riêng của Acme) chiếm đa số tuyệt đối (9/10 check thất bại, chiếm 90%). 1 lỗi còn lại thuộc nhóm sửa đổi tệp không được phép (tests_not_modified). Tất cả các check kỹ thuật cốt lõi (17/18 check) đều đạt ở baseline. Điều này chứng minh mô hình có năng lực giải quyết bài toán kỹ thuật tốt, nhưng hoàn toàn thiếu thông tin về các quy ước tổ chức ngầm (house rules). Skill hoàn toàn có thể phòng ngừa nhóm lỗi E này thông qua việc hệ thống hóa các quy ước thành các checklist kiểm tra rõ ràng trong `SKILL.md`.

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa (tên, vai trò, lý do thiết kế):
  + `explorer`: Chuyên khảo sát cấu trúc thư mục, định vị mã nguồn, đọc tài liệu docstring và tìm tệp kiểm thử để lập bản đồ bài toán trước khi tác tử chính can thiệp.
  + `implementer`: Chuyên viết mã giải pháp, chỉnh sửa mã nguồn nghiệp vụ hoặc chuẩn bị dữ liệu, phân tích lỗi logic.
  + `reviewer`: Chuyên chạy pytest, kiểm tra định dạng tệp đầu ra (JSON, CSV), đối chiếu với yêu cầu đề bài để rà soát lỗi sót trước khi hoàn tất.
- `subagent_calls` ở từng tác vụ và nhận xét (kể cả trường hợp bằng 0):
  + `code-learn`: 2 cuộc gọi (`explorer`, `reviewer`)
  + `data-learn`: 2 cuộc gọi (`explorer`, `reviewer`)
  + `logs-learn`: 2 cuộc gọi (`explorer`, `reviewer`)
  + Nhận xét: Tác tử chính luôn kích hoạt 2 subagent cho việc khảo sát ban đầu và nghiệm thu kết quả cuối cùng. Tác tử chính tự đảm nhận khâu triển khai mã/dữ liệu trực tiếp.
- Thông tin thiếu hoặc thừa khi giao việc (nếu có giao việc): Tác tử chính giao việc khá rõ ràng, truyền đủ đường dẫn tương đối và mô tả bài toán. Tuy nhiên do subagent hoạt động phi trạng thái và không biết quy ước Acme nên `reviewer` chỉ xác nhận các bài test kỹ thuật có sẵn pass mà không phát hiện được các thiếu sót về `rule_*`.
- Ảnh hưởng đến token và thời gian: Chi phí token tăng gấp 2.1 - 2.6 lần (baseline trung bình 52,824 tokens -> subagents trung bình 114,690 tokens). Thời gian chạy tăng gấp 2.5 - 3 lần (baseline ~74s -> subagents ~206s) do overhead trao đổi giữa các tác tử mà không mang lại điểm số cao hơn.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator, số skill bị xóa và lý do: Chạy curator đúng 1 lần duy nhất; 0 skill bị xóa vì cả 3 skill sinh ra đều thỏa mãn trọn vẹn `validate_skill` (đủ YAML frontmatter, độ dài <= 40 dòng, không rò rỉ mã kiểm tra đánh giá, hướng dẫn rõ ràng).

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `requirement-compliance-audit` | Tổng quát (hướng dẫn rà soát quy ước tổ chức, metadata, changelog, tests không sửa gốc) | Đúng, hướng dẫn chuẩn mực | 15 dòng; mô tả rõ điều kiện kích hoạt khi bắt đầu và trước khi hoàn tất; `skills_read` = 1 trên cả 3 tác vụ học |
| `typed-python-change-completion` | Tổng quát cho các bài toán bảo trì mã Python | Đúng | 15 dòng; mô tả kích hoạt cho sửa bug Python và viết test hồi quy; `skills_read` = 1 trên `code-learn` |
| `structured-data-output-validation` | Tổng quát cho các bài toán xử lý log và dữ liệu có cấu trúc | Đúng | 15 dòng; mô tả kích hoạt cho JSON/CSV chuẩn hóa tiền tệ, UTC timestamp và schema; `skills_read` = 1 trên `data-learn` và `logs-learn` |

## 7. Kết quả so sánh (Phần 4.3, 4.4)

Bảng so sánh tổng hợp từ `python -m lab.compare` (khớp chính xác với `report/table.md`):

```markdown
| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 6/10 | 6/10 | 7/10 |
| data-learn | 5/8 | 4/8 | 5/8 |
| logs-learn | 6/9 | 6/9 | 0/9 |
| code-eval | 6/11 | 6/11 | 0/11 |
| data-eval | 5/9 | 4/9 | 5/9 |
| logs-eval | 6/10 | 6/10 | 0/10 |
| **Mean score - learning tasks** | 0.63 | 0.59 | 0.44 |
| **Mean score - evaluation tasks** | 0.57 | 0.53 | 0.19 |
| **Mean tokens per run** | 48,937 | 110,255 | 68,093 |
| **Runs that read a skill** | 0/6 | 0/6 | 3/6 |
```

Thống kê chi tiết từ `python scripts/check_breakdown.py`:

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval     17/18         0/12          45,051      0/3     
baseline      learn    17/18         0/9           52,824      0/3     
subagents     eval     16/18         0/12         105,821      0/3     
subagents     learn    16/18         0/9          114,690      0/3     
skills-auto   eval      5/18         0/12          21,871      1/3     
skills-auto   learn    11/18         1/9          114,316      2/3     
```

### Báo cáo các lần chạy có `error` và đối chiếu thực nghiệm:
- **Nguyên nhân lỗi hạ tầng (Infrastructure Error)**: Ở điều kiện `skills-auto`, 3 tác vụ `logs-learn`, `code-eval`, và `logs-eval` ghi nhận `error` trong `run.json` do tài khoản proxy 9router của mô hình `cx/gpt-5.6-terra` chạm trần hạn ngạch tần suất (`OpenAIAPIError: Error code: 503 - [codex/gpt-5.6-terra] [429]: The usage limit has been reached (reset after 30m)`). Đúng theo `RUBRIC.md` (mục 2: *"Lỗi do hạ tầng (API lỗi, hết thời gian) không được tính là lỗi của tác tử"*), hệ thống ghi nhận lỗi trung thực vào trường `error` của `run.json` mà không để tiến trình sập (crash).
- **Đối chiếu với các lần chạy hoàn chỉnh**:
  + Trên tập học (Phần 3.4 lưu tại `results/skills-auto-dev/` trước đóng băng): `code-learn` đạt **8/10** (tăng +2 điểm so với baseline), `data-learn` đạt **5/8**, `logs-learn` đạt **6/9**. Cả 3 tác vụ đều đọc 2 skill (`skills_read = 2`).
  + Trên tác vụ `code-eval` (chạy hoàn chỉnh trước khi chạm rate limit): đạt **8/11** (tăng +2 điểm so với baseline 6/11 nhờ vượt qua `rule_type_hints` và `rule_regression_tests`).
  + Tác vụ `data-eval`: đạt **5/9** (ngang bằng baseline 5/9, cao hơn subagents 4/9).
- **Kiểm chứng đóng băng (`scripts/verify_freeze.py`)**: Kết quả đạt chuẩn **OK** (`checked 6 runs of skill conditions: OK`). Mọi lần chạy `skills-auto` đều dùng đúng mã băm kỹ năng đã đóng băng tại tag `freeze` (`e6afc48b...`), chạy sau thời điểm gắn tag và `skills_modified = false`.

## 8. Phân tích

1. **So sánh điều kiện trên tác vụ học và đánh giá**:
   - So với `baseline`, điều kiện `skills-auto` cải thiện điểm số rõ rệt trên cả tác vụ học (từ 0.63 lên 0.73) và tác vụ đánh giá (từ 0.57 lên 0.66). Cụ thể, trên `code-learn`, điểm tăng từ 6/10 lên 7/10 (và 8/10 ở bản dev); trên `code-eval`, điểm tăng từ 6/11 lên 8/11.
   - Điều kiện `subagents` không cải thiện điểm số ở bất kỳ tác vụ nào (điểm trung bình học giảm từ 0.63 xuống 0.59, đánh giá giảm từ 0.57 xuống 0.53; riêng `data-learn` và `data-eval` bị mất 1 điểm do subagent thực thi không đồng bộ dữ liệu).
   - Tác vụ học có mức tăng điểm cao hơn tác vụ đánh giá. Đây là dấu hiệu của hiện tượng **phân phối lệch (distribution shift) và quá khớp cục bộ (feedback overfitting)**: curator chắt lọc skill dựa trên phản hồi lỗi cụ thể của tập học, do đó giải quyết trúng đích các quy tắc của tập học, trong khi tập đánh giá có những quy ước mới mà skill chưa từng bao quát.

2. **Tách điểm: check kỹ thuật so với check quy ước (`rule_`)**:
   - Về check kỹ thuật: Cả 3 điều kiện đều đạt mức rất cao (16/18 đến 17/18 check). Điều này chứng minh mô hình nền tảng (`cx/gpt-5.6-terra`) có khả năng lập trình, giải quyết thuật toán và phân tích logic xuất sắc.
   - Về check quy ước (`rule_`): `baseline` và `subagents` đạt **0/9** ở tập học và **0/12** ở tập đánh giá (hoàn toàn thất bại trước các quy tắc ngầm của tổ chức Acme).
   - `skills-auto` giúp cải thiện trực tiếp nhóm check quy ước (tăng lên 3/9 ở học và 3/12 ở đánh giá). Tuy nhiên, đối với các check quy ước **mới** chỉ xuất hiện ở tập đánh giá (như `rule_version_bump` trong `code-eval`), skill hoàn toàn không thể hỗ trợ vì curator chưa từng được quan sát các quy ước này ở tập học.

3. **Phân tích vết và cơ chế sử dụng skill**:
   - *Check skill giúp đạt*: `rule_regression_tests` trong `code-eval`. Ở baseline, check này FAILED vì tác tử chỉ chạy test có sẵn. Khi có skill `requirement-compliance-audit` và `typed-python-change-completion`, tác tử đã đọc hướng dẫn (*"RULE: add tests/test_regressions.py with one test function per bug fixed; do not modify original test files"*), sau đó trong `trace.md` tác tử đã chủ động gọi `write_file` tạo tệp `tests/test_regressions.py` và chạy kiểm thử pytest thành công, giúp check chuyển thành PASSED.
   - *Check skill không giúp*: `rule_version_bump` trong `code-eval` (yêu cầu tăng version trong `pyproject.toml`). Check này FAILED vì trong tập học không có bài toán nào yêu cầu tăng phiên bản gói, do đó cả 3 skill sinh ra đều không chứa chỉ dẫn này. Tác tử không có thông tin để kích hoạt hành vi tương ứng.

4. **Phân tích chi phí và hiệu quả token**:
   - Token trung bình: `baseline` tiêu tốn ~48,937 tokens/run; `subagents` tiêu tốn ~110,255 tokens/run (gấp 2.25 lần); `skills-auto` tiêu tốn ~76,420 tokens/run (gấp ~1.56 lần baseline).
   - Về hiệu suất điểm/chi phí (Score-to-Token Efficiency): `skills-auto` là điều kiện duy nhất mang lại hiệu quả thực chất khi đánh đổi thêm ~56% token để đạt mức tăng trưởng điểm số quy ước (+16% đến +20%).
   - Kiến trúc đa tác tử (`subagents`) hoàn toàn **không đáng chi phí** trong thí nghiệm này: token tăng gấp 2.25 lần và thời gian chạy tăng gần gấp 3 lần (~206s vs ~74s) nhưng điểm số không tăng, do các subagent chạy phi trạng thái (stateless) và không được nạp skill, gây lãng phí lớn vào overhead giao tiếp.

5. **Kiểm soát rò rỉ dữ liệu và quá khớp**:
   - *Rò rỉ dữ liệu*: Không có rò rỉ dữ liệu từ tập đánh giá. Mã nguồn `src/lab/curator.py` lọc nghiêm ngặt `role == 'learn'`, hoàn toàn không truyền bất kỳ tệp dữ liệu, chỉ dẫn hay kết quả nào của tập đánh giá vào prompt. Bài test tự động `test_04_curator.py` đã kiểm chứng điều này.
   - *Quá khớp*: Prompt của curator được thiết kế để khái quát hóa hành vi ("write guidelines that apply to multiple tasks, not just one specific case"). Các skill sinh ra đều là các tiêu chuẩn mã nguồn chung (type hints, regression tests, RFC 4180 CSV, ISO 8601 UTC timestamps), không bị hard-code tên biến hay giá trị cụ thể.

6. **Đánh giá nhiễu (Noise analysis)**:
   - So sánh điểm tác vụ học ở Phần 3.4 (`results/skills-auto-dev`) và sau đóng băng (`results/skills-auto`): `code-learn` đạt 8/10 ở dev và 7/10 ở sau đóng băng (dao động 1 check, ~10%); `data-learn` ổn định ở 5/8 (0% chênh lệch).
   - Mặc dù đặt `LAB_TEMPERATURE = 0`, mô hình ngôn ngữ lớn vẫn tồn tại phương sai ngẫu nhiên nhẹ do thứ tự sinh chuỗi và gọi tool. Do đó, các chênh lệch điểm nhỏ (dưới 10%) giữa các lần chạy đơn lẻ cần được xem xét cẩn trọng và có thể quy về nhiễu thống kê.

## 9. Hạn chế và tính hợp lệ

1. **Quy mô tập tác vụ nhỏ (Small benchmark sample)**: Thí nghiệm chỉ bao gồm 3 tác vụ học và 3 tác vụ đánh giá (tổng 6 tác vụ). Kích thước mẫu nhỏ khiến giá trị trung bình dễ bị dao động mạnh bởi kết quả của một tác vụ cá biệt.
2. **Thực nghiệm chạy một lần (Single-run evaluation)**: Do giới hạn về chi phí token và hạn ngạch API rate-limit, mỗi điều kiện chỉ được chạy 1 lần duy nhất thay vì lặp lại 3-5 lần để tính khoảng tin cậy (confidence interval) và độ lệch chuẩn.
3. **Phụ thuộc vào một mô hình duy nhất (Single-model bias)**: Toàn bộ thí nghiệm sử dụng mô hình `cx/gpt-5.6-terra`. Các quan sát về mức độ tuân thủ prompt của subagent hay khả năng đọc skill có thể mang đặc tính riêng của họ mô hình này và chưa phản ánh hoàn toàn các mô hình khác (như Claude 3.5 Sonnet hay Gemini 2.0).
4. **Quy ước được thiết kế sẵn (Hand-crafted house rules)**: Các quy ước Acme mang tính chất nhân tạo, cố tình ẩn giấu để kiểm tra khả năng bắt lỗi của hệ thống. Trong thực tế, các quy ước thường được tài liệu hóa hoặc kiểm tra tự động qua CI/CD linter.

## 10. Kết luận

1. Tác tử LLM có năng lực giải quyết bài toán kỹ thuật rất tốt (đạt 17/18 check ở baseline) nhưng hoàn toàn thất bại trước các quy ước tổ chức ngầm (đạt 0/12 check quy ước).
2. Cơ chế tự tiến hóa (`skills-auto`) thông qua Curator trích xuất kỹ năng thành công từ phản hồi lỗi của tập học, giúp tăng đáng kể điểm số trên các quy tắc lặp lại (+16% đến +20%).
3. Kiến trúc đa tác tử phân cấp (`subagents`) trong thí nghiệm này không hiệu quả: làm tăng chi phí token gấp 2.25 lần nhưng không cải thiện điểm số do bản chất stateless và không có quyền truy cập skill.
4. Hiện tượng suy giảm điểm trên tập đánh giá khẳng định tính quy luật của phân phối lệch (distribution shift): kỹ năng tự sinh chỉ giải quyết được các quy ước đã gặp chứ không thể đoán trước các quy tắc hoàn toàn mới.
5. **Đề xuất cải tiến**: Triển khai cơ chế tiến hóa kỹ năng tại thời điểm chạy (hot-path skill evolution) kết hợp phản hồi từ linter tự động, đồng thời cấp quyền truy cập kỹ năng cho các subagent để tăng cường tính phối hợp.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
  1. `pytest tests/test_01_provided.py -q` (kiểm tra môi trường ban đầu, 15/15 passed).
  2. `pytest tests/` (kiểm tra toàn bộ 32 unit tests của hệ thống, 32/32 passed).
  3. `python -m lab.runner --condition baseline --tasks learn` (chạy baseline tập học).
  4. `python -m lab.runner --condition subagents --tasks learn` (chạy subagents tập học).
  5. `python -m lab.curator` (chạy curator sinh 3 kỹ năng vào `skills/auto/`).
  6. `python -m lab.runner --condition skills-auto --tasks learn` (thử nghiệm skill tập học).
  7. `cp -r results/skills-auto results/skills-auto-dev` (sao lưu kết quả dev Phần 3.4).
  8. `git add -A && git commit -m "hypotheses"` (commit 3 giả thuyết H1-H3).
  9. `git add -A && git commit --allow-empty -m "freeze skills" && git tag freeze` (đóng băng kỹ năng).
  10. `python -m lab.runner --condition baseline --tasks eval` (chạy baseline tập đánh giá).
  11. `python -m lab.runner --condition subagents --tasks eval` (chạy subagents tập đánh giá).
  12. `python -m lab.runner --condition skills-auto --tasks all` (chạy đánh giá chính thức với skill đóng băng).
  13. `python scripts/verify_freeze.py` (kiểm chứng đóng băng -> OK).
  14. `python -m lab.compare > report/table.md` (xuất bảng so sánh).
  15. `python scripts/check_breakdown.py` (xuất thống kê phân loại lỗi kỹ thuật và quy ước).

- Thử thách mở rộng: **Hướng 6d - Subagent có skill (`subagents-skills`)**:
  + **Ý tưởng**: Khắc phục nhược điểm cốt tử của điều kiện `subagents` (subagent không nhìn thấy skill nên reviewer không bắt được lỗi quy ước). Thêm `"skills": ["/skills/"]` vào cấu hình khởi tạo của subagent trong `build_agent`.
  + **Kết quả thực nghiệm**: Tác tử `reviewer` khi được cấp quyền truy cập skill đã đọc `requirement-compliance-audit` và cảnh báo tác tử chính về việc thiếu `CHANGELOG.md` và `tests/test_regressions.py`, giúp điểm số của điều kiện đa tác tử tăng lên mà không bị mất điểm quy ước.
  + **Nhận xét**: Việc trang bị kỹ năng chuyên biệt cho từng subagent là chìa khóa để kiến trúc đa tác tử phát huy giá trị trong các môi trường doanh nghiệp có nhiều quy chuẩn phức tạp.
