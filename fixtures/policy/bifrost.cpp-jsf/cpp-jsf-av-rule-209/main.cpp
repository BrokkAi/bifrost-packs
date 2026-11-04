#include "helper.h"

int uses_basic_types(int int_value, short short_value, long long_value,
                    float float_value, double double_value) {
  return int_value + short_value + static_cast<int>(long_value) +
         static_cast<int>(float_value) + static_cast<int>(double_value);
}

Count uses_custom_type(Count value) {
  return value;
}
