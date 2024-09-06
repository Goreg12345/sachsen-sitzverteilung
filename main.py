import numpy as np
import pandas as pd


df = pd.read_csv('bereinigt.csv').set_index('partei')
min_mandate = 120

# §6 Abs. 1
# Bei Verteilung der Sitze auf die Landeslisten werden nur Parteien berücksichtigt,
# die mindestens fünf Prozent der abgegebenen gültigen Listenstimmen erhalten
n_stimmen = df['n_listenstimmen'].sum()
df['5%_schwelle'] = False
df.loc[df['n_listenstimmen'] >= n_stimmen * 0.05, '5%_schwelle'] = True
# oder in mindestens zwei Wahlkreisen ein Direktmandat errungen haben.
df.loc[df['n_direkt_mandate'] >= 2, '5%_schwelle'] = True

# §6 Abs. 2
# Von der Gesamtzahl der Abgeordneten (§ 1 Absatz 1) wird die Zahl jener erfolgreichen Wahlkreisbewerberinnen und Wahlkreisbewerber (Direktkandidatinnen und Direktkandidaten) abgezogen, die nicht von einer nach Absatz 1 zu berücksichtigenden Partei vorgeschlagen worden sind.
min_mandate -= df.loc[df['5%_schwelle'] == False, 'n_direkt_mandate'].sum()

# §6 Abs. 3
# Die nach Absatz 2 verbleibenden Sitze werden auf die gemäß Absatz 1 berücksichtigungsfähigen Parteien nach dem Höchstzahlverfahren nach Sainte-Laguë verteilt: es werden die für jede Landesliste einer Partei insgesamt abgegebenen Listenstimmen zusammengezählt und die Gesamtstimmenzahl einer jeden Landesliste nacheinander solange durch 0,5, 1,5, 2,5, 3,5 und so weiter geteilt, bis so viele Höchstzahlen ermittelt sind, wie Sitze zu vergeben sind
df_5_prozent = df.loc[df['5%_schwelle'], 'n_listenstimmen']
hoechstzahlen = pd.concat([df_5_prozent / i for i in np.arange(0.5, min_mandate + 0.5)])

# Jeder Landesliste wird dabei der Reihe nach so oft ein Mandat angerechnet, als sie jeweils die höchste Teilungszahl aufweist.
hoechstzahlen = hoechstzahlen.sort_values(ascending=False)
res = hoechstzahlen.iloc[:min_mandate].index.value_counts()
res = pd.concat([df.loc[~df['5%_schwelle'], 'n_direkt_mandate'], res]).sort_values(ascending=False)
res.name = 'mandate'

# §6 Abs. 6
# In den Wahlkreisen errungene Direktmandate verbleiben einer Partei auch dann, wenn die Summe dieser Sitze die nach den Absätzen 3 und 4 ermittelte Zahl übersteigt (Überhangmandate)
ue_per_partei = df['n_direkt_mandate'] - res
ue_per_partei.loc[ue_per_partei < 0] = 0
n_ueberhang = ue_per_partei.sum()
res.loc[ue_per_partei.index] += ue_per_partei

# §6 Abs. 3 Sonderfall: Ergeben sich für den letzten Sitz oder die letzten Sitze gleiche Höchstzahlen für eine größere Anzahl von Landeslisten, als Sitze zu vergeben sind, entscheidet das von der Landeswahlleiterin oder dem Landeswahlleiter zu ziehende Los.
if (n_ueberhang == 0) and (hoechstzahlen.iloc[min_mandate] == hoechstzahlen.iloc[min_mandate - 1]):
    raise ValueError('Wahlleiter muss losen.')

# Die übrigen Landeslisten erhalten Ausgleichsmandate, wenn auf sie höhere Höchstzahlen entfallen als auf das letzte Überhangmandat
min_hoechstzahl = min(hoechstzahlen[partei].iloc[df.loc[partei, 'n_direkt_mandate']] for partei in df_5_prozent.index)
hoechstzahlen = hoechstzahlen.iloc[min_mandate:]
hoechstzahlen = hoechstzahlen[hoechstzahlen > min_hoechstzahl].reset_index()
# Höchstzahlen löschen, die bereits als Überhangmandate vergeben wurden
hoechstzahlen = hoechstzahlen.groupby('partei').apply(lambda df: df.iloc[ue_per_partei.loc[df.partei.iloc[0]]:])
hoechstzahlen = hoechstzahlen.reset_index(drop=True).set_index('partei')['n_listenstimmen'].sort_values(ascending=False)

# Die Zahl der Ausgleichsmandate darf die der Überhangmandate nicht übersteigen.
ausgleichsmandate = hoechstzahlen.iloc[:n_ueberhang].index.value_counts()

# §6 Abs. 3 Sonderfall: Ergeben sich für den letzten Sitz oder die letzten Sitze gleiche Höchstzahlen für eine größere Anzahl von Landeslisten, als Sitze zu vergeben sind, entscheidet das von der Landeswahlleiterin oder dem Landeswahlleiter zu ziehende Los.
if (len(hoechstzahlen) > n_ueberhang) and (hoechstzahlen.iloc[n_ueberhang] == hoechstzahlen.iloc[n_ueberhang - 1]):
    raise ValueError('Wahlleiter muss losen.')

res.loc[ausgleichsmandate.index] += ausgleichsmandate

res.to_csv('Ergebnis.csv')
