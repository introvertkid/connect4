# setup.py (Nằm trong thư mục 'sever')
from setuptools import setup, Extension
from Cython.Build import cythonize
import os

# Danh sách các file .pyx cần biên dịch (đường dẫn tương đối từ setup.py này)
pyx_files = [
    # "Solver.pyx",
    "Position.pyx",
    # "MoveSorter.pyx",          # <--- Thêm dòng này
    # "TranspositionTable.pyx", # <--- Thêm dòng này
    # Thêm các file .pyx khác nếu có
]

# Phần còn lại giữ nguyên cấu trúc lặp qua pyx_files của bạn
extensions = [
    Extension(
        # Tên module sẽ là tên file .pyx không có đuôi
        name=os.path.splitext(pyx_file)[0],
        sources=[pyx_file]
        # Thêm các tùy chọn biên dịch C nếu cần
        # extra_compile_args=["-O3", "-march=native"]
    )
    for pyx_file in pyx_files
]

setup(
    ext_modules=cythonize(
        extensions,
        compiler_directives={
            'language_level': "3",
            'boundscheck': False,  # Giữ nguyên các chỉ thị tối ưu
            'wraparound': False,
            'cdivision': True,
            'initializedcheck': False
            }
    )
)