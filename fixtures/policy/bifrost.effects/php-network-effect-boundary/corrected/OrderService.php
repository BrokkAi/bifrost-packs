<?php
// Corrected placement: the caller owns the audit transfer and runs it after
// the pure calculation, so the selected boundary reaches only `sum_lines`.
namespace App;

function record(array $order): int
{
    $priced = total($order);
    deliver($order['id']);
    return $priced;
}
