#include "helper.h"

struct Operators {
    bool operator&&(const Operators &other) const { return true; }
    bool operator||(const Operators &other) const { return true; }
    Operators *operator&() { return this; }
    Operators operator&(const Operators &other) const { return other; }
};
