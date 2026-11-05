<?php

function src(): string
{
    return "";
}

function sink(mixed $s): void
{
}

function handler(): void
{
    $u = src(); $a = [$u]; sink($a[0]);
}
