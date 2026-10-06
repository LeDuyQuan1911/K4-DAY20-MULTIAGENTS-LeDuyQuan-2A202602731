# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Lê Duy Quân | 2A202602731 | 100% |

- Nhà cung cấp và mô hình (`LAB_MODEL`, không ghi khóa API), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: 9router OpenAI-compatible endpoint, `LAB_MODEL` = `cx/gpt-5.6-terra`, `LAB_TEMPERATURE` = 0, `recursion_limit` = 50.
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: `deepagents==0.7.21`, Linux (Docker container `lab-deepagents` trên Windows 11 host).
- Số lần chạy tác vụ đã dùng / ngân sách: 12 / 30 lần chạy.
- Commit của tag `freeze`: (sẽ cập nhật sau khi tạo tag `freeze`)

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

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:
