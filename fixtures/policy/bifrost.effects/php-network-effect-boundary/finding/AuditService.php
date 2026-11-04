<?php
namespace App;

function record(array $order): void
{
    deliver($order['id']);
}
