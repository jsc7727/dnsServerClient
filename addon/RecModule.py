class file:
    def __init__(self, path, option):
        self.f = open(path, option)

    def write(self, message):
        return self.f.write(message)

    def read(self):
        return self.f.read().split()


if __name__ == '__main__':
    rec1 = file("test.txt", 'a+')
    rec1.write("test")
    rec1.write("test")
    rec1.write("test")
    rec1.write("test")
