import pandas as pd

def generar_cohortes_conversion(visits_df, orders_df):
    # Obtener primera visita por usuario
    first_visits = visits_df.groupby("uid")["start_ts"].min().reset_index()
    first_visits.columns = ["uid", "first_visit"]

    # Obtener primera compra por usuario
    first_orders = orders_df.groupby("uid")["buy_ts"].min().reset_index()
    first_orders.columns = ["uid", "first_purchase"]

    # Unir visitas y compras por uid (usuarios que hayan comprado)
    cohort_df = pd.merge(first_visits, first_orders, on="uid", how="inner")

    # Calcular días hasta conversión
    cohort_df["conversion_days"] = (cohort_df["first_purchase"] - cohort_df["first_visit"]).dt.days

    print(f"Max conversion days: {cohort_df['conversion_days'].max()}")
    print(f"Min conversion days: {cohort_df['conversion_days'].min()}")

    # Crear categoría de cohorte tipo "Conversion 0d"
    cohort_df["conversion_category"] = "Conversion " + cohort_df["conversion_days"].astype(str) + "d"

    return cohort_df

def calcular_ltv_por_cohorte(visits, orders):
    # Obtener mes de primera visita
    first_visits = visits.groupby('uid')['start_ts'].min().reset_index()
    first_visits['cohort_month'] = first_visits['start_ts'].dt.to_period('M')

    # Agregar cohort_month a orders
    orders = pd.merge(orders, first_visits[['uid', 'cohort_month']], on='uid', how='left')

    # Mes de la orden y diferencia en meses desde la cohorte
    orders['order_month'] = orders['buy_ts'].dt.to_period('M')
    orders['months_since_acquisition'] = (orders['order_month'] - orders['cohort_month']).apply(lambda x: x.n)

    # Total de usuarios por cohorte
    usuarios_por_cohorte = first_visits.groupby('cohort_month')['uid'].nunique()

    # Ingresos por cohorte y mes relativo
    ingresos = orders.groupby(['cohort_month', 'months_since_acquisition'])['revenue'].sum().reset_index()

    # Unir con total de usuarios
    ingresos['usuarios'] = ingresos['cohort_month'].map(usuarios_por_cohorte)
    ingresos['ltv'] = ingresos['revenue'] / ingresos['usuarios']

    # Pivot para formato tabla
    ltv_cohorte = ingresos.pivot(index='cohort_month', columns='months_since_acquisition', values='ltv')
    
    return ltv_cohorte
