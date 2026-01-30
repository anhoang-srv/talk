## 1. Cập nhật hàm run_tab_sequence() với cycle detection

- [ ] 1.1 Thêm biến `seen_runtime_ids = set()` để tracking RuntimeIds đã gặp
- [ ] 1.2 Thêm biến `count` để đếm số lần nhấn Tab (để log)
- [ ] 1.3 Sau `press_tab()`, thêm logic lấy RuntimeId: `element = auto.GetFocusedControl()` và `runtime_id = element.GetRuntimeId()`
- [ ] 1.4 Wrap `GetRuntimeId()` trong try-except để handle exception, set `runtime_id = None` nếu lỗi
- [ ] 1.5 Thêm check `if element is None: break` sau `GetFocusedControl()` để handle focus lost
- [ ] 1.6 Thêm cycle detection logic: `if runtime_id and runtime_id in seen_runtime_ids: break`
- [ ] 1.7 Thêm `seen_runtime_ids.add(runtime_id)` sau cycle check (trước output)
- [ ] 1.8 Log warning ra stderr nếu `runtime_id is None`: "WARNING: No RuntimeId for element, skipping cycle check"

## 2. Cập nhật logging messages

- [ ] 2.1 Giữ nguyên message "Press ESC to stop" khi bắt đầu loop
- [ ] 2.2 Thêm log "CYCLE DETECTED at element #{count}. Stopping." khi detect cycle
- [ ] 2.3 Thêm log "Total unique elements: {len(seen_runtime_ids)}" sau cycle detected message
- [ ] 2.4 Thêm log "WARNING: Focus lost" khi `element is None`
- [ ] 2.5 Cập nhật end message: "Tab pressed {count} time(s)" và "Unique elements visited: {len(seen_runtime_ids)}"
- [ ] 2.6 Đảm bảo tất cả log đều dùng `file=sys.stderr`

## 3. Verify không breaking changes

- [ ] 3.1 Kiểm tra JSON output format vẫn giống cũ (không có RuntimeId trong JSON)
- [ ] 3.2 Verify ESC mechanism vẫn hoạt động (check `is_escape_pressed()` ở đầu loop)
- [ ] 3.3 Verify hàm `get_focused_element_info()` không bị thay đổi
- [ ] 3.4 Verify CLI command `tab` vẫn call `run_tab_sequence()` như cũ

## 4. Testing

- [ ] 4.1 Test với simple dialog có cycle rõ ràng (3-4 controls)
- [ ] 4.2 Verify output chỉ có unique elements, không duplicate
- [ ] 4.3 Verify message "CYCLE DETECTED" xuất hiện trong stderr
- [ ] 4.4 Test ESC mechanism vẫn dừng được loop
- [ ] 4.5 Test với window phức tạp (nhiều controls) để verify RuntimeId khác nhau
- [ ] 4.6 Test edge case: Focus vào window khác giữa chừng (focus lost)
- [ ] 4.7 Verify statistics log đúng: Tab count và unique element count

## 5. Code cleanup và documentation

- [ ] 5.1 Kiểm tra không có code duplication
- [ ] 5.2 Đảm bảo tất cả error handling paths đều có log
- [ ] 5.3 Review code comments trong `run_tab_sequence()` để giải thích logic mới
- [ ] 5.4 Compile check: `python -m py_compile TalkBackAutoTest/module/pc_automation.py`
- [ ] 5.5 Xoá file test `tess.py` nếu không cần nữa (hoặc giữ lại cho reference)
