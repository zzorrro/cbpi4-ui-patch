#!/usr/bin/env python3
"""Пропорциональное масштабирование дашборда CraftBeerPi4 (файл cbpi_dashboard_N.json).

Использование:
    python3 scale_dashboard.py вход.json выход.json 0.62

Умножаются на коэффициент: координаты x/y, ширины (width, maxheight), размеры текста
(size, namesize, stepsize), координаты и толщина линий. Минимальный размер шрифта задаётся MIN_FONT.
Элементы KettleControl (кнопки котла) имеют фиксированный размер small/medium/large, он не меняется.
"""
import json, sys

MIN_FONT = 12          # меньше этого размер шрифта не опускается (px или pt)
FONT_KEYS = ("size", "namesize", "stepsize")
LEN_KEYS = ("width", "maxheight")

def main(src, dst, k):
    d = json.load(open(src, encoding="utf-8"))
    for e in d["elements"]:
        e["x"] = round(e["x"] * k)
        e["y"] = round(e["y"] * k)
        p = e.get("props", {})
        for key in FONT_KEYS:
            v = p.get(key)
            if isinstance(v, (int, float)) or (isinstance(v, str) and v.isdigit()):
                p[key] = max(MIN_FONT, round(float(v) * k))
        for key in LEN_KEYS:
            v = p.get(key)
            if isinstance(v, (int, float)):
                p[key] = round(v * k)
        for key in ("width", "height"):
            if isinstance(e.get(key), (int, float)):
                e[key] = round(e[key] * k)
    for path in d.get("pathes", []):
        path["coordinates"] = [[round(x * k), round(y * k)] for x, y in path["coordinates"]]
        c = path.get("condition", {})
        if isinstance(c.get("stroke"), (int, float)):
            c["stroke"] = max(2, round(c["stroke"] * k))
    json.dump(d, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("Готово:", dst)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2], float(sys.argv[3]))
