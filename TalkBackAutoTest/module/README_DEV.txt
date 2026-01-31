TỔNG QUAN
---------
Module này cung cấp giao diện dòng lệnh để tự động hóa các thao tác trên PC Windows:
- Bật/Tắt Windows Narrator (trình đọc màn hình hỗ trợ khả năng tiếp cận)
- Gửi phím Tab để điều hướng giao diện
- Lấy thông tin phần tử UI đang được focus (mới)

YÊU CẦU HỆ THỐNG
----------------
- Hệ điều hành Windows (đã kiểm tra trên Windows 10/11)
- Python 3.x đã cài đặt và thêm vào PATH
- Thư viện uiautomation (cho chức năng lấy thông tin element):
    pip install uiautomation


CÁCH SỬ DỤNG DÒNG LỆNH
-----------------------

1. LẤY THÔNG TIN PHẦN TỬ ĐANG FOCUS (MỚI)
   Lệnh:
     python pc_automation.py get_focused
   
   Mô tả:
     Lấy thông tin về phần tử UI đang được focus hiện tại sử dụng 
     Microsoft UI Automation API thông qua thư viện uiautomation.
   
   Đầu ra (stdout):
     JSON object với các thuộc tính:
     - Name: Tên/label của element
     - LocalizedControlType: Loại control (button, edit, checkbox, v.v.)
     - BoundingRect: Toạ độ màn hình [left, top, right, bottom]
     - Value: Nội dung text (chỉ cho Edit, Document, ComboBox)
     - ToggleState: Trạng thái 'On'/'Off' (chỉ cho CheckBox, RadioButton)
     - ExpandCollapseState: 'Collapsed'/'Expanded' (chỉ cho ComboBox)
   
   Ví dụ output:
     {"Name": "Search", "LocalizedControlType": "edit", 
      "BoundingRect": [100, 200, 300, 250], "Value": "test", 
      "ToggleState": null, "ExpandCollapseState": null}
   
   Các loại control được hỗ trợ:
     - EditControl: Name, BoundingRect, Value
     - DocumentControl: Name, BoundingRect, Value
     - CheckBoxControl: Name, BoundingRect, ToggleState
     - RadioButtonControl: Name, BoundingRect, ToggleState
     - ComboBoxControl: Name, BoundingRect, Value, ExpandCollapseState
     - Control khác: Name, BoundingRect, LocalizedControlType (base properties)
   
   Xử lý lỗi:
     - Không có element focus: stdout = "null", stderr = thông báo lỗi
     - Pattern không hỗ trợ: thuộc tính = null
     - Control type không rõ: stderr = INFO, chỉ trả về base properties
   
   Mã thoát:
     0 = Thành công (có element)
     1 = Không có element focus hoặc lỗi

   Sử dụng từ C#:
     var psi = new ProcessStartInfo {
         FileName = "python.exe",
         Arguments = "module/pc_automation.py get_focused",
         RedirectStandardOutput = true,
         RedirectStandardError = true
     };
     var process = Process.Start(psi);
     string json = process.StandardOutput.ReadToEnd();
     string errors = process.StandardError.ReadToEnd();
     var info = JsonConvert.DeserializeObject<ElementInfo>(json);


2. BẬT/TẮT NARRATOR
   Lệnh:
     python pc_automation.py narrator
   
   Mô tả:
     Gửi tổ hợp phím tắt Ctrl + Win + Enter để bật/tắt Narrator.
     Chạy lần đầu sẽ BẬT Narrator, chạy lần thứ hai sẽ TẮT Narrator.
   
   Mã thoát:
     0 = Thành công
     1 = Thất bại


3. NHẤN PHÍM TAB VÀ QUÉT UI ELEMENTS (Tự động với Cycle Detection)
   Lệnh:
     python pc_automation.py tab
   
   Mô tả:
     Tự động nhấn phím Tab liên tục để duyệt qua tất cả các phần tử UI trong window hiện tại.
     Sau mỗi lần Tab, lấy thông tin element đang focus và xuất dưới dạng JSON.
     
     Tính năng Cycle Detection:
     - Tự động dừng khi phát hiện vòng lặp Tab quay lại element đã gặp
     - Sử dụng RuntimeId để track các element unique
     - Mỗi element chỉ xuất hiện 1 lần trong output
     - Không cần chỉ định số lần Tab, script tự động dừng đúng lúc
     
     Cách dừng thủ công:
     - Nhấn ESC bất kỳ lúc nào để dừng loop ngay lập tức
   
   Đầu ra:
     STDOUT: Một dòng JSON cho mỗi element unique (tương tự output của get_focused)
     STDERR: Log messages về tiến trình và kết quả
       - "Press ESC to stop" - khi bắt đầu
       - "CYCLE DETECTED at element #N. Stopping." - khi phát hiện vòng lặp
       - "Total unique elements: N" - tổng số element unique đã gặp
       - "Tab pressed N time(s)" - tổng số lần nhấn Tab
       - "Unique elements visited: N" - số element unique đã visit
       - "WARNING: Focus lost" - nếu focus bị mất giữa chừng
       - "WARNING: No RuntimeId for element #N" - nếu không lấy được RuntimeId
   
   Ví dụ output:
     STDERR: Press ESC to stop
     STDOUT: {"Name": "OK", "LocalizedControlType": "button", "Value": null, ...}
     STDOUT: {"Name": "Cancel", "LocalizedControlType": "button", "Value": null, ...}
     STDOUT: {"Name": "Search", "LocalizedControlType": "edit", "Value": "", ...}
     STDERR: CYCLE DETECTED at element #4. Stopping.
     STDERR: Total unique elements: 3
     STDERR: Tab pressed 4 time(s)
     STDERR: Unique elements visited: 3
   
   Xử lý lỗi:
     - RuntimeId không có: Skip cycle check cho element đó, tiếp tục loop
     - Focus lost: Dừng loop, log warning
     - ESC pressed: Dừng ngay lập tức
   
   Mã thoát:
     0 = Thành công (cycle detected hoặc ESC pressed)
     1 = Thất bại (lỗi kỹ thuật)


