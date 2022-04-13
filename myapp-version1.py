from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore

# TẢI DỮ LIỆU TỪ FIRESTORE
cred = credentials.Certificate("thuthu-0403-firebase-adminsdk-o8f98-3ccb4959d5.json")
appLoadData = firebase_admin.initialize_app(cred)

dbFireStore = firestore.client()
queryResults = list(dbFireStore.collection(u'17020741EDWOrdered').where(u'COUNTRY', u'==', 'USA').stream())
listQueryResult = list(map(lambda x: x.to_dict(), queryResults))
dfQueryResult = pd.DataFrame(listQueryResult)
# Tổng hợp dữ liệu
data = dfQueryResult.groupby(['YEAR_ID','QTR_ID'])['TotalProductOrdered'].sum().reset_index(name='SumProductQTRYEAR')
dfTemp = dfQueryResult.groupby(['YEAR_ID','QTR_ID'])['TotalSaleOrdered'].sum().reset_index(name='SumSaleQTRYEAR')
data = data.merge(dfTemp)
dfTemp = dfQueryResult.groupby(['YEAR_ID','QTR_ID'])['ORDERNUMBER'].size().reset_index(name='QuantityQTRYEAR')
data = data.merge(dfTemp)

data["YEAR_ID"] = data["YEAR_ID"].astype("str")
data["QTR_ID"] = data["QTR_ID"].astype("str")
# TRỰC QUAN HÓA DỮ LIỆU WEB APP
app = Dash(__name__)

figSoLuongSanPham = px.bar(data, x="YEAR_ID", y="SumProductQTRYEAR", 
barmode="group", color="QTR_ID", title='Tổng số lượng sản phẩm theo quý và năm',
labels={'YEAR_ID':'Từ năm 2003, 2004 và 2005', 'QTR_ID': 'Quý trong năm', 'SumProductQTRYEAR':'Tổng số lượng SP'})

figDoanhSo = px.pie(data, values='SumSaleQTRYEAR', names='YEAR_ID',
labels={'YEAR_ID':'Năm','SumSaleQTRYEAR':'Doanh số'},
title='Tổng doanh số theo năm')

figSoLuongHoaDon = px.sunburst(data, path=['YEAR_ID', 'QTR_ID'], values='QuantityQTRYEAR',
color='QuantityQTRYEAR',
labels={'parent':'Năm', 'labels':'Quý','QuantityQTRYEAR':'Số lượng đơn hàng'},
title='Số lượng đơn hàng theo quý và năm')

app.layout = html.Div(
    children=[
        html.H1(children="Phân tích đơn hàng tại thị trường USA"),
        html.P(
            children="Phân tích khối lượng đơn hàng"
            " theo số lượng sản phẩm và tổng doanh số"
            " trong năm 2003, 2004 và 2005 theo từng quý"
        ),
        html.H1(children="Business Intelligence with Python by MR. NAM"),
        dcc.Graph(
            id='soluong-graph',
            figure=figSoLuongSanPham
        ),
        dcc.Graph(
            id='doanhso-graph',
            figure=figDoanhSo
        ),
        dcc.Graph(
            id='soluongdonhang-graph',
            figure=figSoLuongHoaDon
        )
        
])


if __name__ == '__main__':
    app.run_server(debug=True, port=8050)