using System;
using System.Data;

namespace Verify.DataSetReadXml.Incomplete
{
    public sealed class VarLocal
    {
        public void Run()
        {
            var orders = new DataSet();
            orders.ReadXml(Environment.GetEnvironmentVariable("BIFROST_IMPORT"));
        }
    }
}
