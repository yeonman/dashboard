
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 한글 폰트 설정
font_path = "./NanumGothic-Regular.ttf"
fm.fontManager.addfont(font_path)
font_name = fm.FontProperties(fname=font_path).get_name()
plt.rcParams['font.family'] = font_name
plt.rcParams['axes.unicode_minus'] = False

# 데이터 로드
@st.cache_data
def load_data():
    df_handover = pd.read_parquet('df_handover_summary_monthly.parquet')
    df_loan_amt = pd.read_parquet('df_loan_amt_summary_monthly.parquet')
    op_handover = pd.read_parquet('op_car_handover.parquet')
    op_loan_amt = pd.read_parquet('op_car_loan_amt.parquet')
    return df_handover, df_loan_amt, op_handover, op_loan_amt

# Streamlit 기본 설정
st.set_page_config(layout="wide", page_title="현대캐피탈 Auto 본부 대시보드")

# 데이터 로드
df_handover, df_loan_amt, op_handover, op_loan_amt = load_data()

# 조합된 모듈 코드 실행

# === 통합공통모듈 ===

# ===== 🛠️ 공통 설정 및 사이드바 =====
st.title("Auto 본부 사업 현황")

# 사이드바 설정 - 기준년월 선택
st.sidebar.header(" 데이터 설정")
months = sorted(df_handover['기준년월'].unique(), reverse=True)
selected_month = st.sidebar.selectbox("기준년월 선택", months)

# 공통 계산
selected_year = selected_month[:4]
selected_month_num = int(selected_month[4:])
year_short = selected_year[2:]

# 전월 계산
if selected_month.endswith('01'):
    prev_month = str(int(selected_month[:4]) - 1) + '12'
else:
    prev_month = selected_month[:4] + str(int(selected_month[4:]) - 1).zfill(2)

# 사이드바 미리보기용 간단 계산
df_handover_month = df_handover[df_handover['기준년월'] == selected_month]
df_halbu = df_handover_month[df_handover_month['상품구분'] == '할부']
df_imdae = df_handover_month[df_handover_month['상품구분'] == '임대']

df_halbu_rate = (df_halbu['인수율분자값'].sum() / df_halbu['인수율분모'].sum() * 100) if len(df_halbu) > 0 else 0
df_imdae_rate = (df_imdae['인수율분자값'].sum() / df_imdae['인수율분모'].sum() * 100) if len(df_imdae) > 0 else 0
df_total_rate = df_halbu_rate + df_imdae_rate

df_loan_month = df_loan_amt[df_loan_amt['기준년월'] == selected_month]
df_halbu_amt = df_loan_month[df_loan_month['상품구분'] == '할부']['취급액'].sum() / 1e8
df_imdae_amt = df_loan_month[df_loan_month['상품구분'] == '임대']['취급액'].sum() / 1e8
df_total_amt = df_halbu_amt + df_imdae_amt

df_junggo_amt = df_loan_month[df_loan_month['상품구분_세부'] == '중고론']['취급액'].sum() / 1e8
df_junggolease_amt = df_loan_month[df_loan_month['상품구분_세부'] == '중고리스']['취급액'].sum() / 1e8
df_jaego_amt = df_loan_month[df_loan_month['상품구분_세부'] == '재고금융']['취급액'].sum() / 1e8
df_junggo_total = df_junggo_amt + df_junggolease_amt + df_jaego_amt

# 사이드바에 주요 지표 미리보기 추가
st.sidebar.markdown("---")
st.sidebar.markdown(f'<span style="font-size:22px; font-weight:bold;">Summary </span>',unsafe_allow_html=True)

st.sidebar.markdown(f"""<span style="font-size:22px;"><b> - 신차 통합인수율 : </b></span> <span style="font-size:22px;"> {df_total_rate:.1f}%</span><br><span style="font-size:22px;"><b> - 신차 취급액 : </b></span> <span style="font-size:22px;"> {df_total_amt:,.0f}억원</span><br><span style="font-size:22px;"><b> - 취급중고 취급액 : </b></span> <span style="font-size:22px;"> {df_junggo_total:,.0f}억원</span>
""", unsafe_allow_html=True)

# # =====  CSS 스타일 설정 =====
# st.markdown("""
# <style>
# h2 {
#     font-size: 18px !important;
#     margin-top: 30px !important;
# }
# </style>
# """, unsafe_allow_html=True)


# === 취급지표표 ===

#=====  취급지표 표 (완전 독립 모듈) =====
st.markdown('<h2 style="font-size: 25px; margin-bottom: 0px; padding-bottom: 0px;">● 취급지표</h2>', unsafe_allow_html=True)
st.markdown('<div style="text-align: right; font-size: 15px; color: #666; margin-top: 0px; margin-bottom: 0px; padding-top: 0px; padding-bottom: 0px;">(단위: %, 억원)</div>', unsafe_allow_html=True)

# === 당월 데이터 계산 ===
df_handover_month = df_handover[df_handover['기준년월'] == selected_month]
df_halbu = df_handover_month[df_handover_month['상품구분'] == '할부']
df_imdae = df_handover_month[df_handover_month['상품구분'] == '임대']

# 신차 통합인수율 계산
df_halbu_rate = (df_halbu['인수율분자값'].sum() / df_halbu['인수율분모'].sum() * 100) if len(df_halbu) > 0 else 0
df_imdae_rate = (df_imdae['인수율분자값'].sum() / df_imdae['인수율분모'].sum() * 100) if len(df_imdae) > 0 else 0
df_total_rate = df_halbu_rate + df_imdae_rate

# 신차 취급액 계산
df_loan_month = df_loan_amt[df_loan_amt['기준년월'] == selected_month]
df_halbu_amt = df_loan_month[df_loan_month['상품구분'] == '할부']['취급액'].sum() / 1e8
df_imdae_amt = df_loan_month[df_loan_month['상품구분'] == '임대']['취급액'].sum() / 1e8
df_total_amt = df_halbu_amt + df_imdae_amt

# 중고 취급액 계산
df_junggo_amt = df_loan_month[df_loan_month['상품구분_세부'] == '중고론']['취급액'].sum() / 1e8
df_junggolease_amt = df_loan_month[df_loan_month['상품구분_세부'] == '중고리스']['취급액'].sum() / 1e8
df_jaego_amt = df_loan_month[df_loan_month['상품구분_세부'] == '재고금융']['취급액'].sum() / 1e8
df_junggo_total = df_junggo_amt + df_junggolease_amt + df_jaego_amt

# === OP 데이터 계산 ===
op_handover_month = op_handover[op_handover['bas_yrmn'] == selected_month]
op_halbu = op_handover_month[op_handover_month['product'] == '할부']
op_imdae = op_handover_month[op_handover_month['product'] == '임대']

