import streamlit as st
import pandas as pd
import numpy as np

# 웹앱 제목 및 설명 설정
st.title('지난 110년간의 기온 변화 분석')
st.write('가지고 계신 기온 데이터(csv)를 업로드해주세요.')

# 1. 파일 업로더 기능 추가 (GitHub 용량 제한 해결)
uploaded_file = st.file_uploader("여기를 클릭하여 temp.csv 파일을 업로드하세요", type=['csv'])

# 데이터 로드 함수
@st.cache_data
def load_data(file):
    # 파일 포인터 위치 초기화 (인코딩 재시도 등을 위해)
    file.seek(0)
    try:
        df = pd.read_csv(file, encoding='utf-8')
    except UnicodeDecodeError:
        file.seek(0)
        df = pd.read_csv(file, encoding='cp949')
    
    # 날짜 컬럼의 공백 및 특수문자 제거
    df['날짜'] = df['날짜'].astype(str).str.strip()
    
    # 날짜를 datetime 형식으로 변환
    df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
    
    # 기온 데이터가 없는 행 제거
    df = df.dropna(subset=['평균기온(℃)'])
    
    # 연도 컬럼 추가
    df['Year'] = df['날짜'].dt.year
    return df

# 2. 파일이 업로드 되었을 때만 분석 실행
if uploaded_file is not None:
    try:
        df = load_data(uploaded_file)

        # 연도별 평균 기온 계산
        annual_mean = df.groupby('Year')['평균기온(℃)'].mean()

        # 추세선 계산 (1차 함수: y = ax + b)
        z = np.polyfit(annual_mean.index, annual_mean.values, 1)
        p = np.poly1d(z)
        
        # 추세선 데이터 생성
        trend_line = p(annual_mean.index)

        # 시각화를 위한 데이터프레임 생성
        chart_data = pd.DataFrame({
            '실제 연평균 기온': annual_mean,
            '기온 상승 추세선': trend_line
        })

        # 라인 차트 그리기
        st.line_chart(chart_data)

        # 분석 결과 텍스트 출력
        start_year = annual_mean.index.min()
        end_year = annual_mean.index.max()
        temp_change = p(end_year) - p(start_year)
        slope = z[0]

        st.subheader('분석 결과')
        st.write(f"분석 기간: {start_year}년 ~ {end_year}년")
        st.write(f"이 기간 동안 추세적으로 기온은 약 {temp_change:.2f}도 상승했습니다.")
        
        if slope > 0:
            st.success("데이터 분석 결과, 지난 110년 동안 명확한 기온 상승 경향이 확인됩니다.")
        else:
            st.info("데이터 분석 결과, 뚜렷한 기온 상승 경향이 보이지 않습니다.")

    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
else:
    st.info("파일을 업로드하면 분석 결과가 나타납니다.")
