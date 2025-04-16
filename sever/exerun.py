import subprocess
import os
import sys

# Lấy đường dẫn đến thư mục chứa file script này (exerun.py)
script_dir = os.path.dirname(os.path.abspath(__file__))

# Tạo đường dẫn đầy đủ đến file .exe
exe_name = "c4solver.exe"
exe_path = os.path.join(script_dir, exe_name)

print(f"Thư mục script: {script_dir}")
print(f"Đường dẫn file thực thi: {exe_path}")

# Kiểm tra xem file .exe có thực sự tồn tại không
if not os.path.exists(exe_path):
    print(f"LỖI: Không tìm thấy file thực thi tại đường dẫn: {exe_path}")
    sys.exit(1) # Thoát script với mã lỗi

try:
    # Chuẩn bị lệnh để chạy.
    # Nếu c4solver.exe cần tham số dòng lệnh, thêm vào đây.
    # Ví dụ: command = [exe_path, "--interactive"]
    command = [exe_path]

    print(f"\nĐang khởi chạy: {' '.join(command)}")
    print("Chương trình C++ sẽ chạy ngay trong cửa sổ này.")
    print("Bạn có thể nhập trực tiếp vào đây khi chương trình yêu cầu.")
    print("-" * 30) # Dòng phân cách để rõ ràng

    # Sử dụng subprocess.Popen thay vì subprocess.run
    # KHÔNG sử dụng các tham số: capture_output, input, text, stdout, stderr, stdin
    # Để mặc định (None), Popen sẽ cho phép chương trình con kế thừa
    # stdin, stdout, stderr từ Python, kết nối nó trực tiếp với console.
    process = subprocess.Popen(command, cwd=script_dir) # Chỉ định thư mục làm việc nếu cần

    # Đợi cho đến khi chương trình C++ kết thúc
    # .wait() sẽ chặn script Python tại đây cho đến khi c4solver.exe thoát
    return_code = process.wait()

    # Sau khi chương trình C++ kết thúc
    print("-" * 30) # Dòng phân cách
    if return_code == 0:
        print(f"Chương trình C++ đã kết thúc thành công (Mã trả về: {return_code}).")
    else:
        # Lưu ý: Đây là mã lỗi do chương trình C++ trả về,
        # không phải lỗi khi chạy Popen (trừ khi có exception bên dưới)
        print(f"LƯU Ý: Chương trình C++ đã kết thúc với mã lỗi: {return_code}.")
        print("(Kiểm tra output của chương trình C++ ở trên để biết chi tiết lỗi nếu có)")

except FileNotFoundError:
    # Lỗi này xảy ra nếu Popen không tìm thấy file exe ngay từ đầu
    print(f"LỖI: Không thể khởi chạy. Không tìm thấy file thực thi tại: {exe_path}")
except PermissionError:
     print(f"LỖI: Không có quyền thực thi file: {exe_path}")
except Exception as e:
    # Bắt các lỗi không mong muốn khác khi cố gắng khởi chạy Popen
    print(f"\n--- LỖI KHÔNG MONG MUỐN KHI KHỞI CHẠY ---")
    print(f"Loại lỗi: {type(e).__name__}")
    print(f"Chi tiết: {e}")