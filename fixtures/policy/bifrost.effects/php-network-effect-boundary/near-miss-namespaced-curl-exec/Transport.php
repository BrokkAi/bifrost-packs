<?php
// Near miss: a userland `curl_exec` in the caller's own namespace. PHP's
// function lookup tries `App\curl_exec` before the global builtin, so the
// call in AuditClient.php resolves to this analyzed body, which performs no
// I/O. The reviewed identity must not bind by spelling.
namespace App;

function curl_exec(string $payload): string
{
    return 'queued:' . $payload;
}
