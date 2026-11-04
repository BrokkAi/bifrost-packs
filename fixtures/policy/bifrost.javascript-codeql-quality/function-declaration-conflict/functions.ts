export function moduleFunction(flag: boolean) {
  if (flag) {
    function helper(): number { return 1; }
  } else {
    function helper(): number { return 2; }
  }
  return helper();
}

function moduleDuplicate() {}
function moduleDuplicate() {}
