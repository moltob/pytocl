from pytocl.speedlist import SpeedList

def test_1():
    speedlist = SpeedList()
    speedlist.add(0, 0)
    speedlist.add(10, 10)
    speedlist.add(20, 20)
    speedlist.add(30, 30)
    speedlist.add(40, 40)
    speedlist.add(50, 50)
    print(speedlist.getSpeedForDistance(30))
    print(speedlist.getSpeedForDistance(35))
    print(speedlist.getSpeedForDistance(45))
    print(speedlist.getSpeedForDistance(60))
    #speedlist.printAll()

if __name__ == '__main__':
    test_1()