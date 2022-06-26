import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation, writers


INTERVAL = 44  # ms
FPS = int(1000/44)


def animate(file_path, filter_volt=5, frames=None):
    data = []
    with open(file_path, "r") as f:
        for l in f.readlines():
            d = []
            for x in l.split(","):
                x = float(x)
                if x > filter_volt:
                    x = 0
                d.append(x)
            d = np.array(d)
            d.resize(16, 16)
            data.append(d)

    def animation_function(i):
        plt.clf()
        plt.imshow(data[i], vmin=0, vmax=3.3)
        plt.colorbar()

    if frames is None:
        frames = len(data)

    fig = plt.figure(figsize=(7, 5))
    anim = FuncAnimation(fig, animation_function,
                         frames=frames, interval=INTERVAL)

    writervideo = animation.FFMpegWriter(fps=FPS)
    anim.save('pressure.mp4', writer=writervideo)
    plt.close()


if __name__ == "__main__":
    # data_file = "/Users/andy/Coding/jupyter-notebooks/adc-debug/data/exp3/data_log.txt"
    # animate(data_file, 3, 1000)

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--data_log", default="./data_log.txt")
    parser.add_argument("--frames", type=int)
    parser.add_argument("--filter", default=3)

    args = parser.parse_args()

    animate(args.data_log, args.filter, args.frames)