op_halbu_rate = (op_halbu['numerator'].sum() / op_halbu['denominator'].sum() * 100) if len(op_halbu) > 0 else 0
op_imdae_rate = (op_imdae['numerator'].sum() / op_imdae['denominator'].sum() * 100) if len(op_imdae) > 0 else 0
op_total_rate = op_halbu_rate + op_imdae_rate

op_loan_month = op_loan_amt[op_loan_amt['bas_yrmn'] == selected_month]
op_halbu_amt = op_loan_month[op_loan_month['product'].isin(['할부','할부연장'])]['value'].sum()
op_imdae_amt = op_loan_month[op_loan_month['product'].isin(['임대신규','임대연장'])]['value'].sum()
op_total_amt = op_halbu_amt + op_imdae_amt

op_junggo_amt = op_loan_month[op_loan_month['product'] == '중고론']['value'].sum()
op_junggolease_amt = op_loan_month[op_loan_month['product'] == '중고리스']['value'].sum()
op_jaego_amt = op_loan_month[op_loan_month['product'] == '재고금융']['value'].sum()
op_junggo_total = op_junggo_amt + op_junggolease_amt + op_jaego_amt

# 달성률 계산
## 인수율
df_total_rate_progress = (df_total_rate / op_total_rate *100) if op_total_rate>0 else 0
df_halbu_rate_progress = (df_halbu_rate / op_halbu_rate *100) if op_halbu_rate>0 else 0
df_imdae_rate_progress = (df_imdae_rate / op_imdae_rate *100) if op_imdae_rate>0 else 0
 
## 취급액  
total_progress = (df_total_amt / op_total_amt * 100) if op_total_amt > 0 else 0
halbu_progress = (df_halbu_amt / op_halbu_amt * 100) if op_halbu_amt > 0 else 0
imdae_progress = (df_imdae_amt / op_imdae_amt * 100) if op_imdae_amt > 0 else 0
junggo_total_progress = (df_junggo_total  / op_junggo_total * 100) if op_junggo_total > 0 else 0
junggo_progress = (df_junggo_amt  / op_junggo_amt * 100) if op_junggo_amt > 0 else 0
junggolease_progress = (df_junggolease_amt  / op_junggolease_amt * 100) if op_junggolease_amt > 0 else 0
jaego_progress = (df_jaego_amt  / op_jaego_amt * 100) if op_jaego_amt > 0 else 0

# 진척비
total_wd = total_progress-100
halbu_wd = halbu_progress-100
imdae_wd = imdae_progress-100
junggo_total_wd = junggo_total_progress-100
junggo_wd = junggo_progress-100
junggolease_wd = junggolease_progress-100
jaego_wd = jaego_progress-100
 

# === 전월 데이터 계산 ===
prev_df_handover = df_handover[df_handover['기준년월'] == prev_month]
prev_halbu = prev_df_handover[prev_df_handover['상품구분'] == '할부']
prev_imdae = prev_df_handover[prev_df_handover['상품구분'] == '임대']

prev_halbu_rate = (prev_halbu['인수율분자값'].sum() / prev_halbu['인수율분모'].sum() * 100) if len(prev_halbu) > 0 else 0
prev_imdae_rate = (prev_imdae['인수율분자값'].sum() / prev_imdae['인수율분모'].sum() * 100) if len(prev_imdae) > 0 else 0
prev_total_rate = prev_halbu_rate + prev_imdae_rate

prev_df_loan = df_loan_amt[df_loan_amt['기준년월'] == prev_month]
prev_halbu_amt = prev_df_loan[prev_df_loan['상품구분'] == '할부']['취급액'].sum() / 1e8
prev_imdae_amt = prev_df_loan[prev_df_loan['상품구분'] == '임대']['취급액'].sum() / 1e8
prev_total_amt = prev_halbu_amt + prev_imdae_amt

prev_junggo_amt = prev_df_loan[prev_df_loan['상품구분_세부'] == '중고론']['취급액'].sum() / 1e8
prev_junggolease_amt = prev_df_loan[prev_df_loan['상품구분_세부'] == '중고리스']['취급액'].sum() / 1e8
prev_jaego_amt = prev_df_loan[prev_df_loan['상품구분_세부'] == '재고금융']['취급액'].sum() / 1e8
prev_junggo_total = prev_junggo_amt + prev_junggolease_amt + prev_jaego_amt

# === 누적 데이터 계산 ===
cumulative_months = [f"{selected_year}{str(i).zfill(2)}" for i in range(1, selected_month_num + 1)]

# 누적 신차 통합인수율
cumulative_op_handover = op_handover[op_handover['bas_yrmn'].isin(cumulative_months)]
cumulative_op_halbu = cumulative_op_handover[cumulative_op_handover['product'] == '할부']
cumulative_op_imdae = cumulative_op_handover[cumulative_op_handover['product'] == '임대']

cumulative_op_halbu_rate = (cumulative_op_halbu['numerator'].sum() / cumulative_op_halbu['denominator'].sum() * 100) if len(cumulative_op_halbu) > 0 else 0
cumulative_op_imdae_rate = (cumulative_op_imdae['numerator'].sum() / cumulative_op_imdae['denominator'].sum() * 100) if len(cumulative_op_imdae) > 0 else 0
cumulative_op_total_rate = cumulative_op_halbu_rate + cumulative_op_imdae_rate

cumulative_df_handover = df_handover[df_handover['기준년월'].isin(cumulative_months)]
cumulative_df_halbu = cumulative_df_handover[cumulative_df_handover['상품구분'] == '할부']
cumulative_df_imdae = cumulative_df_handover[cumulative_df_handover['상품구분'] == '임대']

cumulative_df_halbu_rate = (cumulative_df_halbu['인수율분자값'].sum() / cumulative_df_halbu['인수율분모'].sum() * 100) if len(cumulative_df_halbu) > 0 else 0
cumulative_df_imdae_rate = (cumulative_df_imdae['인수율분자값'].sum() / cumulative_df_imdae['인수율분모'].sum() * 100) if len(cumulative_df_imdae) > 0 else 0
cumulative_df_total_rate = cumulative_df_halbu_rate + cumulative_df_imdae_rate

cumulative_halbu_achievement = (cumulative_df_halbu_rate / cumulative_op_halbu_rate * 100) if cumulative_op_halbu_rate > 0 else 0
cumulative_imdae_achievement = (cumulative_df_imdae_rate / cumulative_op_imdae_rate * 100) if cumulative_op_imdae_rate > 0 else 0
cumulative_total_achievement = (cumulative_df_total_rate / cumulative_op_total_rate * 100) if cumulative_op_total_rate > 0 else 0

# 누적 신차 취급액
cumulative_op_loan = op_loan_amt[op_loan_amt['bas_yrmn'].isin(cumulative_months)]
cumulative_op_halbu_amt = cumulative_op_loan[cumulative_op_loan['product'].isin(['할부','할부연장'])]['value'].sum()
cumulative_op_imdae_amt = cumulative_op_loan[cumulative_op_loan['product'].isin(['임대신규','임대연장'])]['value'].sum()
cumulative_op_total_amt = cumulative_op_halbu_amt + cumulative_op_imdae_amt

