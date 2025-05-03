import pandas as pd

def generar_cohortes_conversion(visitas, ordenes):
    # Obtener primera visita por usuario
    first_visits = visitas.groupby("uid")["start_ts"].min().reset_index()
    first_visits.columns = ["uid", "first_visit"]

    # Obtener primera compra por usuario
    first_orders = ordenes.groupby("uid")["buy_ts"].min().reset_index()
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

def calcular_ltv_por_cohorte(visitas, ordenes):
    # Obtener mes de primera visita
    first_visits = visitas.groupby('uid')['start_ts'].min().reset_index()
    first_visits['cohort_month'] = first_visits['start_ts'].dt.to_period('M')

    # Agregar cohort_month a ordenes
    ordenes = pd.merge(ordenes, first_visits[['uid', 'cohort_month']], on='uid', how='left')

    # Mes de la orden y diferencia en meses desde la cohorte
    ordenes['order_month'] = ordenes['buy_ts'].dt.to_period('M')
    ordenes['months_since_acquisition'] = (ordenes['order_month'] - ordenes['cohort_month']).apply(lambda x: x.n)

    # Total de usuarios por cohorte
    usuarios_por_cohorte = first_visits.groupby('cohort_month')['uid'].nunique()

    # Ingresos por cohorte y mes relativo
    ingresos = ordenes.groupby(['cohort_month', 'months_since_acquisition'])['revenue'].sum().reset_index()

    # Unir con total de usuarios
    ingresos['usuarios'] = ingresos['cohort_month'].map(usuarios_por_cohorte)
    print(ingresos['usuarios'] )
    ingresos['ltv'] = ingresos['revenue'] / ingresos['usuarios']

    # Pivot para formato tabla
    ltv_cohorte = ingresos.pivot(index='cohort_month', columns='months_since_acquisition', values='ltv')
    
    return ltv_cohorte

def calcular_cac(costos_por_fuente, cohort_conversion, visitas):
    # Unimos visitas con cohort_conversion para obtener el source_id
    cohort_conversion = cohort_conversion.merge(visitas[['uid', 'source_id']], on='uid', how='left')

    # Sacamos el número de usuarios únicos por source_id
    usuarios_por_fuente = cohort_conversion.groupby(['source_id'])['uid'].nunique().reset_index()
    usuarios_por_fuente.rename(columns={'uid': 'usuarios'}, inplace=True)

    # Unimos costos por fuente con usuarios por fuente
    cac = costos_por_fuente.merge(usuarios_por_fuente, on='source_id', how='left')

    # Calculamos el CAC
    cac['cac'] = cac['costs'] / cac['usuarios']

    return cac

def calcular_romi(costos_por_fuente, ordenes, source_id_n_uid):
    # Unimos ordenes con source_id_n_uid para obtener el source_id
    ordenes = ordenes.merge(source_id_n_uid, on='uid', how='left')

    # Calculamos el revenue por fuente  
    revenue_por_fuente = ordenes.groupby('source_id')['revenue'].sum().reset_index()
    revenue_por_fuente.rename(columns={'revenue': 'revenue'}, inplace=True)

    # Unimos costos por fuente con revenue por fuente
    costos_por_fuente = costos_por_fuente.merge(revenue_por_fuente, on='source_id', how='outer')

    # Calculamos el revenue por fuente
    romi = costos_por_fuente[['source_id', 'costs', 'revenue']].copy()
    romi['romi'] = (romi['revenue'] - romi['costs']) / romi['costs']

    return romi
