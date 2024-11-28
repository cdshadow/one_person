import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium

# Streamlit 애플리케이션 설정
st.title("Shapefile Viewer with Coordinate System Conversion")

# Shapefile 파일 로드 및 좌표계 변환
@st.cache_data
def load_and_transform_shapefile(file_path):
    # Shapefile 로드
    gdf = gpd.read_file(file_path)
    
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

# 업로드된 파일 표시
st.sidebar.title("Shapefile Files")
uploaded_files = {
    "One Person (one_person.shp)": "one_person.shp",
    "Daejeon (daejoen.shp)": "daejoen.shp"
}

selected_file = st.sidebar.selectbox("Select a Shapefile", list(uploaded_files.keys()))

if selected_file:
    file_path = uploaded_files[selected_file]
    gdf = load_and_transform_shapefile(file_path)
    
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
