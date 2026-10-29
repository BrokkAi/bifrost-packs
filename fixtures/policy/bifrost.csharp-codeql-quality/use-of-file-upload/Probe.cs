using System.IO;
using System.Web;
using System.Web.UI.HtmlControls;

public class FileUploadProbe
{
    public void BadSave(HtmlInputFile upload, string directory)
    {
        HttpPostedFile posted = upload.PostedFile;
        posted.SaveAs(Path.Combine(directory, posted.FileName));
    }

    public int BadChained(HtmlInputFile upload)
    {
        return upload.PostedFile.ContentLength;
    }

    public HttpPostedFile BadCast(object control)
    {
        return ((HtmlInputFile)control).PostedFile;
    }

    public HttpPostedFile BadQualified(System.Web.UI.HtmlControls.HtmlInputFile upload)
    {
        return upload.PostedFile;
    }

    public string NearMissAccept(HtmlInputFile upload)
    {
        return upload.Accept;
    }

    public string NearMissFileName(HttpPostedFile posted)
    {
        return posted.FileName;
    }

    public string NearMissHiddenValue(HtmlInputHidden hidden)
    {
        return hidden.Value;
    }
}
