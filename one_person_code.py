import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium

# 데이터 경로
file_paths = {
    "대전 경계선": 'https://raw.githubusercontent.com/cdshadow/facility/main/daejeon_line.shp',
    "1인 가구 격자": 'https://raw.githubusercontent.com/cdshadow/facility/main/one_person_grid.shp',
}

# 마커 색상 설정 (폴리곤의 색상과 투명도 포함)
layer_styles = {
    "대전 경계선": {"color": "blue", "weight": 2, "fill_color": "lightblue", "fill_opacity": 0.2},
    "1인 가구 격자": {"color": "green", "weight": 1, "fill_color": "lightgreen", "fill_opacity": 0.4},
}

# Streamlit 설정
st.set_page_config(layout="wide")

# Folium 지도 생성 함수
def create_map():
    # Folium 지도 설정 (대전광역시 중심)
    map_obj = folium.Map(
        location=[36.3504, 127.3845],
        zoom_start=12,
    )

    # 파일 추가
    for name, path in file_paths.items():
        try:
            if path.endswith('.shp'):
                # 쉐이프파일 처리
                gdf = gpd.read_file(path)
                gdf = gdf.to_crs(epsg=4326)  # 좌표계 변환

                # FeatureGroup 생성
                feature_group = folium.FeatureGroup(name=name)

                # 각 지오메트리를 지도에 추가
                for _, row in gdf.iterrows():
                    # 폴리곤과 라인 처리
                    if row.geometry.geom_type in ["Polygon", "MultiPolygon"]:
                        folium.GeoJson(
                            row.geometry,
                            style_function=lambda x, s=layer_styles.get(name, {}): s,
                            tooltip=folium.GeoJsonTooltip(fields=list(gdf.columns), aliases=list(gdf.columns)),
                        ).add_to(feature_group)
                    elif row.geometry.geom_type in ["LineString", "MultiLineString"]:
                        folium.GeoJson(
                            row.geometry,
                            style_function=lambda x, s=layer_styles.get(name, {}): s,
                            tooltip=folium.GeoJsonTooltip(fields=list(gdf.columns), aliases=list(gdf.columns)),
                        ).add_to(feature_group)

                # FeatureGroup을 지도에 추가
                feature_group.add_to(map_obj)
            else:
                st.error(f"지원되지 않는 파일 형식입니다: {path}")
        except Exception as e:
            st.error(f"{name} 데이터를 불러오는 중 오류가 발생했습니다: {e}")

    # 레이어 컨트롤 추가
    folium.LayerControl(position='topleft').add_to(map_obj)

    return map_obj

# Streamlit 레이아웃 설정
st.title('대전광역시 지도 시각화')

# 지도 생성 및 출력
map_display = create_map()
st_folium(map_display, width=1200, height=700)
