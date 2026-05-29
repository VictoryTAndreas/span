path = r'C:\Users\victo\VtaGithub\span2vta\span2vta\venv\Lib\site-packages\geemap\foliumap.py'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old = 'basemaps = box.Box(basemaps.xyz_to_folium(), frozen_box=True)'

new = """\
try:
    basemaps = box.Box(basemaps.xyz_to_folium(), frozen_box=True)
except Exception:
    import xyzservices as _xyz
    import folium as _folium
    _bm = {}
    for _k, _v in _xyz.providers.flatten().items():
        try:
            _bm[_k.replace(".", "_")] = _folium.TileLayer(
                tiles=_v.build_url(),
                attr=_v.html_attribution,
                name=_k,
            )
        except Exception:
            pass
    if "OpenStreetMap_Mapnik" in _bm:
        _bm["OpenStreetMap"] = _bm["OpenStreetMap_Mapnik"]
    if "Esri_WorldImagery" in _bm:
        _bm["HYBRID"] = _bm["Esri_WorldImagery"]
        _bm["SATELLITE"] = _bm["Esri_WorldImagery"]
    if "CartoDB_Positron" in _bm:
        _bm["ROADMAP"] = _bm["CartoDB_Positron"]
    if "OpenTopoMap" in _bm:
        _bm["TERRAIN"] = _bm["OpenTopoMap"]
    basemaps = box.Box(_bm, frozen_box=True)"""

if old not in content:
    print("ERROR: target string not found in file - may already be patched or file differs")
else:
    content = content.replace(old, new)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patch applied successfully.")