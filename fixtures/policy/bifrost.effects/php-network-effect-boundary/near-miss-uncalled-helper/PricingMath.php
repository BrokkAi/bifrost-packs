<?php
// The pure calculation `total` keeps on its own path. Its whole reachable call
// graph is analyzed, so the boundary's clean verdict is provable rather than
// merely unseen. The loop is written out instead of calling an unmodeled
// builtin such as `array_sum`, so no open callee leaks into the effect set.
namespace App;

function sum_lines(array $lines): int
{
    $total = 0;
    foreach ($lines as $line) {
        $total += $line['amount'];
    }
    return $total;
}
