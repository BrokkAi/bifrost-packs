using System.IO;

public class PathProbe
{
    public string BadThree(string root, string folder, string file)
    {
        return Path.Combine(root, folder, file);
    }

    public string BadTwo(string root, string file)
    {
        return Path.Combine(root, file);
    }

    public string NearMissJoin(string root, string file)
    {
        return Path.Join(root, file);
    }

    public string NearMissOtherCombine(string root, string file)
    {
        return Local.Paths.Combine(root, file);
    }
}
