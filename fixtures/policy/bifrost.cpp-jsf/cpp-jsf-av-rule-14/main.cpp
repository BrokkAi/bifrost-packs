#include "helpers.h"

unsigned int lower_u = 1u;
unsigned long lower_ul = 2ul;
unsigned int upper_u = 3U;
unsigned long upper_ul = 4UL;
int no_suffix = 5;

int main() {
  return lower_u + lower_ul + upper_u + upper_ul + no_suffix;
}
