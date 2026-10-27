"""C# staging contracts, using authored sources and an optional real SDK."""
import json
import os
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from scripts.upstream.codeql_gate.stagers.csharp import CSharpStager, GateError, csharp_comments


class CSharpStagerTests(unittest.TestCase):
    def fixture(self, root):
        codeql = root / 'codeql'
        test = codeql / 'csharp/ql/test/query-tests/With Spaces'
        stubs = codeql / 'csharp/ql/test/resources/stubs'
        test.mkdir(parents=True)
        stubs.mkdir(parents=True)
        return codeql, test, stubs

    def test_options_map_tokens_before_expanding_testdir_with_spaces(self):
        with tempfile.TemporaryDirectory() as temporary:
            codeql, test, stubs = self.fixture(Path(temporary))
            for name in ('_frameworks/Microsoft.NETCore.App/Microsoft.NETCore.App.csproj',
                         '_frameworks/Microsoft.AspNetCore.App/Microsoft.AspNetCore.App.csproj',
                         'Example.Package/1.2.3/Example.Package.csproj', 'Legacy.cs'):
                path = stubs / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('authored stub')
            test.joinpath('options').write_text(
                'ignored-line: unused\n'
                'semmle-extractor-options: /nostdlib /noconfig --standalone /r:System.Runtime.dll\n'
                'semmle-extractor-options: --load-sources-from-project:${testdir}/../../resources/stubs/_frameworks/Microsoft.NETCore.App/Microsoft.NETCore.App.csproj\n'
                'semmle-extractor-options: --load-sources-from-project:../../resources/stubs/_frameworks/Microsoft.AspNetCore.App/Microsoft.AspNetCore.App.csproj\n'
                'semmle-extractor-options: --load-sources-from-project:${testdir}/../../resources/stubs/Example.Package/1.2.3/Example.Package.csproj\n'
                'semmle-extractor-options: ../../resources/stubs/Legacy.cs\n')
            tokens, artifacts = CSharpStager._options(test, codeql)
            self.assertEqual(len(tokens), 8)
            self.assertEqual([a['kind'] for a in artifacts],
                             ['flag', 'flag', 'flag', 'reference', 'framework', 'framework', 'package', 'stub-package'])
            self.assertEqual(artifacts[6]['id'], 'Example.Package')
            self.assertEqual(artifacts[6]['version'], '1.2.3')
            self.assertEqual(artifacts[7]['stub_path'], stubs / 'Legacy.cs')
            test.joinpath('options').write_text('semmle-extractor-options: --unknown\n')
            with self.assertRaisesRegex(GateError, '--unknown'):
                CSharpStager._options(test, codeql)

    def test_project_and_external_nuget_configuration(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            staged = root / 'prepared'
            staged.mkdir()
            references = [dict(kind=kind, id=name, version=version, status=status)
                          for kind, name, version, status in (
                              ('framework', 'Microsoft.NETCore.App', None, 'restored'),
                              ('framework', 'Microsoft.AspNetCore.App', None, 'restored'),
                              ('package', 'Example', '2.3.4', 'restored'),
                              ('package', 'Example', '2.3.4', 'restored'),
                              ('stub-package', 'CodeQL.Stub.Failed', '0.0.0-sha.abc', 'compile_failed'))]
            CSharpStager._project(staged / 'CodeQLTest.csproj', references)
            p = ET.parse(staged / 'CodeQLTest.csproj').getroot()
            self.assertEqual(p.get('Sdk'), 'Microsoft.NET.Sdk')
            self.assertEqual(p.findtext('PropertyGroup/TargetFramework'), 'net10.0')
            self.assertEqual(p.findtext('PropertyGroup/AllowUnsafeBlocks'), 'true')
            self.assertEqual(p.findtext('PropertyGroup/ImplicitUsings'), 'disable')
            self.assertEqual([n.attrib for n in p.iter('PackageReference')], [{'Include': 'Example', 'Version': '[2.3.4]'}])
            self.assertEqual([n.get('Include') for n in p.iter('FrameworkReference')], ['Microsoft.AspNetCore.App'])
            stager = CSharpStager(None, root / 'packages', 'https://packages.example/index.json')
            config = root / 'NuGet.Config'
            stager._config(config, root / 'feed')
            sources = ET.parse(config).getroot().find('packageSources')
            self.assertEqual([n.tag for n in sources], ['clear', 'add', 'add'])
            self.assertEqual(sources[1].get('value'), str(root / 'feed'))
            self.assertEqual(sources[2].get('value'), 'https://packages.example/index.json')
            self.assertFalse(any(staged.glob('*.config')))
            with self.assertRaisesRegex(GateError, 'net10.0'):
                stager._sdk(root / 'cache')

    def test_csharp_literal_and_interpolation_boundaries(self):
        # Each fake tag is literal content, including strings inside nested holes.
        lines = [
            'var a = "// $ Alert";',
            r'var b = "escaped \\\" // $ Alert";',
            'var c = @"quoted "" // $ Alert";',
            'var d = $"literal // $ Alert {F("// $ Alert")}";',
            'var e = $@"literal // $ Alert {F(@"// $ Alert")}";',
            'var f = @$"literal // $ Alert {F($"nested {F("// $ Alert")}")}";',
            'var g = """raw // $ Alert""";',
            'var h = """"raw """ // $ Alert"""";',
            'var i = $"""raw // $ Alert {F("// $ Alert")}""";',
            'var j = $$"""raw {literal} // $ Alert {{F("// $ Alert")}}""";',
            "var k = '\\''; var l = '/'; // $ Alert[cs/other]",
            '/// $ Alert',
            '/* $ Alert */',
            '// prose $ Alert',
            '// $ Alert[cs/example]',
            '// $ MISSING: Alert[cs/example]',
            '// $ SPURIOUS: Alert[cs/example]',
            '// $ Source Sink RelatedLocation',
        ]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'Literals.cs').write_text('\n'.join(lines))
            oracle = CSharpStager(None, root / 'packages', '').inline_oracle(root, 'cs/example')
            self.assertEqual([r['start'] for r in oracle['inline_alert']], [15])
            self.assertEqual([r['start'] for r in oracle['missing']], [16])
            self.assertEqual([r['start'] for r in oracle['spurious']], [17])
            self.assertEqual(len(list(csharp_comments('var v = $"{F("x")} // literal"; // $ Alert'))), 1)

    def test_xml_asp_and_razor_comment_kinds(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            files = {
                'Web.config': '<configuration>\n<!-- $ Alert[cs/example] -->\n<![CDATA[<!-- $ Alert -->]]>\n</configuration>',
                'Data.xml': '<r a="&lt;!-- $ Alert --&gt;">\n<!-- $ Alert[cs/other] -->\n</r>',
                'Page.aspx': '<div title="<%-- $ Alert --%>">\n<%-- $ Alert[cs/example] --%>\n<!-- $ MISSING: Alert -->\n<% var s = "<!-- $ Alert -->"; %>\n</div>',
                'View.cshtml': '<!-- $ Alert -->\n@* $ Alert *@\n<p>// $ Alert</p>\n@{ var s = "// $ Alert"; // $ Alert[cs/example]\n}\n',
                'Notes.txt': '<!-- $ Alert -->\n// $ Alert',
            }
            for name, content in files.items():
                (root / name).write_text(content)
            oracle = CSharpStager(None, root / 'packages', '').inline_oracle(root, 'cs/example')
            self.assertEqual([(r['path'], r['start']) for r in oracle['inline_alert']],
                             [('Page.aspx', 2), ('View.cshtml', 4), ('Web.config', 2)])
            self.assertEqual([(r['path'], r['start']) for r in oracle['missing']], [('Page.aspx', 3)])

    @unittest.skipUnless(os.environ.get('CODEQL_GATE_DOTNET_ROOT'), 'requires CODEQL_GATE_DOTNET_ROOT with a net10.0 SDK')
    def test_real_prepare_restore_stub_package_and_cache(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            codeql, test, stubs = self.fixture(base)
            (stubs / 'ExampleApi.cs').write_text('namespace Probe { public class ExampleApi { public void Run() {} } }\n')
            (test / 'Main.cs').write_text('class MainClass { void Run(Probe.ExampleApi api) { api.Run(); } }\n')
            (test / 'Main.expected').write_text('excluded')
            (test / '.gitignore').write_text('authored-output/')
            (test / 'options').write_text('semmle-extractor-options: /nostdlib /r:System.Runtime.dll /r:DoesNotExist.dll ../../resources/stubs/ExampleApi.cs\n')
            stager = CSharpStager(os.environ['CODEQL_GATE_DOTNET_ROOT'], base / 'packages',
                                  'https://api.nuget.org/v3/index.json')
            first = stager.prepare(test, codeql, base / 'cache')
            again = stager.prepare(test, codeql, base / 'cache')
            self.assertEqual(first, again)
            self.assertEqual(first.source_paths, ('Main.cs',))
            self.assertFalse((first.root / 'Main.expected').exists())
            self.assertFalse(any(first.root.rglob('ExampleApi.cs')))
            self.assertFalse((first.root / 'NuGet.Config').exists())
            self.assertEqual((first.root / '.gitignore').read_text(), 'authored-output/\nbin/\nobj/\n')
            self.assertTrue((first.root / 'obj/project.assets.json').is_file())
            artifacts = {a['id']: a for a in first.staged_artifacts}
            self.assertEqual(artifacts['System.Runtime.dll']['status'], 'found')
            self.assertEqual(artifacts['DoesNotExist.dll']['status'], 'not_found')
            stub = artifacts['CodeQL.Stub.ExampleApi']
            self.assertEqual(stub['status'], 'restored')
            self.assertTrue(stub['sha512'])
            self.assertTrue(stub['version'].startswith('0.0.0-sha.'))
            assets = json.loads((first.root / 'obj/project.assets.json').read_text())
            self.assertEqual(assets['libraries']['CodeQL.Stub.ExampleApi/' + stub['version']]['sha512'], stub['sha512'])
            (stubs / 'ExampleApi.cs').write_text('invalid source with a syntax error')
            broken = stager.prepare(test, codeql, base / 'cache')
            self.assertNotEqual(first.root, broken.root)
            failed = next(a for a in broken.staged_artifacts if a['kind'] == 'stub-package')
            self.assertEqual(failed['status'], 'compile_failed')
            self.assertTrue(Path(failed['compile_log']).is_file())
            self.assertFalse(ET.parse(broken.root / 'CodeQLTest.csproj').getroot().findall('.//PackageReference'))


if __name__ == '__main__':
    unittest.main()
