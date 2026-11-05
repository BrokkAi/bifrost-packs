using System;
using System.Data;

namespace Verify.DataSetReadXml
{
    public sealed class Probe
    {
        public void DataSetParameter(DataSet orders)
        {
            orders.ReadXml(Environment.GetEnvironmentVariable("BIFROST_IMPORT"));
        }

        public void DataSetTypedLocal()
        {
            DataSet orders = new DataSet();
            orders.ReadXml(Console.ReadLine(), XmlReadMode.ReadSchema);
        }

        public void DataTableParameter(DataTable table)
        {
            table.ReadXml(Console.ReadLine());
        }

        // Near misses: no finding expected below this line.
        public void ConstantResource(DataSet orders)
        {
            orders.ReadXml("seed-data.xml");
        }

        public void ExportToExternalPath(DataSet orders)
        {
            orders.WriteXml(Environment.GetEnvironmentVariable("BIFROST_EXPORT"));
        }

        public void LocalLookalike(Local.DataSet orders)
        {
            orders.ReadXml(Console.ReadLine());
        }
    }
}

namespace Local
{
    public sealed class DataSet
    {
        public void ReadXml(string fileName) { }
    }
}
