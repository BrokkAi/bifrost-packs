"""Reserved for the Java gate owner: toolchains and coordinate data live here."""


class JavaStager:
    def prepare(self, test_dir, codeql_root, cache_dir):
        raise NotImplementedError('Java staging has not been ported yet')

    def run_env(self, run_dir, prepared):
        raise NotImplementedError('Java staging has not been ported yet')

    def extra_policy_files(self, prepared):
        raise NotImplementedError('Java staging has not been ported yet')
