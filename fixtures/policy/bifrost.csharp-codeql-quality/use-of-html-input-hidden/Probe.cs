using System;
using System.Web.UI.HtmlControls;

public class HiddenFieldProbe
{
    private HtmlInputHidden declaredOnly;

    public HtmlInputHidden BadInitializer(string token)
    {
        return new HtmlInputHidden { ID = "csrf", Value = token };
    }

    public object BadQualified()
    {
        return new System.Web.UI.HtmlControls.HtmlInputHidden();
    }

    public HtmlInputHidden BadKept()
    {
        var field = new HtmlInputHidden();
        field.Value = "state";
        return field;
    }

    public HtmlInputHidden KnownMissTargetTyped()
    {
        HtmlInputHidden field = new();
        return field;
    }

    public string NearMissExisting(HtmlInputHidden existing)
    {
        return existing.Value;
    }

    public Type NearMissTypeOf()
    {
        return typeof(HtmlInputHidden);
    }

    public HtmlInputHidden NearMissSubclass()
    {
        return new AuditedHiddenField();
    }
}

public class AuditedHiddenField : HtmlInputHidden
{
    public AuditedHiddenField() : base() { }
}
