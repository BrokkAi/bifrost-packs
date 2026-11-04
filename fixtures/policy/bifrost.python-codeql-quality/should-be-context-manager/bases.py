class Resource:
    def __del__(self):
        self.close()

    def close(self):
        pass

class SafeResource:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def close(self):
        pass

class PartialResource:
    def __enter__(self):
        return self

    def __del__(self):
        self.close()

    def close(self):
        pass
