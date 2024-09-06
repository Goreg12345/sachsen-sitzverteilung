import pandas as pd


df = pd.read_excel('statistik-sachsen_LW24_vorlErgebnisse.xlsx', sheet_name='LW24_vorlErgebnisse_SN&WK')

# alle Spalten mit "%" im Spaltennamen entfernen
df = df.loc[:, ~df.columns.str.contains('%')]
# alle Spalten mit "gültige" im Spaltennamen entfernen
df = df.loc[:, ~df.columns.str.contains('gültige')]
# erste Zeile löschen, da sie die Summe enthält
df = df.drop(0)
# x durch 0 ersetzen
df = df.replace('x', 0)

# alle Direktmandate durch Auswahl der Spalten mit _1 im Spaltennamen erhalten
df_direkt = df.loc[:, df.columns.str.contains('_1')]
df_liste = df.loc[:, df.columns.str.contains('_2')]
parteien = df_direkt.columns.str.split('_').str[0].unique().tolist()

# für jede Zeile den maximalen Wert der Direktmandate erhalten
df_direkt['max_direkt'] = df_direkt.max(axis=1)

# überprüfen, ob es Zeilen gibt, bei denen mehrere Parteien die gleiche Anzahl an Stimmen haben -> dann muss der Wahlleiter auslosen
df_direkt['anzahl'] = df_direkt.apply(lambda row: (row == row['max_direkt']).sum(), axis=1)
if df_direkt['anzahl'].max() > 2:
    raise ValueError('Wahlleiter muss losen.')

# die Partei mit der maximalen Anzahl an Stimmen erhalten
df_direkt['direkt_gewinner'] = df_direkt.idxmax(axis=1).str.split('_').str[0]

df_berreinigt = df_direkt.direkt_gewinner.value_counts().reindex(parteien).fillna(0).astype(int)
df_berreinigt.name = 'n_direkt_mandate'

# die Listenstimmen erhalten
# das _2 entfernen
df_liste.columns = df_liste.columns.str.replace('_2', '')
df_liste = df_liste.sum()
df_liste.name = 'n_listenstimmen'
# mit df_berreinigt zusammenführen
df_berreinigt = pd.concat([df_berreinigt, df_liste], axis=1).fillna(0).astype('int64')
df_berreinigt.index.name = 'partei'

df_berreinigt.to_csv('bereinigt.csv')
