using System;

public class GcProbe
{
    public void Bad()
    {
        GC.Collect();
    }

    public void NearMissGeneration()
    {
        GC.Collect(0);
    }

    public void NearMissOtherCollector(Local.Collector collector)
    {
        collector.Collect();
        Local.GC.Collect();
    }
}
