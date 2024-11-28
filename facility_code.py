import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium

# 데이터 경로
file_paths = {
    "대전 경계선": 'https://raw.githubusercontent.com/cdshadow/facility/main/daejeon_line.shp',
    "1인 가구 그리드": 'https://raw.githubusercontent.com/cdshadow/facility/main/one_person_grid.shp',
}

# 마커 색상 및 스타일 설정
layer_styles = {
    "대전 경계선": {"color": "blue", "weight": 2},  # 라인 스타일
    "1인 가구 그리드": {"color": "green", "fill_opacity": 0.5},  # 폴리곤 스타일
}

# Streamlit 설정
st.set_page_config(layout="wide")

# Folium 지도 생성 함수
def create_map():
    # Folium 지도 설정 (대전광역시 중심)
    map_obj = folium.Map(
        location=[36.3504, 127.3845],
        zoom_start=12,  # 줌 레벨 조정
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

                # 파일에 따라 다르게 처리
                if name == "대전 경계선":
                    # LineString 또는 MultiLineString 처리
                    for _, row in gdf.iterrows():
                        folium.PolyLine(
                            locations=[list(coord[::-1]) for coord in row.geometry.coords],
                            color=layer_styles[name]["color"],
                            weight=layer_styles[name]["weight"],
                        ).add_to(feature_group)
                elif name == "1인 가구 그리드":
                    # Polygon 또는 MultiPolygon 처리
                    for _, row in gdf.iterrows():
                        folium.GeoJson(
                            data=row.geometry,
                            style_function=lambda x: layer_styles[name],
                            tooltip="Grid 정보",
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
st.title('대전광역시 데이터 지도')

# 지도 생성 및 출력
map_display = create_map()
st_folium(map_display, width=1200, height=700)
