from pytocl.speedlist import SpeedList

def test_1():
    speedlist = SpeedList()
    speedlist.add(0, 0)
    speedlist.add(1, 10)
    speedlist.add(2, 20)
    speedlist.add(3, 30)
    speedlist.add(4, 40)
    speedlist.add(5, 50)
    speedlist.printAll()

if __name__ == '__main__':
    test_1()