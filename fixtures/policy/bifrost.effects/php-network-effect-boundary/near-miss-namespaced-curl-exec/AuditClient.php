<?php
namespace App;

function deliver(string $orderId): string
{
    return curl_exec('order=' . $orderId);
}
