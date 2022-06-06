from os import chdir
import pandas as pd
import matplotlib.pyplot as plt
from textwrap import wrap
from matplotlib.ticker import FormatStrFormatter

chdir('C:/Users/sschae/Documents')
datasets = { 'en': pd.read_csv('results-survey729411_wQCode.csv'),
             'fr': pd.read_csv('results-survey213591_wQCode.csv') }

skip = [ '[comment]', ' which ', ' address', ' please ', 'specify',
         ' what ', ' your ', ' name', ' feel ', '[other]',
         ' quel', 'nom ', 'courriel', 'veuillez', 'vous ', 'vous,' ]

resp = dict()
label = dict()
total = 0
scale = set([ x for x in range(1, 6) ] + [ None ])
for lang in datasets:
    resp[lang] = dict()
    label[lang] = dict()
    data = datasets[lang]
    for question in data:
        values = data[question]
        total = max(total, len(values))
        levels = set([ int(x) if str(x).isdigit() else None
                       for x in values.unique() ])
        if levels.issubset(scale):
            if 'Q' in question:
                omit = False
                for s in skip:
                    if s in question.lower():
                        omit = True
                        break
                if not omit:
                    f = question.split('.')
                    l = f[0][:3]
                    if len(l) > 0:
                        label[lang][l] = f[1].lstrip()
                        resp[lang][l] = values

def fit(long):
    return '\n'.join(wrap(long, width = 40))

adj = 4
r = ['Responded', 'Did not respond']
xl = [ x for x in range(1, 6) ]
yl = [ y for y in range(0, total // adj, 2) ]
resp['both'] = dict()
for l in set(label['en']) & set(label['fr']):
    fig, axes = plt.subplots(nrows = 2, ncols = 3, figsize = (20, 10))
    resp['both'][l] = pd.concat([ resp['en'][l], resp['fr'][l]])
    column = 0
    save = False
    for variant in resp:
        d = resp[variant][l]
        no = d.isna().sum()
        answers = len(d)
        yes = answers - no
        if yes > 0:
            # plots (pie and bar)
            axes[1, column].pie([yes, no], labels = r, autopct = '%.0f%%', startangle = 90)
            counts = d.value_counts().to_dict()
            axes[0, column].bar(xl, [ counts.get(x, 0.01) for x in xl ], width = 0.8)
            # proportions
            axes[1, column].axis('equal')
            axes[0, column].axis('auto')
            # ticks and ranges for the bar chart
            axes[0, column].set_xticks(xl)
            axes[0, column].set_yticks(yl)
            axes[0, column].xaxis.set_major_formatter(FormatStrFormatter('%.0f'))
            axes[0, column].yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
            axes[0, column].set_xlim(0.5, 5.5)
            axes[0, column].set_ylim(0, total // adj)
            # titles
            axes[1, column].set_title(f'Response rate ({variant})')
            axes[0, column].set_title(fit(label[variant][l]) if variant in label else 'Combined (1 = close, 5 = far)')
            save = True
        else:
            axes[0, column].axis('off')
            axes[0, column].axis('off')
            axes[1, column].axis('off')
            axes[1, column].axis('off')
        column += 1
    if save:
        fig.suptitle(l)
        plt.savefig(l + '.png')
    plt.close()
