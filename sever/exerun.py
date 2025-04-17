import subprocess
import os
import sys

# Lấy đường dẫn đến thư mục chứa file script này (exerun.py)
script_dir = os.path.dirname(os.path.abspath(__file__))

exe_name = "c4solver.exe"
exe_path = os.path.join(script_dir, exe_name)

print(f"Thư mục script: {script_dir}")
print(f"Đường dẫn file thực thi: {exe_path}")

if not os.path.exists(exe_path):
    print(f"LỖI: Không tìm thấy file thực thi tại đường dẫn: {exe_path}")
    sys.exit(1) # Thoát script với mã lỗi

    command = [exe_path]

    print("-" * 30) # Dòng phân cách để rõ ràng

    # Sử dụng subprocess.Popen thay vì subprocess.run
    # KHÔNG sử dụng các tham số: capture_output, input, text, stdout, stderr, stdin
    # Để mặc định (None), Popen sẽ cho phép chương trình con kế thừa
    # stdin, stdout, stderr từ Python, kết nối nó trực tiếp với console.
    process = subprocess.Popen(command, cwd=script_dir) # Chỉ định thư mục làm việc nếu cần

    return_code = process.wait()

    print("-" * 30) # Dòng phân cách
