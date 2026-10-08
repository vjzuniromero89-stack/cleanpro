# Catálogo Xpromise

Catálogo completo de **Yantai Xpromise Garage Equipment Co., Ltd.** (tienda en Alibaba: https://xpromise.en.alibaba.com), tomado el 5 de octubre de 2026.

- `index.html`: el catálogo. Un solo archivo con las 431 fotos incluidas; se abre en cualquier navegador, incluso sin internet. Tiene búsqueda, filtro por categoría, orden por precio y ficha de cada producto con enlace a Alibaba.
- `catalogo_xpromise.csv`: los mismos 431 productos para Excel o Google Sheets (categoría, nombre en español, modelo, precio, pedido mínimo, vendidos, título original, enlace, foto y ficha técnica cuando existe).
- `img/`: fotos de cada producto (209×209 px), nombradas por el ID de Alibaba.
- `raw/`: datos extraídos (listado por página y fichas técnicas de 21 modelos).
- `build.py` + `template.html`: regeneran `index.html` y el CSV con `python3 build.py` (requiere los datos de `raw/` e `img/`).

Notas:
- Los precios son los de Alibaba en USD (FOB). Seis artículos tienen un rango de relleno ($20-1,000 / $50-2,000) y aparecen como «Precio a consultar».
- Muchas publicaciones repiten la misma máquina con otro título. Cuando una publicación sin ficha tiene la misma categoría y precio que un modelo con ficha, el catálogo lo enlaza como probable equivalente.