cumulative_df_loan = df_loan_amt[df_loan_amt['기준년월'].isin(cumulative_months)]
cumulative_df_halbu_amt = cumulative_df_loan[cumulative_df_loan['상품구분'] == '할부']['취급액'].sum() / 1e8
cumulative_df_imdae_amt = cumulative_df_loan[cumulative_df_loan['상품구분'] == '임대']['취급액'].sum() / 1e8
cumulative_df_total_amt = cumulative_df_halbu_amt + cumulative_df_imdae_amt

cumulative_halbu_amt_achievement = (cumulative_df_halbu_amt / cumulative_op_halbu_amt * 100) if cumulative_op_halbu_amt > 0 else 0
cumulative_imdae_amt_achievement = (cumulative_df_imdae_amt / cumulative_op_imdae_amt * 100) if cumulative_op_imdae_amt > 0 else 0
cumulative_total_amt_achievement = (cumulative_df_total_amt / cumulative_op_total_amt * 100) if cumulative_op_total_amt > 0 else 0

# 누적 중고 취급액
cumulative_op_junggo_amt = cumulative_op_loan[cumulative_op_loan['product'] == '중고론']['value'].sum()
cumulative_op_junggolease_amt = cumulative_op_loan[cumulative_op_loan['product'] == '중고리스']['value'].sum()
cumulative_op_jaego_amt = cumulative_op_loan[cumulative_op_loan['product'] == '재고금융']['value'].sum()
cumulative_op_junggo_total = cumulative_op_junggo_amt + cumulative_op_junggolease_amt + cumulative_op_jaego_amt

cumulative_df_junggo_amt = cumulative_df_loan[cumulative_df_loan['상품구분_세부'] == '중고론']['취급액'].sum() / 1e8
cumulative_df_junggolease_amt = cumulative_df_loan[cumulative_df_loan['상품구분_세부'] == '중고리스']['취급액'].sum() / 1e8
cumulative_df_jaego_amt = cumulative_df_loan[cumulative_df_loan['상품구분_세부'] == '재고금융']['취급액'].sum() / 1e8
cumulative_df_junggo_total = cumulative_df_junggo_amt + cumulative_df_junggolease_amt + cumulative_df_jaego_amt

cumulative_junggo_total_achievement = (cumulative_df_junggo_total / cumulative_op_junggo_total * 100) if cumulative_op_junggo_total > 0 else 0
cumulative_junggo_achievement = (cumulative_df_junggo_amt / cumulative_op_junggo_amt * 100) if cumulative_op_junggo_amt > 0 else 0
cumulative_junggolease_achievement = (cumulative_df_junggolease_amt / cumulative_op_junggolease_amt * 100) if cumulative_op_junggolease_amt > 0 else 0
cumulative_jaego_achievement = (cumulative_df_jaego_amt / cumulative_op_jaego_amt * 100) if cumulative_op_jaego_amt > 0 else 0

# === 표 헤더 생성 ===
dynamic_month_header = f"당월('{year_short}.{selected_month_num}월)"
dynamic_cumulative_header = f"누적('{year_short}.1~{selected_month_num}월)"

# === 표 데이터 생성 ===
combined_data = {
    ('구분', ''): ['신차_통합인수율', '• 할부', '• 임대', '신차_취급액', '• 할부', '• 임대', '중고_취급액', '• 중고론', '• 중고리스', '• 재고금융'],
    (dynamic_month_header, 'OP'): [
        f"{op_total_rate:.1f}%", f"{op_halbu_rate:.1f}%", f"{op_imdae_rate:.1f}%",
        f"{op_total_amt:,.0f}", f"{op_halbu_amt:,.0f}", f"{op_imdae_amt:,.0f}",
        f"{op_junggo_total:,.0f}", f"{op_junggo_amt:,.0f}", f"{op_junggolease_amt:,.0f}", f"{op_jaego_amt:,.0f}"
    ],
    (dynamic_month_header, '실적'): [
        f"{df_total_rate:.1f}%", f"{df_halbu_rate:.1f}%", f"{df_imdae_rate:.1f}%",
        f"{df_total_amt:,.0f}", f"{df_halbu_amt:,.0f}", f"{df_imdae_amt:,.0f}",
        f"{df_junggo_total:,.0f}", f"{df_junggo_amt:,.0f}", f"{df_junggolease_amt:,.0f}", f"{df_jaego_amt:,.0f}"
    ],
    (dynamic_month_header, '달성률'): [
        f"{df_total_rate_progress:+.1f}%", f"{df_halbu_rate_progress:+.1f}%", f"{df_imdae_rate_progress:+.1f}%",
        f"{total_progress:+.1f}%", f"{halbu_progress:+.1f}%", f"{imdae_progress:+.1f}%",
        f"{junggo_total_progress:+.1f}%", f"{junggo_progress:+.1f}%", f"{junggolease_progress:+.1f}%", f"{jaego_progress:+.1f}%"
    ],
    (dynamic_month_header, '진척비'): [
        '-', '-', '-',
        f"{total_wd:+.1f}%", f"{halbu_wd:+.1f}%", f"{imdae_wd:+.1f}%",
        f"{junggo_total_wd:+.1f}%", f"{junggo_wd:+.1f}%", f"{junggolease_wd:+.1f}%", f"{jaego_wd:+.1f}%"
    ],
    (dynamic_month_header, '전월대비'): [
        f"{df_total_rate - prev_total_rate:+.1f}%p",
        f"{df_halbu_rate - prev_halbu_rate:+.1f}%p",
        f"{df_imdae_rate - prev_imdae_rate:+.1f}%p",
        f"{df_total_amt - prev_total_amt:+,.0f}",
        f"{df_halbu_amt - prev_halbu_amt:+,.0f}",
        f"{df_imdae_amt - prev_imdae_amt:+,.0f}",
        f"{df_junggo_total - prev_junggo_total:+,.0f}",
        f"{df_junggo_amt - prev_junggo_amt:+,.0f}",
        f"{df_junggolease_amt - prev_junggolease_amt:+,.0f}",
        f"{df_jaego_amt - prev_jaego_amt:+,.0f}"
    ],
    (dynamic_cumulative_header, '누적OP'): [
        f"{cumulative_op_total_rate:.1f}%", f"{cumulative_op_halbu_rate:.1f}%", f"{cumulative_op_imdae_rate:.1f}%",
        f"{cumulative_op_total_amt:,.0f}", f"{cumulative_op_halbu_amt:,.0f}", f"{cumulative_op_imdae_amt:,.0f}",
        f"{cumulative_op_junggo_total:,.0f}", f"{cumulative_op_junggo_amt:,.0f}", f"{cumulative_op_junggolease_amt:,.0f}", f"{cumulative_op_jaego_amt:,.0f}"
    ],
    (dynamic_cumulative_header, '누적실적'): [
        f"{cumulative_df_total_rate:.1f}%", f"{cumulative_df_halbu_rate:.1f}%", f"{cumulative_df_imdae_rate:.1f}%",
        f"{cumulative_df_total_amt:,.0f}", f"{cumulative_df_halbu_amt:,.0f}", f"{cumulative_df_imdae_amt:,.0f}",
        f"{cumulative_df_junggo_total:,.0f}", f"{cumulative_df_junggo_amt:,.0f}", f"{cumulative_df_junggolease_amt:,.0f}", f"{cumulative_df_jaego_amt:,.0f}"
    ],
    (dynamic_cumulative_header, '누적달성률'): [
        f"{cumulative_total_achievement:.1f}%", f"{cumulative_halbu_achievement:.1f}%", f"{cumulative_imdae_achievement:.1f}%",
        f"{cumulative_total_amt_achievement:.1f}%", f"{cumulative_halbu_amt_achievement:.1f}%", f"{cumulative_imdae_amt_achievement:.1f}%",
        f"{cumulative_junggo_total_achievement:.1f}%", f"{cumulative_junggo_achievement:.1f}%", f"{cumulative_junggolease_achievement:.1f}%", f"{cumulative_jaego_achievement:.1f}%"
    ]
}

