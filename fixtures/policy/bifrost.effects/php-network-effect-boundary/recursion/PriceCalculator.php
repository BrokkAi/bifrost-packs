<?php
// Recursion termination: the boundary reaches the effect through a recursive
// helper, so the effect walk has to reach a fixpoint and report it once.
namespace App;

function total(array $order): int
{
    return accumulate($order, 3);
}

function accumulate(array $order, int $remaining): int
{
    if ($remaining <= 0) {
        record($order);
        return 0;
    }
    record($order);
    return accumulate($order, $remaining - 1) + 1;
}
