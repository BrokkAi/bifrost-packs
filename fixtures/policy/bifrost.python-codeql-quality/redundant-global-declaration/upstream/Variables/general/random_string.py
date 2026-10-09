# Source: github/codeql/python/ql/test/query-tests/Variables/general/random_string.py at ae741615f3e178ce61289a651790dc67fcc18e19
# MIT License, Copyright GitHub, Inc.

#ODASA-3688
def generate_random_string(char_sequences, length):
    random_string = ""

    # Two tests of the same variable to force splitting of the flow-graph
    if char_sequences:
        for char_seq in char_sequences:
            pass

    def func_used():
        pass

    #Only use the variable on one of the split arms.
    if char_sequences:
        while len(random_string) < length:
            random_string += func_used()