# === 표 렌더링, download ===
df_display = pd.DataFrame(combined_data)
df_display.columns = pd.MultiIndex.from_tuples(df_display.columns)


st.sidebar.markdown("---")
st.sidebar.markdown(
    f'<span style="font-size:22px; font-weight:bold;"> > download summary < </span>',
    unsafe_allow_html=True)

import io
excel_buffer = io.BytesIO()
df_display.to_excel(excel_buffer, index=True)
excel_buffer.seek(0)
st.sidebar.download_button(label=f"{selected_year}년_{selected_month_num}월_취급지표",
data=excel_buffer,file_name=f"{selected_year}년_{selected_month_num}월_취급지표.xlsx",
mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


def create_custom_table_html(df):
    html = f"""
    <div style="overflow-x: auto; margin: 0px; padding: 0px;">
        <table style="width: 100%; border-collapse: collapse; border: 2px solid #2563eb; border-top: 3px solid #000000; border-bottom: 3px solid #000000; border-radius: 10px; overflow: hidden; box-shadow: 0 6px 15px rgba(0,0,0,0.15); margin: 0px;">
            <thead>
                <tr>
                    <th rowspan="2" style="background: #1e40af; color: white; font-weight: bold; font-size: 20px; text-align: center; vertical-align: middle; padding: 14px 8px; border: 2px solid #ffffff; text-shadow: 1px 1px 3px rgba(0,0,0,0.4);">구분</th>
                    <th colspan="5" style="background: #1e40af; color: white; font-weight: bold; font-size: 20px; text-align: center; vertical-align: middle; padding: 14px 8px; border: 2px solid #ffffff; text-shadow: 1px 1px 3px rgba(0,0,0,0.4);">{dynamic_month_header}</th>
                    <th colspan="3" style="background: #1e40af; color: white; font-weight: bold; font-size: 20px; text-align: center; vertical-align: middle; padding: 14px 8px; border: 2px solid #ffffff; text-shadow: 1px 1px 3px rgba(0,0,0,0.4);">{dynamic_cumulative_header}</th>
                </tr>
                <tr>
                    <th style="background: #2563eb; color: white; font-weight: bold; font-size: 20px; text-align: center; vertical-align: middle; padding: 10px 6px; border: 1px solid #ffffff;">OP</th>
                    <th style="background: #2563eb; color: white; font-weight: bold; font-size: 20px; text-align: center; vertical-align: middle; padding: 10px 6px; border: 1px solid #ffffff;">실적</th>
                    <th style="background: #2563eb; color: white; font-weight: bold; font-size: 20px; text-align: center; vertical-align: middle; padding: 10px 6px; border: 1px solid #ffffff;">달성률</th>
                    <th style="background: #2563eb; color: white; font-weight: bold; font-size: 20px; text-align: center; vertical-align: middle; padding: 10px 6px; border: 1px solid #ffffff;">진척비</th>
                    <th style="background: #2563eb; color: white; font-weight: bold; font-size: 20px; text-align: center; vertical-align: middle; padding: 10px 6px; border: 1px solid #ffffff;">전월대비</th>
                    <th style="background: #2563eb; color: white; font-weight: bold; font-size: 20px; text-align: center; vertical-align: middle; padding: 10px 6px; border: 1px solid #ffffff;">누적OP</th>
                    <th style="background: #2563eb; color: white; font-weight: bold; font-size: 20px; text-align: center; vertical-align: middle; padding: 10px 6px; border: 1px solid #ffffff;">누적실적</th>
                    <th style="background: #2563eb; color: white; font-weight: bold; font-size: 20px; text-align: center; vertical-align: middle; padding: 10px 6px; border: 1px solid #ffffff;">누적달성률</th>
                </tr>
            </thead>
            <tbody>
    """
    
    row_names = ['신차_통합인수율', '• 할부', '• 임대', '신차_취급액', '• 할부', '• 임대', '중고_취급액', '• 중고론', '• 중고리스', '• 재고금융']
    
    for i, row_name in enumerate(row_names):
        if i in [0, 3, 6]:
            row_style = "background-color: #bfdbfe; color: #1e40af; font-weight: bold;"
        else:
            row_style = "background-color: white; color: black;"
            
        html += f'<tr>'
        html += f'<td style="{row_style} text-align: center; vertical-align: middle; padding: 8px; border: 1px solid #dbeafe; font-size: 20px;">{row_name}</td>'
        
        for col_key in [(dynamic_month_header, 'OP'), (dynamic_month_header, '실적'), (dynamic_month_header, '달성률'), (dynamic_month_header, '진척비'), (dynamic_month_header, '전월대비'), (dynamic_cumulative_header, '누적OP'), (dynamic_cumulative_header, '누적실적'), (dynamic_cumulative_header, '누적달성률')]:
            value = combined_data[col_key][i]
            html += f'<td style="{row_style} text-align: center; vertical-align: middle; padding: 8px; border: 1px solid #dbeafe; font-size: 20px;">{value}</td>'
        
        html += '</tr>'
    
    html += """
            </tbody>
        </table>
    </div>
    """
    return html

custom_table_html = create_custom_table_html(df_display)
st.markdown(custom_table_html, unsafe_allow_html=True)


# === 상품별취급액사업실별_HTML커스텀 ===

# =====  상품별 취급액(사업실별) 표 (HTML 커스텀 테이블) =====
st.markdown('<h2 style="font-size: 25px; margin-bottom: 0px; padding-bottom: 0px;">● 상품별 취급액</h2>', unsafe_allow_html=True)
st.markdown('<div style="text-align: right; font-size: 15px; color: #666; margin-top: 0px; margin-bottom: 0px; padding-top: 0px; padding-bottom: 0px;">(단위: %, 억원)</div>', unsafe_allow_html=True)

op_loan_amt.insert(0, '구분1' ,np.where(op_loan_amt['product'].isin(['중고론', '중고리스', '재고금융']), '중고','신차'))
op_loan_amt.insert(1 ,'구분2' ,np.where(op_loan_amt['product'].isin(['할부', '할부연장']), '할부',
                                  np.where(op_loan_amt['product'].isin(['임대신규', '임대연장']), '임대',op_loan_amt['product'])))
op_loan_amt.insert(2 ,'구분3' ,np.where(op_loan_amt['product'].isin(['임대신규','임대연장']), op_loan_amt['product'], op_loan_amt['depart']))
op_loan_amt.insert(3 ,'구분4' ,op_loan_amt['depart'])
df_loan_amt.insert(0, '구분1' ,np.where(df_loan_amt['상품구분'].isin(['할부', '임대']), '신차','중고'))
df_loan_amt.insert(1 ,'구분2' ,np.where(df_loan_amt['상품구분'].isin(['중고']), df_loan_amt['상품구분_세부'], df_loan_amt['상품구분']))
df_loan_amt.insert(2 ,'구분3' ,np.where(df_loan_amt['상품구분'].isin(['임대']), df_loan_amt['상품구분_세부'], df_loan_amt['부서']))
df_loan_amt.insert(3 ,'구분4' ,df_loan_amt['부서'])

groups = ['구분1', '구분2', '구분3', '구분4']
def custom_sort_key(row):
    구분1 = row['구분1']
    구분2 = row['구분2']
    구분3 = row['구분3']
    구분4 = row['구분4']
    if 구분1 == '신차':
        sort1 = 0
    else: 
        sort1 = 1

    if 구분2 == '할부':
        sort2 = 0
    elif 구분3 == '임대신규':
        sort2 = 1
    elif 구분3 == '임대연장':
        sort2 = 2   
    elif 구분2 == '중고론':
        sort2 = 3
    elif 구분2 == '중고리스':
        sort2 = 4
    else:
        sort2 = 5

    if 구분1 == '신차' and 구분4 == '신차영업팀':
        sort3 = 0
    elif 구분1 == '신차' and 구분4 == '플랫폼영업팀':
        sort3 = 1
    elif 구분1 == '신차' and 구분4 == 'Auto법인마케팅팀':
        sort3 = 2
    elif 구분1 == '중고' and 구분4 == '중고영업팀':
        sort3 = 3
    elif 구분1 == '중고' and 구분4 == '플랫폼영업팀':
        sort3 = 4
    elif 구분1 == '중고' and 구분4 == 'Auto법인마케팅팀':
        sort3 = 5   

    return (sort1, sort2, sort3)


# === 당월 데이터 계산 ===
current_loan_data = df_loan_amt[df_loan_amt['기준년월'] == selected_month].groupby(groups)['취급액'].sum().reset_index()
current_loan_data['sort_key'] = current_loan_data.apply(custom_sort_key, axis=1)
current_loan_data = current_loan_data.sort_values('sort_key').drop('sort_key', axis=1)


신차_취급액_합 = current_loan_data[current_loan_data['구분1'] == '신차']['취급액'].sum() if '구분1' in current_loan_data.columns else None
row = ['신차', 'total', 'total', 'total', 신차_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','취급액'])
current_loan_data = pd.concat([row_df, current_loan_data], ignore_index=True)

중고_취급액_합 = current_loan_data[current_loan_data['구분1'] == '중고']['취급액'].sum() if '구분1' in current_loan_data.columns else None
row = ['중고', 'total', 'total', 'total', 중고_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','취급액'])
current_loan_data = pd.concat([current_loan_data[:10],row_df, current_loan_data[10:]], ignore_index=True)

임대_취급액_합 = current_loan_data[current_loan_data['구분2'] == '임대']['취급액'].sum() if '구분2' in current_loan_data.columns else None
row = ['신차', '임대', 'total', 'total', 임대_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','취급액'])
current_loan_data = pd.concat([current_loan_data[:4],row_df, current_loan_data[4:]], ignore_index=True)


임대신규_취급액_합 = current_loan_data[current_loan_data['구분3'] == '임대신규']['취급액'].sum() if '구분3' in current_loan_data.columns else None
row = ['신차', '임대', '임대신규', 'total', 임대신규_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','취급액'])
current_loan_data = pd.concat([current_loan_data[:5],row_df, current_loan_data[5:]], ignore_index=True)


임대연장_취급액_합 = current_loan_data[current_loan_data['구분3'] == '임대연장']['취급액'].sum() if '구분3' in current_loan_data.columns else None
row = ['신차', '임대', '임대연장', 'total', 임대연장_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','취급액'])
current_loan_data = pd.concat([current_loan_data[:9],row_df, current_loan_data[9:]], ignore_index=True)

#7.24 추가 
할부_취급액_합 = current_loan_data[current_loan_data['구분2'] == '할부']['취급액'].sum() if '구분2' in current_loan_data.columns else None
row = ['신차', '할부', 'total', 'total', 할부_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','취급액'])
current_loan_data = pd.concat([current_loan_data[:1],row_df, current_loan_data[1:]], ignore_index=True)


# 당월 OP 데이터와 병합
current_op_result = op_loan_amt[op_loan_amt['bas_yrmn'] == selected_month].groupby(groups)['value'].sum().reset_index()
current_op_result['sort_key'] = current_op_result.apply(custom_sort_key, axis=1)
current_op_result = current_op_result.sort_values('sort_key').drop('sort_key', axis=1)
current_op_result.drop(columns=['bas_yrmn', 'product','depart'], inplace=True, errors='ignore')

신차_취급액_합 = current_op_result[current_op_result['구분1'] == '신차']['value'].sum() if '구분1' in current_op_result.columns else None
row = ['신차', 'total', 'total', 'total', 신차_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','value'])
current_op_result = pd.concat([row_df, current_op_result], ignore_index=True)

중고_취급액_합 = current_op_result[current_op_result['구분1'] == '중고']['value'].sum() if '구분1' in current_op_result.columns else None
row = ['중고', 'total', 'total', 'total', 중고_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','value'])
current_op_result = pd.concat([current_op_result[:10],row_df, current_op_result[10:]], ignore_index=True)


임대_취급액_합 = current_op_result[current_op_result['구분2'] == '임대']['value'].sum() if '구분2' in current_op_result.columns else None
row = ['신차', '임대', 'total', 'total', 임대_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','value'])
current_op_result = pd.concat([current_op_result[:4],row_df, current_op_result[4:]], ignore_index=True)


임대신규_취급액_합 = current_op_result[current_op_result['구분3'] == '임대신규']['value'].sum() if '구분3' in current_op_result.columns else None
row = ['신차', '임대', '임대신규', 'total', 임대신규_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','value'])
current_op_result = pd.concat([current_op_result[:5],row_df, current_op_result[5:]], ignore_index=True)


임대연장_취급액_합 = current_op_result[current_op_result['구분3'] == '임대연장']['value'].sum() if '구분3' in current_op_result.columns else None
row = ['신차', '임대', '임대연장', 'total', 임대연장_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','value'])
current_op_result = pd.concat([current_op_result[:9],row_df, current_op_result[9:]], ignore_index=True)
current_op_result.drop(columns=['bas_yrmn', 'product','depart'], inplace=True, errors='ignore')

#7.24 추가
할부_취급액_합 = current_op_result[current_op_result['구분2'] == '할부']['value'].sum() if '구분2' in current_op_result.columns else None
row = ['신차', '할부', 'total', 'total', 할부_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','value'])
current_op_result = pd.concat([current_op_result[:1],row_df, current_op_result[1:]], ignore_index=True)
current_op_result.drop(columns=['bas_yrmn', 'product','depart'], inplace=True, errors='ignore')


current_loan_result = pd.merge(current_loan_data, current_op_result, 
   left_on=['구분1','구분2','구분3','구분4'], right_on=['구분1','구분2','구분3','구분4'], 
   how='inner').rename(columns={'취급액': '취급액', 'value': 'OP_취급액'}).reset_index(drop=True)


# === 전월 데이터 계산 ===
prev_loan_data = df_loan_amt[df_loan_amt['기준년월'] == prev_month].groupby(groups)['취급액'].sum().reset_index()
prev_loan_data['sort_key'] = prev_loan_data.apply(custom_sort_key, axis=1)
prev_loan_data = prev_loan_data.sort_values('sort_key').drop('sort_key', axis=1)


신차_취급액_합 = prev_loan_data[prev_loan_data['구분1'] == '신차']['취급액'].sum() if '구분1' in prev_loan_data.columns else None
row = ['신차', 'total', 'total', 'total', 신차_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','취급액'])
prev_loan_data = pd.concat([row_df, prev_loan_data], ignore_index=True)

중고_취급액_합 = prev_loan_data[prev_loan_data['구분1'] == '중고']['취급액'].sum() if '구분1' in prev_loan_data.columns else None
row = ['중고', 'total', 'total', 'total', 중고_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','취급액'])
prev_loan_data = pd.concat([prev_loan_data[:10],row_df, prev_loan_data[10:]], ignore_index=True)

임대_취급액_합 = prev_loan_data[prev_loan_data['구분2'] == '임대']['취급액'].sum() if '구분2' in prev_loan_data.columns else None
row = ['신차', '임대', 'total', 'total', 임대_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','취급액'])
prev_loan_data = pd.concat([prev_loan_data[:4],row_df, prev_loan_data[4:]], ignore_index=True)


임대신규_취급액_합 = prev_loan_data[prev_loan_data['구분3'] == '임대신규']['취급액'].sum() if '구분3' in prev_loan_data.columns else None
row = ['신차', '임대', '임대신규', 'total', 임대신규_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','취급액'])
prev_loan_data = pd.concat([prev_loan_data[:5],row_df, prev_loan_data[5:]], ignore_index=True)


임대연장_취급액_합 = prev_loan_data[prev_loan_data['구분3'] == '임대연장']['취급액'].sum() if '구분3' in prev_loan_data.columns else None
row = ['신차', '임대', '임대연장', 'total', 임대연장_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','취급액'])
prev_loan_data = pd.concat([prev_loan_data[:9],row_df, prev_loan_data[9:]], ignore_index=True)

#7.24 추가 
할부_취급액_합 = prev_loan_data[prev_loan_data['구분2'] == '할부']['취급액'].sum() if '구분2' in prev_loan_data.columns else None
row = ['신차', '할부', 'total', 'total', 할부_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','취급액'])
prev_loan_data = pd.concat([prev_loan_data[:1],row_df, prev_loan_data[1:]], ignore_index=True)

# # 전월 OP 데이터와 병합
prev_op_result = op_loan_amt[op_loan_amt['bas_yrmn'] == prev_month].groupby(groups)['value'].sum().reset_index()
prev_op_result['sort_key'] = prev_op_result.apply(custom_sort_key, axis=1)
prev_op_result = prev_op_result.sort_values('sort_key').drop('sort_key', axis=1)
prev_op_result.drop(columns=['bas_yrmn', 'product','depart'], inplace=True, errors='ignore')

신차_취급액_합 = prev_op_result[prev_op_result['구분1'] == '신차']['value'].sum() if '구분1' in prev_op_result.columns else None
row = ['신차', 'total', 'total', 'total', 신차_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','value'])
prev_op_result = pd.concat([row_df, prev_op_result], ignore_index=True)

중고_취급액_합 = prev_op_result[prev_op_result['구분1'] == '중고']['value'].sum() if '구분1' in prev_op_result.columns else None
row = ['중고', 'total', 'total', 'total', 중고_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','value'])
prev_op_result = pd.concat([prev_op_result[:10],row_df, prev_op_result[10:]], ignore_index=True)


임대_취급액_합 = prev_op_result[prev_op_result['구분2'] == '임대']['value'].sum() if '구분2' in prev_op_result.columns else None
row = ['신차', '임대', 'total', 'total', 임대_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','value'])
prev_op_result = pd.concat([prev_op_result[:4],row_df, prev_op_result[4:]], ignore_index=True)


임대신규_취급액_합 = prev_op_result[prev_op_result['구분3'] == '임대신규']['value'].sum() if '구분3' in prev_op_result.columns else None
row = ['신차', '임대', '임대신규', 'total', 임대신규_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','value'])
prev_op_result = pd.concat([prev_op_result[:5],row_df, prev_op_result[5:]], ignore_index=True)


임대연장_취급액_합 = prev_op_result[prev_op_result['구분3'] == '임대연장']['value'].sum() if '구분3' in prev_op_result.columns else None
row = ['신차', '임대', '임대연장', 'total', 임대연장_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','value'])
prev_op_result = pd.concat([prev_op_result[:9],row_df, prev_op_result[9:]], ignore_index=True)
prev_op_result.drop(columns=['bas_yrmn', 'product','depart'], inplace=True, errors='ignore')

#7.24 추가 
할부_취급액_합 = prev_op_result[prev_op_result['구분3'] == '할부']['value'].sum() if '구분2' in prev_op_result.columns else None
row = ['신차', '할부', 'total', 'total', 할부_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','value'])
prev_op_result = pd.concat([prev_op_result[:9],row_df, prev_op_result[9:]], ignore_index=True)
prev_op_result.drop(columns=['bas_yrmn', 'product','depart'], inplace=True, errors='ignore')


prev_loan_result = pd.merge(prev_loan_data, prev_op_result, 
   left_on=['구분1','구분2','구분3','구분4'], right_on=['구분1','구분2','구분3','구분4'], 
   how='inner').rename(columns={'취급액': '취급액', 'value': 'OP_취급액'}).reset_index(drop=True)

# === 누적 데이터 계산 ===
cumulative_months = [f"{selected_year}{str(i).zfill(2)}" for i in range(1, selected_month_num + 1)]

cumulative_loan_data = df_loan_amt[df_loan_amt['기준년월'].isin(cumulative_months)].groupby(groups)['취급액'].sum().reset_index()
cumulative_loan_data['sort_key'] = cumulative_loan_data.apply(custom_sort_key, axis=1)
cumulative_loan_data = cumulative_loan_data.sort_values('sort_key').drop('sort_key', axis=1)


신차_취급액_합 = cumulative_loan_data[cumulative_loan_data['구분1'] == '신차']['취급액'].sum() if '구분1' in cumulative_loan_data.columns else None
row = ['신차', 'total', 'total', 'total', 신차_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','취급액'])
cumulative_loan_data = pd.concat([row_df, cumulative_loan_data], ignore_index=True)

중고_취급액_합 = cumulative_loan_data[cumulative_loan_data['구분1'] == '중고']['취급액'].sum() if '구분1' in cumulative_loan_data.columns else None
row = ['중고', 'total', 'total', 'total', 중고_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','취급액'])
cumulative_loan_data = pd.concat([cumulative_loan_data[:10],row_df, cumulative_loan_data[10:]], ignore_index=True)

임대_취급액_합 = cumulative_loan_data[cumulative_loan_data['구분2'] == '임대']['취급액'].sum() if '구분2' in cumulative_loan_data.columns else None
row = ['신차', '임대', 'total', 'total', 임대_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','취급액'])
cumulative_loan_data = pd.concat([cumulative_loan_data[:4],row_df, cumulative_loan_data[4:]], ignore_index=True)


임대신규_취급액_합 = cumulative_loan_data[cumulative_loan_data['구분3'] == '임대신규']['취급액'].sum() if '구분3' in cumulative_loan_data.columns else None
row = ['신차', '임대', '임대신규', 'total', 임대신규_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','취급액'])
cumulative_loan_data = pd.concat([cumulative_loan_data[:5],row_df, cumulative_loan_data[5:]], ignore_index=True)


임대연장_취급액_합 = cumulative_loan_data[cumulative_loan_data['구분3'] == '임대연장']['취급액'].sum() if '구분3' in cumulative_loan_data.columns else None
row = ['신차', '임대', '임대연장', 'total', 임대연장_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','취급액'])
cumulative_loan_data = pd.concat([cumulative_loan_data[:9],row_df, cumulative_loan_data[9:]], ignore_index=True)

#7.24 추가 
할부_취급액_합 = cumulative_loan_data[cumulative_loan_data['구분2'] == '할부']['취급액'].sum() if '구분2' in cumulative_loan_data.columns else None
row = ['신차', '할부', 'total', 'total', 할부_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','취급액'])
cumulative_loan_data = pd.concat([cumulative_loan_data[:1],row_df, cumulative_loan_data[1:]], ignore_index=True)


# # 누적 OP 데이터와 병합
cumulative_op_result= op_loan_amt[op_loan_amt['bas_yrmn'].isin(cumulative_months)].groupby(groups)['value'].sum().reset_index()
cumulative_op_result['sort_key'] = cumulative_op_result.apply(custom_sort_key, axis=1)


cumulative_op_result= cumulative_op_result.sort_values('sort_key').drop('sort_key', axis=1)
cumulative_op_result.drop(columns=['bas_yrmn', 'product','depart'], inplace=True, errors='ignore')

신차_취급액_합 = cumulative_op_result[cumulative_op_result['구분1'] == '신차']['value'].sum() if '구분1' in cumulative_op_result.columns else None
row = ['신차', 'total', 'total', 'total', 신차_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','value'])
cumulative_op_result= pd.concat([row_df, cumulative_op_result], ignore_index=True)

중고_취급액_합 = cumulative_op_result[cumulative_op_result['구분1'] == '중고']['value'].sum() if '구분1' in cumulative_op_result.columns else None
row = ['중고', 'total', 'total', 'total', 중고_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','value'])
cumulative_op_result= pd.concat([cumulative_op_result[:10],row_df, cumulative_op_result[10:]], ignore_index=True)


임대_취급액_합 = cumulative_op_result[cumulative_op_result['구분2'] == '임대']['value'].sum() if '구분2' in cumulative_op_result.columns else None
row = ['신차', '임대', 'total', 'total', 임대_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','value'])
cumulative_op_result= pd.concat([cumulative_op_result[:4],row_df, cumulative_op_result[4:]], ignore_index=True)


임대신규_취급액_합 = cumulative_op_result[cumulative_op_result['구분3'] == '임대신규']['value'].sum() if '구분3' in cumulative_op_result.columns else None
row = ['신차', '임대', '임대신규', 'total', 임대신규_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','value'])
cumulative_op_result= pd.concat([cumulative_op_result[:5],row_df, cumulative_op_result[5:]], ignore_index=True)


임대연장_취급액_합 = cumulative_op_result[cumulative_op_result['구분3'] == '임대연장']['value'].sum() if '구분3' in cumulative_op_result.columns else None
row = ['신차', '임대', '임대연장', 'total', 임대연장_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','value'])
cumulative_op_result= pd.concat([cumulative_op_result[:9],row_df, cumulative_op_result[9:]], ignore_index=True)
cumulative_op_result.drop(columns=['bas_yrmn', 'product','depart'], inplace=True, errors='ignore')

#7.24 추가 
할부_취급액_합 = cumulative_op_result[cumulative_op_result['구분2'] == '할부']['value'].sum() if '구분2' in cumulative_op_result.columns else None
row = ['신차', '할부', 'total', 'total', 할부_취급액_합]
row_df = pd.DataFrame([row], columns=['구분1','구분2','구분3','구분4','value'])
cumulative_op_result = pd.concat([cumulative_op_result[:1],row_df, cumulative_op_result[1:]], ignore_index=True)
cumulative_op_result.drop(columns=['bas_yrmn', 'product','depart'], inplace=True, errors='ignore')


cumulative_loan_result = pd.merge(cumulative_loan_data, cumulative_op_result, 
   left_on=['구분1','구분2','구분3','구분4'], right_on=['구분1','구분2','구분3','구분4'], 
   how='inner').rename(columns={'취급액': '취급액', 'value': 'OP_취급액'}).reset_index(drop=True)

new=['신차','할부','할부 - 신차영업팀','할부 - 플랫폼영업팀','할부 - Auto법인마케팅팀','임대','임대신규','신차영업팀','플랫폼영업팀','Auto법인마케팅팀',
'임대연장','신차영업팀','플랫폼영업팀','Auto법인마케팅팀','중고','중고론 - 중고영업팀','중고론 - 플랫폼영업팀','중고론 - Auto법인마케팅팀',
'중고리스 - 중고영업팀','중고리스 - 플랫폼영업팀','중고리스 - Auto법인마케팅팀','재고금융 - 중고영업팀']
current_loan_result.insert(0,'구분',new)
prev_loan_result.insert(0,'구분',new)
cumulative_loan_result.insert(0,'구분',new)

    

def create_product_loan_table_data():
    table_rows = []

    for idx, row in current_loan_result.iterrows():
        전월_data = prev_loan_result.iloc[idx]
        누적_data = cumulative_loan_result.iloc[idx]

        # 당월 데이터
        당월_실적 = row['취급액'] / 1e8
        당월_OP = row['OP_취급액']
        당월_달성률 = (당월_실적 / 당월_OP * 100) if 당월_OP > 0 else 0

        # 전월 데이터
        if 전월_data is not None:
            전월_실적 = 전월_data['취급액'] / 1e8
            전월대비 = 당월_실적 - 전월_실적
        else:
            전월대비 = 0

        # 누적 데이터
        if 누적_data is not None:
            누적_실적 = 누적_data['취급액'] / 1e8
            누적_OP = 누적_data['OP_취급액']
            누적_달성률 = (누적_실적 / 누적_OP * 100) if 누적_OP > 0 else 0
        else:
            누적_실적 = 당월_실적
            누적_OP = 당월_OP
            누적_달성률 = 당월_달성률

        table_rows.append([
            row['구분'],
            f"{당월_OP:,.2f}",
            f"{당월_실적:,.2f}",
            f"{당월_달성률:.2f}%",
            f"{전월대비:+,.2f}",
            f"{누적_OP:,.2f}",
            f"{누적_실적:,.2f}",
            f"{누적_달성률:.2f}%"
        ])

    return table_rows
    
dynamic_month_header = f"당월('{year_short}.{selected_month_num}월)"
dynamic_cumulative_header = f"누적('{year_short}.1~{selected_month_num}월)"
table_data = create_product_loan_table_data()    
df_table_data =pd.DataFrame(table_data,columns=['구분','당월_OP','당월_실적','당월_달성률','전월대비','누적_OP','누적_실적','누적_달성률'])


excel_buffer = io.BytesIO()
df_table_data.to_excel(excel_buffer, index=True)
excel_buffer.seek(0)
st.sidebar.download_button(label=f"{selected_year}년_{selected_month_num}월_상품별취급액",
data=excel_buffer,
file_name=f"{selected_year}년_{selected_month_num}월_상품별취급액.xlsx",
mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


st.sidebar.markdown("---")
# st.sidebar.markdown(
#     f'<span style="font-size:22px; font-weight:bold;">📥 download source(not yet) </span>',
#     unsafe_allow_html=True)



#=== 모든 셀에 구분별 스타일을 적용하는 커스텀 테이블 함수 ===
def create_product_loan_custom_table_html_fullstyle(data):
    html = f"""
    <div style="overflow-x: auto; margin: 0px; padding: 0px;">
        <table style="width: 100%; border-collapse: collapse; border: 2px solid #2563eb; border-top: 3px solid #000000; border-bottom: 3px solid #000000; border-radius: 10px; overflow: hidden; box-shadow: 0 6px 15px rgba(0,0,0,0.15); margin: 0px;">
            <thead>
                <tr>
                    <th rowspan="2" style="background: #1e40af; color: white; font-weight: bold; font-size: 20px; text-align: center; vertical-align: middle; padding: 14px 8px; border: 2px solid #ffffff; text-shadow: 1px 1px 3px rgba(0,0,0,0.4);">구분</th>
                    <th colspan="4" style="background: #1e40af; color: white; font-weight: bold; font-size: 20px; text-align: center; vertical-align: middle; padding: 14px 8px; border: 2px solid #ffffff; text-shadow: 1px 1px 3px rgba(0,0,0,0.4);">{dynamic_month_header}</th>
                    <th colspan="3" style="background: #1e40af; color: white; font-weight: bold; font-size: 20px; text-align: center; vertical-align: middle; padding: 14px 8px; border: 2px solid #ffffff; text-shadow: 1px 1px 3px rgba(0,0,0,0.4);">{dynamic_cumulative_header}</th>
                </tr>
                <tr>
                    <th style="background: #2563eb; color: white; font-weight: bold; font-size: 20x; text-align: center; vertical-align: middle; padding: 10px 6px; border: 1px solid #ffffff;">OP</th>
                    <th style="background: #2563eb; color: white; font-weight: bold; font-size: 20px; text-align: center; vertical-align: middle; padding: 10px 6px; border: 1px solid #ffffff;">실적</th>
                    <th style="background: #2563eb; color: white; font-weight: bold; font-size: 20px; text-align: center; vertical-align: middle; padding: 10px 6px; border: 1px solid #ffffff;">달성률</th>
                    <th style="background: #2563eb; color: white; font-weight: bold; font-size: 20px; text-align: center; vertical-align: middle; padding: 10px 6px; border: 1px solid #ffffff;">전월대비</th>
                    <th style="background: #2563eb; color: white; font-weight: bold; font-size: 20px; text-align: center; vertical-align: middle; padding: 10px 6px; border: 1px solid #ffffff;">OP</th>
                    <th style="background: #2563eb; color: white; font-weight: bold; font-size: 20px; text-align: center; vertical-align: middle; padding: 10px 6px; border: 1px solid #ffffff;">실적</th>
                    <th style="background: #2563eb; color: white; font-weight: bold; font-size: 20px; text-align: center; vertical-align: middle; padding: 10px 6px; border: 1px solid #ffffff;">달성률</th>
                </tr>
            </thead>
            <tbody>
    """
    for i, row in enumerate(data):
        구분 = row[0]
        # subtotal 스타일 지정
        if 구분 in ['신차', '중고']:  
            cell_style = "background-color: #bfdbfe; color: #1e40af; font-weight: bold; text-align: center;"
        elif 구분 in ['할부', '임대']:
            cell_style = "background-color: #e0f2fe; color: #60a5fa; font-weight: bold; text-align: center;"
        elif 구분 in ['임대신규', '임대연장']:
            cell_style = "background-color: #f0f9ff; color: black; font-weight: bold; text-align: center;"
        else:
            cell_style = "background-color: white; color: black; font-weight: normal; text-align: center;"
        html += f'<tr>'

        for j in range(len(row)):
            html += f'<td style="{cell_style} vertical-align: middle; padding: 8px; border: 1px solid #dbeafe; font-size: 20px;">{row[j]}</td>'
        

        html += '</tr>'
    html += """
            </tbody>
        </table>
    </div>
    """
    return html

# # # === 표 렌더링 예시 ===
custom_product_table_html_fullstyle = create_product_loan_custom_table_html_fullstyle(table_data)
st.markdown(custom_product_table_html_fullstyle, unsafe_allow_html=True)


