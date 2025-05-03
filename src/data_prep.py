# Función para gráficar histogramas de variables numéricas (hecho con ayuda de deepseek r1)
from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import re

class Eda:
    @staticmethod
    def plot_numeric_analysis(df, numeric_cols, figsize=(15, 10), col_objetivo=None):
        """Gráfica histogramas de variables numéricas, adaptando los ejes a la data.
        Si hay columnas de fecha, se pueden usar para el eje x con col_objetivo en el eje y."""
        if not numeric_cols:
            print("No hay columnas numéricas para graficar.")
            return
            
        # Detectar columnas de fecha
        date_cols = []
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                date_cols.append(col)
            elif pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_string_dtype(df[col]):
                # Intentar convertir a fecha si es string
                try:
                    pd.to_datetime(df[col], errors='raise')
                    date_cols.append(col)
                except:
                    pass
        
        # Si hay una columna de fecha y un col_objetivo, crear un gráfico especial
        if date_cols and len(date_cols) == 1 and col_objetivo and col_objetivo in df.columns:
            fig, ax = plt.subplots(figsize=(12, 6))
            date_col = date_cols[0]
            
            # Convertir la columna a datetime si aún no lo es
            if not pd.api.types.is_datetime64_any_dtype(df[date_col]):
                df_plot = df.copy()
                df_plot[date_col] = pd.to_datetime(df_plot[date_col], errors='coerce')
            else:
                df_plot = df
                
            # Graficar con fecha en x y col_objetivo en y
            df_plot = df_plot.sort_values(by=date_col)
            ax.plot(df_plot[date_col], df_plot[col_objetivo], marker='o', linestyle='-', alpha=0.7)
            ax.set_title(f'{col_objetivo} vs {date_col}')
            ax.set_xlabel(date_col)
            ax.set_ylabel(col_objetivo)
            # Formatear el eje x para mejor visualización de fechas
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
            return

        n_cols = min(3, len(numeric_cols))
        n_rows = (len(numeric_cols) + n_cols - 1) // n_cols

        if len(numeric_cols) <= 2:
            figsize = (8, 5)

        fig, axes = plt.subplots(n_rows, n_cols, figsize=figsize)
        fig.suptitle('Análisis de Variables Numéricas', fontsize=16)

        # Aplanar los ejes para simplificar la iteración
        axes = np.array(axes).flatten() if isinstance(axes, np.ndarray) else np.array([axes])

        for idx, col in enumerate(numeric_cols):
            # Se extrae la data de la columna ignorando valores nulos
            data = df[col].dropna()
            # Se calcula un margen del 5% del rango para que el gráfico no esté muy pegado a los bordes
            if not data.empty and np.isfinite(data).all():
                margin = 0.05 * (data.max() - data.min()) if data.max() != data.min() else 0.5
                x_min = data.min() - margin
                x_max = data.max() + margin
                
                # Graficamos el histograma usando bins automáticos para mejor adaptación
                sns.histplot(data=df, x=col, ax=axes[idx], bins='auto')
                axes[idx].set_title(f'Distribución de {col}')
                
                # Solo establecer límites si son finitos
                if np.isfinite(x_min) and np.isfinite(x_max):
                    axes[idx].set_xlim(x_min, x_max)
            else:
                # Si no hay datos válidos o contiene infinitos/NaN
                axes[idx].text(0.5, 0.5, 'No hay datos válidos para graficar',
                              horizontalalignment='center', verticalalignment='center',
                              transform=axes[idx].transAxes)
                axes[idx].set_title(f'Distribución de {col}')

        # Ocultar subplots no utilizados
        for idx in range(len(numeric_cols), len(axes)):
            axes[idx].set_visible(False)

        # Ajustamos el layout dejando espacio para el título general
        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.show()

    # Función para detectar outlayers con el método IQR, extremos y no extremos
    @staticmethod
    def iqr_method(column):
        """Detecta outliers usando el método IQR."""
        q1 = column.quantile(0.25)
        q3 = column.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        extreme_lower_bound = q1 - 3 * iqr
        extreme_upper_bound = q3 + 3 * iqr
        return pd.Series([column>upper_bound, column<lower_bound, column>extreme_upper_bound, column<extreme_lower_bound], 
                         index=['outliers_upper', 'outliers_lower', 'extreme_upper', 'extreme_lower'])

    @staticmethod
    def standarize_columns(cols):
        cols = cols.str.lower()
        cols = cols.str.replace(' ', '_')
        cols = cols.str.replace('(', '')
        cols = cols.str.replace(')', '')
        return cols

    # Función para realizar un análisis exploratorio de una tabla (mejorado con ayuda de claude 3.7 sonnet)
    @staticmethod
    def analisis_exploratorio(name, df, col_objetivo=None):
        """Realiza un análisis exploratorio de una tabla.
        
        Args:
            name: Nombre de la tabla
            df: DataFrame a analizar
            col_objetivo: Columna objetivo para gráficos con fechas (opcional)
        """
        df = df.copy()
        df.columns = Eda.standarize_columns(df.columns)
        total_chars = 125
        print("="*total_chars)
        string = f"Análisis de la tabla {name}"
        print('|' + string.center(total_chars-2) + '|')
        print("="*total_chars)
        print(f"Dimensiones: {df.shape}")
        
        # Expresión regular para identificar columnas ID
        id_pattern = re.compile(
            r'^id_.*|.*_id$|^id$|^Id_.*|.*_Id$|^Id$',  # Empieza con id_ o Id_, termina con _id o _Id, o es exactamente id o Id
            flags=re.IGNORECASE
        )
        id_cols = [col for col in df.columns if id_pattern.fullmatch(col)]
        
        # Separar columnas numéricas y no numéricas
        numeric_cols = [col for col in df.select_dtypes(include=['int64', 'float64']).columns if col not in id_cols]
        non_numeric_cols = list(df.select_dtypes(exclude=['int64', 'float64']).columns)
        
        # Normalizar strings y manejar IDs
        for col in non_numeric_cols:
            if pd.api.types.is_string_dtype(df[col]):
                df[col] = df[col].apply(lambda x: x.lower().strip() if pd.notna(x) else x)
        
        # Agregar IDs a no numéricas para estadísticas especiales
        non_numeric_cols += id_cols

        non_numeric_stats = []
        if non_numeric_cols:
            for col in non_numeric_cols:
                stats = {
                    'Columna': col,
                    'Valores Únicos': df[col].nunique(),
                    'Media': '-',
                    'Desviación Estándar': '-',
                    'Mínimo': df[col].min() if col in id_cols else '-',
                    'Mediana': '-',
                    'Máximo': df[col].max() if col in id_cols else '-'
                }
                non_numeric_stats.append(stats)
        
        numeric_stats = []
        cols_to_remove = []
        if numeric_cols:
            for col in numeric_cols:
                if df[col].nunique() == 2 and set(df[col].dropna().unique()).issubset({0, 1}):
                    df[col] = df[col].astype('boolean')
                    cols_to_remove.append(col)
                else:
                    numeric_stats.append({
                        'Columna': col,
                        'Valores Únicos': df[col].nunique(),
                        'Media': df[col].mean(),
                        'Desviación Estándar': df[col].std(),
                        'Mínimo': df[col].min(),
                        'Mediana': df[col].median(),
                        'Máximo': df[col].max()
                    })
            # Remover columnas convertidas a boolean
            numeric_cols = [col for col in numeric_cols if col not in cols_to_remove]
        
        # Crear un único DataFrame con todas las estadísticas
        all_stats = []
        
        for col in df.columns:
            is_numeric = col in numeric_cols
            
            stats = {
                'Columna': col,
                'Valores Únicos': df[col].nunique(),
                'Media': df[col].mean() if is_numeric else '-',
                'Desviación Estándar': df[col].std() if is_numeric else '-',
                'Mínimo': df[col].min() if is_numeric or col in id_cols else '-',
                'Mediana': df[col].median() if is_numeric else '-',
                'Máximo': df[col].max() if is_numeric or col in id_cols else '-',
                'Tipos de datos': df[col].apply(type).unique() if len(df[col].apply(type).unique()) == 1 else '\n'.join(str(t) for t in df[col].apply(type).unique()),
                'NaN/Null': df[col].isnull().sum(),
                'Duplicados únicos': len(df[(df.duplicated(subset=[col], keep='first'))&(df[col].notnull())]),
                'Duplicados totales': len(df[(df.duplicated(subset=[col], keep=False))&(df[col].notnull())])
            }
            
            # Agregar información de outliers solo para columnas numéricas
            if is_numeric:
                iqr_stats = Eda.iqr_method(df[col])
                stats.update({
                    'Outlayers (IQR extreme_lower)': iqr_stats['extreme_lower'].sum(),
                    'Outlayers (IQR lower)': iqr_stats['outliers_lower'].sum(),
                    'Outlayers (IQR upper)': iqr_stats['outliers_upper'].sum(),
                    'Outlayers (IQR extreme_upper)': iqr_stats['extreme_upper'].sum()
                })
            else:
                stats.update({
                    'Outlayers (IQR extreme_lower)': '-',
                    'Outlayers (IQR lower)': '-',
                    'Outlayers (IQR upper)': '-',
                    'Outlayers (IQR extreme_upper)': '-'
                })
                
            all_stats.append(stats)
        
        # Crear un único DataFrame con todas las estadísticas
        all_stats_df = pd.DataFrame(all_stats).set_index('Columna')
        inconsistencias_stats_df = all_stats_df.T
        
        print('\nEstadísticas descriptivas y problemas de calidad:')
        print(inconsistencias_stats_df.to_markdown(index=True))
        
        if numeric_cols:
            # Filtrar columnas numéricas que contienen valores infinitos o NaN
            valid_numeric_cols = []
            for col in numeric_cols:
                if df[col].dropna().empty or not np.isfinite(df[col].dropna()).all():
                    print(f"Advertencia: La columna '{col}' contiene valores no finitos y no será graficada.")
                else:
                    valid_numeric_cols.append(col)
            
            if valid_numeric_cols:
                Eda.plot_numeric_analysis(df, valid_numeric_cols, col_objetivo=col_objetivo)
            else:
                print("No hay columnas numéricas válidas para graficar.")
        return