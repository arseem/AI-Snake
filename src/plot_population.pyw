from matplotlib import pyplot as plt
import pandas as pd
from tkinter import filedialog, Tk
import os

BACK_COLOR = 'black'
FRONT_COLOR = 'white'
SEC_COLOR = 'green'

def ask_for_file():
    global path
    root = Tk()
    root.withdraw()
    path_to_change = filedialog.askopenfilename(title='Open .csv', initialdir='.')
    if path_to_change:
        path = path_to_change


try:
    all_subdirs = os.listdir(f'{os.getcwd()}\populations')
    for i, _ in enumerate(all_subdirs):
        all_subdirs[i] = f'{os.getcwd()}\populations\{all_subdirs[i]}'
    latest_subdir = max(all_subdirs, key=os.path.getmtime)
    path = f'{latest_subdir}\generations_data.csv'
    pd.read_csv(path, delimiter=';')
except:
    ask_for_file()

fig, axes = plt.subplots(2)
fig.patch.set_facecolor('black')
for ax in axes:
    ax.set_facecolor('black')
    ax.spines['bottom'].set_color(FRONT_COLOR)
    ax.spines['top'].set_color(FRONT_COLOR) 
    ax.spines['right'].set_color(FRONT_COLOR)
    ax.spines['left'].set_color(FRONT_COLOR)
    ax.tick_params(axis='x', colors=FRONT_COLOR)
    ax.tick_params(axis='y', colors=FRONT_COLOR)
    ax.yaxis.label.set_color(FRONT_COLOR)
    ax.xaxis.label.set_color(FRONT_COLOR)
    ax.title.set_color(FRONT_COLOR)

(time_plot, score_plot) = axes
fig.canvas.manager.toolbar._Button("PREVIOUS", "zoom_to_rect_large.png", ask_for_file, command=ask_for_file)
time_plot.set_title('Time [s] per generation')
score_plot.set_title('Score per generation')
#avg_score_plot.set_title('Average score per generation')
fig.tight_layout()
plt.ion()
plt.show()

time_temp = []

while plt.fignum_exists(1):
    data = pd.read_csv(path, delimiter=';')
    time = data.iloc[:, 1].values
    score = data.iloc[:, 2].values
    avg_score = data.iloc[:, 3].values

    if len(time)!=len(time_temp):
        for ax in axes:
            ax.clear()
        time_plot.plot(time, color=FRONT_COLOR)
        h, = score_plot.plot(score, color=FRONT_COLOR)
        a, = score_plot.plot(avg_score, color=SEC_COLOR)
        score_plot.legend([h, a], labels=['Highest', 'Average'])

        #avg_score_plot.plot(avg_score)
    
    plt.gcf().canvas.draw_idle()
    plt.gcf().canvas.start_event_loop(1)

    time_temp = time
