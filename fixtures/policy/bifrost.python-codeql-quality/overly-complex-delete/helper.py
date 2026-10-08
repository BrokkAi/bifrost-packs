class Complex:
    def __del__(self):
        if self.ready:
            print(1)
        if self.closed:
            print(2)
        for value in range(2):
            print(value)


class Simple:
    def __del__(self):
        self.close()

    def close(self):
        pass