ĐỊNH DẠNG OUTPUT
-----------------
Script in ra STDOUT và STDERR riêng biệt:

STDOUT:
  - JSON data của UI elements (một object JSON mỗi dòng)
  - Dùng cho C# parsing và processing

STDERR:
  - Status messages: "Press ESC to stop", "CYCLE DETECTED", v.v.
  - Warning messages: "WARNING: Focus lost", "WARNING: No RuntimeId"
  - Statistics: "Tab pressed N time(s)", "Unique elements visited: N"
  - Error messages: "ERROR: [thông báo lỗi]"
  
Lưu ý: 
  - STDERR dùng cho logging/debug, không parse trong C#
  - STDOUT chỉ chứa JSON data thuần túy


HƯỚNG DẪN TÍCH HỢP C#
----------------------
Sử dụng Pattern RunCommand (Đã có sẵn trong MainForm.cs)

1. BẬT/TẮT NARRATOR:
    private void ToggleNarratorPC()
    {
        string modulePath = Path.GetDirectoryName(Application.ExecutablePath) 
                          + "\\module\\pc_automation.py";
        string command = "python \"" + modulePath + "\" narrator";
        string output = RunCommand(command, 2000);
        
        if (output.Contains("SUCCESS"))
        {
            printLog("Narrator đã được bật/tắt thành công");
        }
        else
        {
            printLog("Không thể bật/tắt Narrator: " + output, "error");
        }
    }

2. TỰ ĐỘNG QUÉT UI ELEMENTS VỚI TAB (Cycle Detection):
    private List<ElementInfo> ScanUIElements()
    {
        string modulePath = Path.GetDirectoryName(Application.ExecutablePath) 
                          + "\\module\\pc_automation.py";
        
        var psi = new ProcessStartInfo {
            FileName = "python.exe",
            Arguments = "\"" + modulePath + "\" tab",
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            UseShellExecute = false,
            CreateNoWindow = true
        };
        
        var process = Process.Start(psi);
        var elements = new List<ElementInfo>();
        
        // Đọc JSON từ stdout (mỗi dòng là 1 element)
        string line;
        while ((line = process.StandardOutput.ReadLine()) != null)
        {
            var element = JsonConvert.DeserializeObject<ElementInfo>(line);
            if (element != null)
            {
                elements.Add(element);
            }
        }
        
        // Đọc stderr để log (optional)
        string stderr = process.StandardError.ReadToEnd();
        if (!string.IsNullOrEmpty(stderr))
        {
            printLog("Tab scan info: " + stderr, "info");
        }
        
        process.WaitForExit();
        
        printLog($"Scanned {elements.Count} unique UI elements", "success");
        return elements;
    }

    Lưu ý:
    - Script tự động dừng khi phát hiện cycle, không cần timeout
    - Mỗi element chỉ xuất hiện 1 lần trong output
    - User có thể nhấn ESC để dừng sớm
    - Parse stderr nếu cần thông tin debug (cycle detected, warnings, v.v.)



DANH SÁCH KIỂM TRA TRIỂN KHAI
------------------------------
1. Đảm bảo thư mục module/ tồn tại trong thư mục dự án
2. Copy pc_automation.py vào thư mục module/
3. Cấu hình .csproj để bao gồm file module trong build output:
   
   <ItemGroup>
     <Content Include="module\pc_automation.py">
       <CopyToOutputDirectory>Always</CopyToOutputDirectory>
     </Content>
   </ItemGroup>

4. Xác minh Python đã được cài đặt trên máy đích
5. Kiểm tra các lệnh thủ công trước khi tích hợp C#
6. Thêm xử lý lỗi cho trường hợp thiếu Python trong code C#


KHẮC PHỤC SỰ CỐ
----------------

VẤN ĐỀ: "Python is not recognized as internal or external command"
GIẢI PHÁP: Thêm Python vào biến môi trường PATH của Windows

VẤN ĐỀ: Script chạy nhưng Narrator không bật/tắt
GIẢI PHÁP: Kiểm tra xem Narrator có bị vô hiệu hóa trong cài đặt Windows không
           (Settings > Accessibility > Narrator)

VẤN ĐỀ: Phím Tab không hoạt động trong một số ứng dụng
GIẢI PHÁP: Một số ứng dụng có thể bỏ qua SendInput vì lý do bảo mật.
           Kiểm tra với các ứng dụng Windows chuẩn trước.

VẤN ĐỀ: "ImportError: No module named ctypes"
GIẢI PHÁP: Cập nhật lên Python 3.x (ctypes là thư viện chuẩn trong Python 3+)

