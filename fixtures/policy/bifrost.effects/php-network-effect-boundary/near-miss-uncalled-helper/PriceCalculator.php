<?php
// Near miss: the workspace still contains `deliver`, which reaches the real
// `curl_exec`, but nothing the selected boundary calls reaches it. The
// boundary's effect closure follows calls, not files or declarations that
// merely exist.
namespace App;

function total(array $order): int
{
    return sum_lines($order['lines']);
}
