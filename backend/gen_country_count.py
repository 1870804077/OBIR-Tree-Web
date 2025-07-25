import reverse_geocoder as rg
import json
import pycountry
import os

def iso_to_country_name(iso):
    try:
        country = pycountry.countries.get(alpha_2=iso)
        return country.name if country else iso
    except Exception:
        return iso

def main():
    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../public/mock/data.txt'))
    out_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../public/mock/country_count.json'))
    country_count = {}
    coords = []
    with open(data_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 4:
                continue
            _, _, lat, lon = parts
            try:
                lat_f = float(lat)
                lon_f = float(lon)
                coords.append((lat_f, lon_f))
            except ValueError:
                continue
    # 批量查找
    results = rg.search(coords)
    for res in results:
        cc = res['cc']
        country_count[cc] = country_count.get(cc, 0) + 1
    country_count_named = {iso_to_country_name(k): v for k, v in country_count.items()}
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(country_count_named, f, ensure_ascii=False, indent=2)
    print('统计完成，已保存为 country_count.json')

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print('运行出错:', e) 