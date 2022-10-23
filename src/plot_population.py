from matplotlib import pyplot as plt
import pandas as pd
from tkinter import filedialog, Tk
import os

def ask_for_file():
    global path
    root = Tk()
    root.withdraw()
    path = filedialog.askopenfilename(title='Open .csv', initialdir='.')


try:
    all_subdirs = os.listdir(f'{os.getcwd()}\populations')
    for i, _ in enumerate(all_subdirs):
        all_subdirs[i] = f'{os.getcwd()}\populations\{all_subdirs[i]}'
    latest_subdir = max(all_subdirs, key=os.path.getmtime)
    path = f'{latest_subdir}\generations_data.csv'
except:
    ask_for_file()

fig, (time_plot, score_plot) = plt.subplots(2)
fig.canvas.manager.toolbar._Button("PREVIOUS", "zoom_to_rect_large.png", ask_for_file, command=ask_for_file)
time_plot.set_title('Time [s] per generation')
score_plot.set_title('Highest score per generation')
fig.tight_layout()
while True:
    data = pd.read_csv(path, delimiter=';')
    time = data.iloc[:, 1].values
    score = data.iloc[:, 2].values
    print(time)

    time_plot.plot(time)
    score_plot.plot(score)
    plt.pause(10)

plt.show()