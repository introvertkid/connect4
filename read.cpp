#include <iostream>
#include <fstream>
#include <iomanip>
#include <cctype>
#include <sstream>

void readBookFile(const std::string& path) {
     std::ifstream file(path, std::ios::binary);
     if (!file) {
         std::cerr << "Không thể mở file: " << path << std::endl;
         return;
     }

     std::string data((std::istreambuf_iterator<char>(file)),
                       std::istreambuf_iterator<char>());

     std::cout << "Total bytes: " << data.size() << std::endl;

     for (size_t i = 0; i < 1000; i += 16) {
         std::cout << std::setw(8) << std::setfill('0') << std::hex << i << "  ";

         std::ostringstream hexPart;
         std::string asciiPart;

         for (size_t j = 0; j < 16; ++j) {
             if (i + j < data.size()) {
                 unsigned char byte = static_cast<unsigned char>(data[i + j]);
                 if (j == 8) hexPart <<" ";
                 hexPart << std::setw(2) << std::setfill('0') << std::hex << static_cast<int>(byte) << " ";
                 asciiPart += (std::isprint(byte) ? static_cast<char>(byte) : '.');
             } else {
                 hexPart << "   ";
                 if (j == 8) hexPart << " ";
             }
         }

         std::cout << std::left << std::setw(47) << hexPart.str() << " " << asciiPart << std::endl;
     }
 }

 int main() {
     readBookFile("NegamaxSolver/7x6.book");
     return 0;
 }
