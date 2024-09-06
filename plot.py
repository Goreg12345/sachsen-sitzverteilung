import matplotlib.pyplot as plt
import pandas as pd

colors = {
    'CDU': '#000000',
    'AfD': '#0096D6',
    'BSW': '#FF8C00',
    'SPD': '#E3000F',
    'GRÜNE': '#64A12D',
    'DIE LINKE': '#C8102E',
    'FW': '#FFD700',
}


df = pd.read_csv('Ergebnis.csv')
df['partei'] = df['partei'].replace('FREIE WÄHLER', 'FW')
df = df[df.mandate > 0]

plt.style.use('ggplot')
plt.bar(df.partei, df.mandate, color=[colors[partei] for partei in df.partei])
# add the number of mandates on top of the bars
for i, v in enumerate(df.mandate):
    plt.text(i, v + 1, str(v), ha='center', va='bottom')
plt.title('Vorläufige Sitzplatzverteilung Landtagswahl Sachsen 2024')
plt.ylabel('Mandate')
plt.savefig('mandates.png')