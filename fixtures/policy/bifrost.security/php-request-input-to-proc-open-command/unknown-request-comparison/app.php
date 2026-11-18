<?php
// The request value only selects whether a constant command runs. On Bifrost
// 0.15.3 the comparison leaves the procedure semantics unknown, so the run is
// inconclusive rather than a clean near miss.
function convertImage(): mixed
{
    $pipes = [];
    $mode = $_GET['mode'];
    if ($mode === 'thumbnail') {
        return proc_open(['convert', 'in.png', 'out.png'], [], $pipes);
    }
    return null;
}
