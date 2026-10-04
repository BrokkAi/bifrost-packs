#include "helpers.h"

const wchar_t *wide_text = L"bad";
const char *plain_text = "good";

int main() {
  wchar_t wide_char = L'x';
  char plain_char = 'x';
  use_char(plain_char);
  use_wide(wide_char);
  return 0;
}
