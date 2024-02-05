import matplotlib.pyplot as plt
import matplotlib.animation as animation
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
from scipy import stats
import multiprocessing
import pandas as pd
import datetime
import time

SPI_PORT = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
x_len = 150
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
xs = list(range(0, x_len))
ys = [0] * x_len
ax.set_ylim(-5, 5)
ecg = []
timeecg = []
line, = ax.plot(xs, ys)
threshold = 2047.5
last_beat_time = 0

def moving_average(values, window):
    if window < 1:
        raise ValueError("Window size must be at least 1.")

    filtered = []

    for i in range(len(values)):
        if i < window - 1:
            window_vals = values[0:i + 1]
        else:
            window_vals = values[i - window + 1 : i + 1]
        avg = sum(window_vals) / len(window_vals)
        filtered.append(avg)

    return filtered

def calculate_bpm_ibm():
    global last_beat_time

    current_time = time.time() * 1000
    beat_interval = current_time - last_beat_time
    last_beat_time = current_time

    beats_per_minute = 60000.0 / beat_interval
    print(f"BPM: {beats_per_minute:.2f}")
    print(f"IBM: {beat_interval:.2f} ms")

def animate(i, ys):
    value = mcp.read_adc(0)
    ys.append(value)
    ys = ys[-x_len:]
    y_ = stats.zscore(ys)
    y = moving_average(y_, 2)
    y = y[-x_len:]
    ecg.append(y[x_len - 1])
    timeecg.append(datetime.datetime.now())

    line.set_ydata(y)

    if i % 60 == 0:
        calculate_bpm_ibm()

    return line,

def loop():
    ani = animation.FuncAnimation(
        fig, animate, fargs=(ys,), interval=3, blit=True
    )
    plt.show()

if __name__ == '__main__':
    p1 = multiprocessing.Process(target=loop)
    p1.start()
    p1.join()
