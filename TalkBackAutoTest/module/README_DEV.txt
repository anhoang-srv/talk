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


3. NHẤN PHÍM TAB (Đơn lẻ)
   Lệnh:
     python pc_automation.py tab
   
   Mô tả:
     Gửi một lần nhấn phím Tab để di chuyển focus sang phần tử UI tiếp theo.
   
   Mã thoát:
     0 = Thành công
     1 = Thất bại


3. NHẤN PHÍM TAB (Nhiều lần)
   Lệnh:
     python pc_automation.py tab <số_lần>
   
   Ví dụ:
     python pc_automation.py tab 5
   
   Mô tả:
     Gửi phím Tab <số_lần> lần với độ trễ phù hợp.
     Hữu ích để điều hướng qua nhiều phần tử UI.
   
   Mã thoát:
     0 = Thành công
     1 = Thất bại


ĐỊNH DẠNG OUTPUT
-----------------
Script in ra STDOUT theo định dạng:

  ACTION: [mô tả hành động]
  SUCCESS: [thông báo xác nhận]

Khi có lỗi, in ra STDERR:
  ERROR: [thông báo lỗi]


HƯỚNG DẪN TÍCH HỢP C#
----------------------
Sử dụng Pattern RunCommand (Đã có sẵn trong MainForm.cs)

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

