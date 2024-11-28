import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import requests
import os

# GitHub 레포지토리 URL 설정
GITHUB_BASE_URL = "https://raw.githubusercontent.com/cdshadow/one_person/main/"

# Streamlit 애플리케이션 설정
st.title("Shapefile Viewer from GitHub with CRS Conversion")

# 파일 다운로드 및 로드 함수
@st.cache_data
def download_and_load_shapefile(file_name):
    # 파일 URL 생성
    file_url = f"{GITHUB_BASE_URL}{file_name}"
    
    # 파일 다운로드
    local_file = f"./{file_name}"
    response = requests.get(file_url)
    if response.status_code == 200:
        with open(local_file, "wb") as f:
            f.write(response.content)
    else:
        st.error(f"Failed to download {file_name}. Check the file path or GitHub repository.")
        return None

    # GeoPandas로 Shapefile 읽기
    gdf = gpd.read_file(local_file)

    # 다운로드된 파일 정리
    os.remove(local_file)
    return gdf

# 좌표계 변환 함수
def transform_crs(gdf):
    # 현재 좌표계 확인
    current_crs = gdf.crs
    st.sidebar.write(f"Current CRS: {current_crs}")
    
    # 좌표계를 EPSG:4326으로 변환
    if current_crs != "EPSG:4326":
        gdf = gdf.to_crs(epsg=4326)
        st.sidebar.write("Transformed to CRS: EPSG:4326")
    else:
        st.sidebar.write("Already in CRS: EPSG:4326")
    return gdf

# Shapefile 파일 선택
st.sidebar.title("Shapefile Files")
available_files = ["one_person.shp", "daejoen.shp"]
selected_file = st.sidebar.selectbox("Select a Shapefile", available_files)

if selected_file:
    # Shapefile 로드 및 좌표계 변환
    gdf = download_and_load_shapefile(selected_file)
    if gdf is not None:
        gdf = transform_crs(gdf)
        
        # Shapefile 데이터 요약 정보
        st.subheader(f"{selected_file} - Metadata")
        st.write(gdf.head())
        
        # 지도 시각화
        st.subheader("Map View")
        centroid = gdf.geometry.centroid
        if not centroid.is_empty.all():
            map_center = [centroid.y.mean(), centroid.x.mean()]
        else:
            map_center = [36.35, 127.38]  # 대전 임의 중심
        
        m = folium.Map(location=map_center, zoom_start=12)
        folium.GeoJson(gdf).add_to(m)
        st_folium(m, width=700, height=500)
