// Source: github/codeql/csharp/ql/src/Input Validation/UseOfFileUpload.cs at ae741615f3e178ce61289a651790dc67fcc18e19
// MIT License, Copyright GitHub, Inc.
using System;
using System.Web.UI.HtmlControls;

namespace UseOfFileUpload
{
    class Main
    {

        public void Foo()
        {
            HtmlInputFile FileUpload = new HtmlInputFile();
            HttpPostedFile posted = FileUpload.PostedFile; // BAD
        }

    }

}
