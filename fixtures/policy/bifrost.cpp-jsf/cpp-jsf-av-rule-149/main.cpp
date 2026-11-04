#include <cstdint>

int main() {
  int nonzero_octal = 0123;
  unsigned long suffixed_octal = 0123u;
  int zero = 00;
  int decimal = 123;
  int hexadecimal = 0x123;
  return nonzero_octal + suffixed_octal + zero + decimal + hexadecimal;
}
