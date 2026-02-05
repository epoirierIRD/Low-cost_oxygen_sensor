#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 16 10:44:31 2025

@author: epoirier1
"""


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from datetime import date, time, datetime
import matplotlib.dates as mdates
from fpdf import FPDF
import os
from io import StringIO





'''
#################################################################################################################################
#Gestion du format de l'heure
# attention du formatage est nécessaire avant pour fabriquer les fichiers csv d'entrée à partir des fichiers xlsx bruts de sortie des logiciels fabricants
#################################################################################################################################
# lecteur qui prend en compte les décimales sur le format d'heure
df1 = pd.read_csv(rbr231853, parse_dates=['date'], sep=';', date_parser=lambda x: pd.to_datetime(x, format='%Y-%m-%d %H:%M:%S,%f'))
df2 = pd.read_csv(rbr236135, parse_dates=['date'], sep=';',date_parser=lambda x: pd.to_datetime(x, format='%Y-%m-%d %H:%M:%S,%f'))
# attention ligne ci-dessous adaptée pour SBE
df3 = pd.read_csv(sbe, parse_dates=['date'], sep=',',date_parser=lambda x: pd.to_datetime(x, format='%Y-%m-%d %H:%M:%S.%f'))
# Ajouter le déphasage de 9 secondes à la colonne 'date' car la SBE avançait de 9sec pendant les opérations
df3['date'] = df3['date'] - pd.to_timedelta(9, unit='s')
df3.apply(lambda x: pd.to_numeric(x.str.replace(',', '.'), errors='coerce') if x.dtype == 'object' else x)
'''

# parser to read the wtw data

def read_wtw(ref_csv):

    # Read the data using pandas
    from io import StringIO
    df = pd.read_csv(
    ref_csv, 
    sep=";", 
    na_values=["no_data"],  # Treat 'no_data' as NaN
    dtype={"wtw_temp(°C)": float, "wtw_DO(mg/L)": float, "wtw_Dosat(%)": float},
    skiprows = [0,10]
    )

    # Combine 'Date' and 'Time HL' into a single datetime column
    df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time HL'])
    
    # Drop the original 'Date' and 'Time HL' columns
    df.drop(columns=['Date', 'Time HL'], inplace=True)
    
    # Reorder columns
    df = df[['DateTime', 'wtw_temp(°C)', 'wtw_DO(mg/L)', 'wtw_Dosat(%)', 'event']]
    
    return df

def read_serial_monitor(file_path):
    """
    Parses a log file containing semi-structured data into a pandas DataFrame.

    Args:
        file_path (str): Path to the text file containing the log data.

    Returns:
        pd.DataFrame: DataFrame containing parsed data with columns:
                      ["Time", "Temperature (°C)", "DO (mg/L)", "DO Saturation (%)"].
    """
    # Read the file and extract only relevant lines containing log data
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Filter lines matching the log pattern
    log_pattern = r"(\\d{2}:\\d{2}:\\d{2}\\.\\d{3}) -> Température: ([\\d\\.]+)°C, DO: ([\\d\\.]+)mg/L, DO Saturé: ([\\d\\.]+)%"
    log_lines = [re.sub(log_pattern, r"\\1,\\2,\\3,\\4", line.strip()) for line in lines if re.search(log_pattern, line)]

    # Join filtered lines into a CSV-like string
    processed_data = "\n".join(log_lines)

    # Define the column names
    columns = ["Time", "Temperature (°C)", "DO (mg/L)", "DO Saturation (%)"]

    # Read the processed data into a DataFrame
    df = pd.read_csv(StringIO(processed_data), names=columns)

    return df

# Main
ref_csv = '/home/epoirier1/Documents/PROJETS/2024/oxygen_probe_seeedstudio/comparison_test_16012025/WTW_ref_data.csv'
instru_txt = '/home/epoirier1/Documents/PROJETS/2024/oxygen_probe_seeedstudio/comparison_test_16012025/DO_probe_data.txt'

dfr = read_wtw(ref_csv)
dfi = read_serial_monitor(instru_txt)

'''



#################################################################################################################################
# Chargement des données
# Assurez-vous que chaque fichier contient au moins deux colonnes : 'date' et 'temperature'
# ce script permet de lire 3 fichiers csv venant d'uen intercomp à ste anne avec 2 RBR et 1 SBE
# Il sort les statistiques pour chaque paramètre un PDF avec le graphique également
#################################################################################################################################

#attention, c'est epoirier1 sur le fixe et epoirier sur le portable
rbr231853 = '/home/epoirier1/Documents/METROLOGIE/2024/intercomp_steanne_12092024/Maestro_P2I_231853/231853_20240912_1229.csv'
rbr236135 = '/home/epoirier1/Documents/METROLOGIE/2024/intercomp_steanne_12092024/Maestro_P2I_236135/236135_20240912_1238.csv'
sbe = '/home/epoirier1/Documents/METROLOGIE/2024/intercomp_steanne_12092024/SBE/sbe_time_corrected.csv'

#################################################################################################################################
#Gestion du format de l'heure
# attention du formatage est nécessaire avant pour fabriquer les fichiers csv d'entrée à partir des fichiers xlsx bruts de sortie des logiciels fabricants
#################################################################################################################################
# lecteur qui prend en compte les décimales sur le format d'heure
df1 = pd.read_csv(rbr231853, parse_dates=['date'], sep=';', date_parser=lambda x: pd.to_datetime(x, format='%Y-%m-%d %H:%M:%S,%f'))
df2 = pd.read_csv(rbr236135, parse_dates=['date'], sep=';',date_parser=lambda x: pd.to_datetime(x, format='%Y-%m-%d %H:%M:%S,%f'))
# attention ligne ci-dessous adaptée pour SBE
df3 = pd.read_csv(sbe, parse_dates=['date'], sep=',',date_parser=lambda x: pd.to_datetime(x, format='%Y-%m-%d %H:%M:%S.%f'))
# Ajouter le déphasage de 9 secondes à la colonne 'date' car la SBE avançait de 9sec pendant les opérations
df3['date'] = df3['date'] - pd.to_timedelta(9, unit='s')
df3.apply(lambda x: pd.to_numeric(x.str.replace(',', '.'), errors='coerce') if x.dtype == 'object' else x)

#################################################################################################################################
#Creation du dataframe global avec tous les instruments
#################################################################################################################################
# Fusionner les trois DataFrames sur la colonne 'date', ils sont tous à 0.5 sec
# on n'ajoute pas de suffixe car fait avant
# merge accepts only two df
merged_df = pd.merge(df1, df2 ,on='date', suffixes=('_rbr231853', '_rbr236135'))

# on va renommer les colonnes du df de la sbe avant merging sauf la colonne date
# Use rename to add a suffix to all columns except the one you want to exclude
df3 = df3.rename(columns=lambda x: f"{x}_sbeSOMLIT" if x != 'date' else x)

merged_df = pd.merge(merged_df,df3, on='date')

#################################################################################################################################
#Selection de la fenêtre temporelle d'intérêt
#################################################################################################################################
# #Periode d'intérêt, en monitoring
start = datetime(2024, 9, 12, 9, 52,40)
end = datetime(2024, 9, 12, 9, 58,20)
#Periode d'intérêt, stable en monitoring mais courte
# start = datetime(2024, 9, 12, 9, 57,00)
# end = datetime(2024, 9, 12, 9, 58,20)
# Filtrer le DataFrame entre les deux dates
merged_df = merged_df[(merged_df['date'] >= start) & (merged_df['date'] <= end)]

#################################################################################################################################
#Sélection des paramètres à examiner métrologiquement
#################################################################################################################################
# Liste des paramètres à comparer
# Mettre _ pour comparer seulement le premier capteur de Tempé du RBR l'autre est Temperature.1, on l'exclut
#parameters = ['PAR']
parameters = ['Temperature_','Conductivity','Pressure','Dissolved O2 concentration','PAR','pH','Chlorophyll-a','FDOM','Turbidity','Sea pressure','Depth','Salinity','Speed of sound','Specific conductivity','Dissolved O2 saturation','Density anomaly']

# Définition des unités pour chaque paramètre

# Define units for each parameter
parameter_units = {
    'Temperature_':'°C',
    'Conductivity':'mS/cm',
    'Pressure':'dBar(ou m)',
    'Temperature(Coda T.ODO)':'°C',
    'Dissolved O2 concentration':'µmol/L',
    'PAR':'µMol/m2/s',
    'pH':'pH_units',
    'Chlorophyll-a':'µg/L',
    'FDOM':'ppb',
    'Turbidity':'FTU',
    'Sea pressure':'dBar(ou m)',
    'Depth':'m',
    'Salinity':'PSU',
    'Speed of sound':'m/s',
    'Specific conductivity':'µS/cm',
    'Dissolved O2 saturation':'%',
    'Density anomaly':'kg/m3'
}
# Display accuracy for each parameter from specs
nominal_accuracy_rbr = {
    'Temperature_':'±0.002°C',
    'Conductivity':'±0.003 mS/cm',
    'Pressure':'±0.05% Full Scale = ±0.375 dBar(ou m)',
    'Temperature(Coda T.ODO)':'±0.002 °C',
    'Dissolved O2 concentration':'Maximum of ±8μmol/L ',
    'PAR':'±5% of reading or ±1.4 µMol/m2/s',
    'pH':'Accuracy unknown pH_units',
    'Chlorophyll-a':'±5.0% full scale (±2.5 µg/L). Cal range [0-50] µg/L ',
    'FDOM':'±5.0% full scale (±25.0 ppb)',
    'Turbidity':'±5.0% full scale (±25.00 FTU)',
    'Sea pressure':'±0.05% Full Scale = ±0.375 dBar(ou m)',
    'Depth':'±0.05% Full Scale = ±0.375 dBar(ou m)',
    'Salinity':'estimated 0.01 PSU',
    'Speed of sound':'Calculated parameter m/s',
    'Specific conductivity':'Calculated parameter 3 µS/cm',
    'Dissolved O2 saturation':'±5% | fast%',
    'Density anomaly':'Calculated parameter kg/m3'}




# Remplacer les virgules par des points, puis convertir toutes les colonnes en float
merged_df = merged_df.apply(lambda x: pd.to_numeric(x.str.replace(',', '.'), errors='coerce') if x.dtype == 'object' else x)





#################################################################################################################################
#Fonctions pour les stats et le plotting
#################################################################################################################################

import pandas as pd
import numpy as np

def calculate_stats(parameters, df):
    """
    Calcule les statistiques pour chaque paramètre et génère un fichier CSV distinct par paramètre.

    Paramètres :
    - parameters : Liste des paramètres à analyser (e.g., ['temperature', 'conductivity', 'pressure']).
    - df : DataFrame contenant les données des instruments pour chaque paramètre.

    Retour :
    - Un fichier CSV pour chaque paramètre contenant les moyennes, écarts-types, moyennes des différences, et RMSE.
    """
    for param in parameters:
        # Filtrer les colonnes du paramètre pour chaque instrument
        param_cols = [col for col in df.columns if col.startswith(param)]

        # S'assurer qu'il y a au moins trois colonnes
        if len(param_cols) < 3:
            print(f"Skipping {param}: only {len(param_cols)} columns found. Expected at least 3.")
            print(f"Columns found: {param_cols}")
            continue  # Passer au paramètre suivant s'il y a moins de 3 colonnes

        # Calcul des moyennes et écarts-types pour chaque instrument
        stats_summary = {}
        for col in param_cols:
            stats_summary[col] = {
                'mean': df[col].mean(),
                'std': df[col].std()
            }

        # Liste pour stocker les résultats pour ce paramètre
        results = []

        # Ajouter les moyennes et écarts-types à la liste des résultats
        results.append([f"{param} - Instrument Stats", "", ""])
        for col in param_cols:
            results.append([col, "%.4f" % stats_summary[col]['mean'], "%.4f" % stats_summary[col]['std']])

        # Ajouter l'en-tête "Mean of Differences and RMSE" sur une seule ligne avec les colonnes Mean et RMSE
        results.append(["Mean of Differences and RMSE", "Mean of Differences", "RMSE"])

        # Calcul des différences moyennes et RMSE pour chaque paire d'instruments
        instrument_pairs = [(param_cols[0], param_cols[1]), (param_cols[0], param_cols[2]), (param_cols[1], param_cols[2])]

        for inst1, inst2 in instrument_pairs:
            # Calculer les différences entre les deux instruments
            differences = df[inst1] - df[inst2]

            # Calculer la moyenne des différences
            mean_diff = differences.mean()

            # Calculer le RMSE
            rmse = np.sqrt(np.mean(np.square(differences)))

            # Ajouter à la liste des résultats
            results.append([f"{inst1} - {inst2}", '%.4f' % mean_diff, '%.4f' % rmse])

        # Création du DataFrame des résultats
        results_df = pd.DataFrame(results, columns=["Instrument statistics", "Mean", "Standard Deviation"])

        # Générer un fichier CSV distinct pour ce paramètre
        csv_filename = f'{param}_comparison_stats.csv'
        results_df.to_csv(csv_filename, index=False)

        print(f"Results for {param} saved to {csv_filename}")
        
        print(results_df)





# Function to create a plot for the parameter and save it as an image
def plot_instruments(parameter, df, output_file):
    # Select the columns for the parameter
    cols = [col for col in df.columns if parameter in col]
    
    # Plot the data for the three instruments
    plt.figure(figsize=(8, 6))
    for col in cols:
        plt.plot(df['date'], df[col], label=col)
    
    plt.title(f"{parameter.capitalize()} Comparison")
    plt.xlabel("Time")
    plt.ylabel(parameter.capitalize())
    plt.legend()
    plt.grid(True)
    # Format the x-axis to show date and time. Ligne importante sinon les heures affichees sont fausses
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    #plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    #plt.gcf().autofmt_xdate()  # Automatically format date labels to avoid overlap
    # Save the plot to a file
    plt.savefig(output_file)
    plt.close()



# Fonction pour ajouter les statistiques CSV dans un PDF
def csv_to_pdf(csv_filename, param_name, merged_df):
    """
    Lire un fichier CSV et l'insérer dans un tableau PDF.
    
    - csv_filename : Le fichier CSV contenant les statistiques.
    - pdf_filename : Le fichier PDF à créer.
    - param_name : Le nom du paramètre à utiliser pour le titre du tableau.
    """
    
    # Lire les données du CSV avec pandas
    df = pd.read_csv(csv_filename, skiprows=[1])
    
    
    # Créer un objet PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Titre du PDF (le nom du paramètre étudié)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, f"Statistiques de comparaison pour {param_name}", ln=True, align="C")
    
    # Add units for the parameter
    unit = parameter_units.get(param_name, '')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Units: {unit}", ln=True, align='C')
    
    # Add nominal accuracy from specs for the parameter
    accuracy = nominal_accuracy_rbr.get(param_name, 'N/A')
    pdf.cell(200, 10, f"Nominal accuracy from specs: {accuracy}", ln=True, align='C')

    # Ajouter un espace
    pdf.ln(10)

    # Créer un tableau avec les données du CSV
    pdf.set_font("Arial", size=10)
    
    # Largeurs des colonnes
    col_widths = [100, 40, 40]

    # En-têtes du tableau (colonnes du CSV)
    for i, col in enumerate(df.columns):
        pdf.cell(col_widths[i], 10, col, border=1, align='C')
    pdf.ln()

    # Ajouter les lignes de données
    for _, row in df.iterrows():
        for i, col in enumerate(df.columns):
            pdf.cell(col_widths[i], 10, str(row[col]), border=1, align='C')
        pdf.ln()

    # # Add some space before the plot
    # pdf.ln(10)
    
    # Generate and save the plot
    plot_filename = f"{param_name}_plot.png"
    plot_instruments(param_name, merged_df, plot_filename)
    
    # Insert the plot image into the PDF
    pdf.image(plot_filename, x=10, y=None, w=190)  # Adjust size and position as necessary
   
    # Save the PDF to file with the parameter as the filename
    pdf_output = f"{param_name}_comparison_stats.pdf"
    pdf.output(pdf_output)
    print(f"PDF saved as {pdf_output}")
   
    # Save the PDF to file with the parameter as the filename
    pdf_output = f"{param_name}_comparison_stats.pdf"
    pdf.output(pdf_output)
    print(f"PDF saved as {pdf_output}")



################################################################################################################################
#!!!!!!!!!!!!!!!    MAIN au-dessous    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#################################################################################################################################

# Assuming `merged_df` is the merged DataFrame with all instruments' data
#compare_instruments(parameters, merged_df)

calculate_stats(parameters, merged_df)

# Example: Create PDFs for different parameters
# for param in parameters:
#     csv_file = f"{param}_comparison_stats.csv"
#     create_pdf_from_csv(param, csv_file)
# Assuming `df` is the merged DataFrame with all instruments' data
for param in parameters:
    csv_file = f"{param}_comparison_stats.csv"
    # Tester si le fichier existe
    if not os.path.exists(csv_file):
        print(f"File {csv_file} not found, skipping {param}.")
        continue  # Revenir au début de la boucle si le fichier n'existe pas
    
    csv_to_pdf(csv_file, param, merged_df)
    
    
################################################################################################################################
#!!!!!!!!!!!!!!!    MAIN au dessus     !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#################################################################################################################################
    
  '''
    
  
    
  # ----------------- CRAP BELOW  --------------------------------
    
    # # Plot the data for the three instruments
    # plt.figure(figsize=(8, 6))
    # for col in cols:
    #     plt.plot(df.index, df[col], label=col)
    
    # plt.title(f"{parameter.capitalize()} Comparison")
    # plt.xlabel("Time")
    # plt.ylabel(parameter.capitalize())
    # plt.legend()
    
    # # Save the plot to a file
    # plt.savefig(output_file)
    # plt.close()



# # Comparaison des paramètres
# for param in parameters:
    
#     # Select all columns starting with 'param' (e.g., 'temperature', 'density')
#     columns_to_compare = [col for col in merged_df.columns if col.startswith(param)]
    
#     # Ensure there are exactly 3 columns for comparison
#     if len(columns_to_compare) != 3:
#         print(f"Expected 3 columns for {param}, but found {len(columns_to_compare)}")
#         continue
#     # Extract the data for comparison
#     df_param = merged_df[columns_to_compare]

#     # Calculate statistics for each instrument
#     for col in columns_to_compare:
#         mean_value = df_param[col].mean()
#         std_value = df_param[col].std()
#         print(f"{col}: Mean = {mean_value:.3f}, Std = {std_value:.3f}")

#     # # Calculate pairwise Pearson correlation
#     # correlation_matrix = df_param.corr(method='pearson')
#     # print(f"\nCorrelation Matrix for {param.capitalize()}:")
#     # print(correlation_matrix)


    
    
    
    
    # # Calcul des statistiques descriptives
    # mean_inst1 = merged_df[f'{param}_inst1'].mean()
    # std_inst1 = merged_df[f'{param}_inst1'].std()

    # mean_inst2 = merged_df[f'{param}_inst2'].mean()
    # std_inst2 = merged_df[f'{param}_inst2'].std()

    # # Calcul des statistiques de comparaison
    # mean_difference = abs(mean_inst1 - mean_inst2)
    # std_difference = abs(std_inst1 - std_inst2)

    # # Différence absolue moyenne entre les deux séries
    # mean_absolute_difference = np.mean(abs(merged_df[f'{param}_inst1'] - merged_df[f'{param}_inst2']))

    # # Corrélation entre les deux séries
    # correlation, p_value = stats.pearsonr(merged_df[f'{param}_inst1'], merged_df[f'{param}_inst2'])

    # # Affichage des résultats statistiques
    # print(f"Comparaison pour {param.capitalize()}:")
    # print(f"  Moyenne Instrument 1 : {mean_inst1:.5f}")
    # print(f"  Ecart-type Instrument 1 : {std_inst1:.5f}")
    # print(f"  Moyenne Instrument 2 : {mean_inst2:.5f}")
    # print(f"  Ecart-type Instrument 2 : {std_inst2:.5f}")
    # print(f"  Différence des moyennes : {mean_difference:.5f}")
    # print(f"  Différence des écarts-types : {std_difference:.5f}")
    # print(f"  Différence absolue moyenne : {mean_absolute_difference:.5f}")
    # print(f"  Corrélation (Pearson) : {correlation:.5f}")
    # print(f"  P-value : {p_value:.4f}\n")

    # # Visualisation des séries temporelles pour chaque paramètre
    # plt.figure(figsize=(12, 6))
    # plt.plot(merged_df['date'], merged_df[f'{param}_inst1'], label=f'Instrument 1 - {param}', color='blue')
    # plt.plot(merged_df['date'], merged_df[f'{param}_inst2'], label=f'Instrument 2 - {param}', color='red')
    # plt.title(f'Comparaison des séries temporelles pour {param.capitalize()}')
    # plt.xlabel('Date')
    # plt.ylabel(param.capitalize())
    # plt.legend()
    # plt.grid(True)
    # # Format the x-axis to show date and time. Ligne importante sinon les heures affichees sont fausses
    # plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    # #plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    # plt.gcf().autofmt_xdate()  # Automatically format date labels to avoid overlap
    
    # # Sauvegarder le plot dans un fichier
    # plt.savefig(f'{param}_comparison.png', dpi=300)  # Vous pouvez changer l'extension pour d'autres formats (pdf, svg, etc.)
    # plt.close()

    # # Visualisation de la différence entre les deux séries
    # plt.figure(figsize=(12, 6))
    # plt.plot(merged_df['date'], merged_df[f'{param}_inst1'] - merged_df[f'{param}_inst2'], label=f'Différence {param} (Instrument 1 - Instrument 2)', color='green')
    # plt.title(f'Différence des {param} mesurées')
    # plt.xlabel('Date')
    # plt.ylabel(f'Différence {param}')
    # plt.legend()
    # plt.grid(True)
    # # Format the x-axis to show date and time. Ligne importante sinon les heures affichees sont fausses
    # plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    # #plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    # plt.gcf().autofmt_xdate()  # Automatically format date labels to avoid overlap

    # # Sauvegarder le plot de la différence dans un fichier
    # plt.savefig(f'{param}_difference.png', dpi=300)
    # plt.close()
