<?php
// The selected pure-calculation boundary.
//
// `total` is the exact declaration the reviewed policy configuration selects.
// It reaches the network only through workspace helpers: `record` in
// AuditService.php, then `deliver` in AuditClient.php, then the global
// `curl_exec` builtin the reviewed model declares a network effect on.
namespace App;

function total(array $order): int
{
    record($order);
    return sum_lines($order['lines']);
}
