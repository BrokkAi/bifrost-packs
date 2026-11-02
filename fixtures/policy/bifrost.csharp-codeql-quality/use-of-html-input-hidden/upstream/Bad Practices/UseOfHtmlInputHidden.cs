// Source: github/codeql/csharp/ql/src/Bad Practices/UseOfHtmlInputHidden.cs at ae741615f3e178ce61289a651790dc67fcc18e19
// MIT License, Copyright GitHub, Inc.
using System;
using System.Web.UI.HtmlControls;

namespace UseOfHtmlInputHidden
{
    class Main
    {

        public void Foo()
        {
            HtmlInputHidden field = new HtmlInputHidden(); // BAD
        }

    }

}
