<?php
// The selected boundary after the fix. Every callee below it is analyzed
// workspace code, so the clean verdict rests on exhaustive coverage.
namespace App;

function total(array $order): int
{
    return sum_lines($order['lines']);
}
