<?php
// Unresolved helper: `Vendor\Billing\dispatch` has no workspace definition and
// no activated model, so the effect set below the boundary is open and the
// absence claim cannot be certified.
namespace App;

function total(array $order): int
{
    return \Vendor\Billing\dispatch($order);
}
