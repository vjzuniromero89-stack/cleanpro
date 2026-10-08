"""Genera el catálogo del proveedor Xpromise a partir de los datos extraídos.

Entradas:  raw/all_products.tsv, raw/details.jsonl, img/<id>.jpg
Salidas:   index.html (catálogo autocontenido, fotos incrustadas)
           catalogo_xpromise.csv (para Excel / Google Sheets)
"""
import base64, csv, html, json, re
from pathlib import Path

ROOT = Path(__file__).parent
CDN = "https://s.alicdn.com/@sc04/kf/"

CAT_LABELS = {
    "alineadoras": "Alineadoras 3D",
    "balanceadoras": "Balanceadoras",
    "desmontadoras": "Desmontadoras de llantas",
    "combos": "Combos desmontadora + balanceadora",
    "elevadores": "Elevadores",
    "simuladores": "Simuladores de chasis",
    "bancadas": "Bancadas de enderezado",
    "cabinas": "Cabinas de pintura",
    "tornos": "Tornos de frenos",
    "vulcanizadoras": "Vulcanizadoras",
    "fluidos": "Fluidos, A/C y limpieza",
    "herramientas": "Gatos, herramientas y accesorios",
}
CAT_ORDER = list(CAT_LABELS)

PATTERNS = [
    ("cabinas", r"spray booth|paint booth|painting room|paint room|painting booth|spray paint|paint oven|painting machine"),
    ("simuladores", r"road simulator|chassis simulator|road test simulator|chassis suspension|abnormal (noise|sound)|car shaker|shaking machine|shake machine|road shaking|suspension tester|sound testing|road simulation|rattle test"),
    ("bancadas", r"straightening bench|frame machine|frame straightener|car bench|body repair (machine|equipment|tool)|straightening machine"),
    ("tornos", r"brake (disc |drum )?lathe|drum lathe|disc lathe|brake drum|drum disc cutter"),
    ("vulcanizadoras", r"vulcaniz|tire patch|tyre curing|curing press|patch machine|reconditioning"),
    ("fluidos", r"refrigerant|a/c\b|\batf\b|transmission fluid|fluid oil|brake fluid|cooling system|fuel injector|fuel system|oil extractor|flush|nitrogen|oil exchanger"),
    ("herramientas", r"dolly|transmission jack|transmission lifting jack|shop crane|low profile car lift jack|engine support|car ramps|tire spreader|tyre expander|tire remover, portable|bead breaker|timing tire repair|clamp 11"),
    ("alineadoras", r"wheel alignment|wheel aligner|alignment machine|alignment system|aligner|car alignment|truck alignment|four wheel alignment|4 wheel alignment|alignment equipment|alignment camera"),
    ("combos", r"changer.{0,40}balancer combo|balancer combo|changer and (wheel )?balanc|balancer.{0,20}tire changer|tyre changer and wheel balancer|tire changers and wheel balancers|tire machine and balancer"),
    ("desmontadoras", r"tire changer|tyre changer|tire changing|tyre changing|tirechanger|tire changers|tire repair machine|tyre machine|tire machine|tire fitting|tire removal|tyre removal|tire remove|tyre repair equipment|tire dismount|wheel changer|tire mounting|tyre opening|tire repair service|tire remover|changer tires"),
    ("balanceadoras", r"balanc"),
    ("elevadores", r"lift|hoist|lifter|stacker|elevator|parking system"),
]
PAT = dict(PATTERNS)
STRONG = ("cabinas", "simuladores", "bancadas", "tornos", "vulcanizadoras", "fluidos", "herramientas")
OVERRIDES = {
    "1601960908724": "alineadoras",  # elevador 4 postes + alineadora, precio de alineadora
    "1601385837702": "alineadoras",
    "1601115807671": "elevadores",   # elevador de tijera para alineación
}


def low_price(p):
    n = re.findall(r"[\d,]+(?:\.\d+)?", p)
    return float(n[0].replace(",", "")) if n else 0.0


def high_price(p):
    n = re.findall(r"[\d,]+(?:\.\d+)?", p)
    return float(n[-1].replace(",", "")) if n else 0.0


def classify(pid, title, price):
    if pid in OVERRIDES:
        return OVERRIDES[pid]
    t = title.lower()
    for key in STRONG:
        if re.search(PAT[key], t):
            return key
    best = None
    for key, pat in PATTERNS:
        m = re.search(pat, t)
        if m and (best is None or m.start() < best[0]):
            best = (m.start(), key)
    k = best[1] if best else "herramientas"
    lp = low_price(price)
    if k == "alineadoras" and lp < 1000:
        k = "balanceadoras" if "balanc" in t else ("desmontadoras" if re.search(PAT["desmontadoras"], t) else k)
    if (k in ("elevadores", "desmontadoras", "balanceadoras", "combos") and re.search(PAT["alineadoras"], t)
            and 2000 <= lp <= 15000 and not re.search(r"4 post|four post|column|scissor|2 post|two post", t[:40])):
        k = "alineadoras"
    if k == "combos" and lp >= 2000 and re.search(PAT["alineadoras"], t):
        k = "alineadoras"
    return k


def has(t, pat):
    return re.search(pat, t) is not None


def capacity(t):
    m = re.search(r"(\d{4,5})\s*kg", t)
    if m:
        return f"{int(m.group(1)):,} kg".replace(",", ",")
    m = re.search(r"\b(\d+(?:\.\d+)?)\s*(?:-\s*)?(?:t|ton|tons)\b", t)
    if m:
        return f"{m.group(1)} t"
    return None


def spanish_name(cat, title):
    t = title.lower()
    truck = has(t, r"truck|bus|heavy duty|trailer")
    q = []
    if cat == "alineadoras":
        n = "Alineadora 3D"
        if truck:
            n += " para camión y autobús"
        if has(t, r"two screen|two monitors|2 monitor|double screen"):
            q.append("doble pantalla")
        if has(t, r"lifting beam|lifting cabinet"):
            q.append("con viga elevadora")
        if has(t, r"auto tracking|automatic tracking"):
            q.append("seguimiento automático")
        if has(t, r"portable|mobile truck"):
            q.append("portátil")
        if has(t, r"\bmanual\b"):
            q.append("manual")
        if has(t, r"4 post|four post"):
            q.append("con elevador de 4 postes")
    elif cat == "balanceadoras":
        n = "Balanceadora de ruedas"
        if has(t, r"motorcycle"):
            n += " para moto"
        elif truck:
            n += " para camión y auto"
        if has(t, r"semi-automatic|semi automatic"):
            q.append("semiautomática")
        elif has(t, r"automatic"):
            q.append("automática")
        elif has(t, r"\bmanual\b"):
            q.append("manual")
        if has(t, r"laser"):
            q.append("con láser")
    elif cat == "desmontadoras":
        n = "Desmontadora de llantas"
        if has(t, r"motorcycle"):
            n += " para moto"
        elif truck:
            n += " para camión"
        if has(t, r"semi-automatic|semi automatic"):
            q.append("semiautomática")
        elif has(t, r"fully automatic|full automatic|automatic"):
            q.append("automática")
        elif has(t, r"\bmanual\b"):
            q.append("manual")
        if has(t, r"leverless|lever-less"):
            q.append("sin palanca")
        if has(t, r"helper|helping arm|arm helper"):
            q.append("con brazo auxiliar")
        if has(t, r"swing arm"):
            q.append("brazo oscilante")
        if has(t, r"tilting|back tilting"):
            q.append("columna basculante")
        if has(t, r"portable|mobile tire"):
            q.append("portátil")
    elif cat == "combos":
        n = "Combo desmontadora + balanceadora"
        if truck:
            q.append("para camión")
    elif cat == "elevadores":
        if has(t, r"new energy|ev cars"):
            n = "Elevador de tijera para vehículos eléctricos"
        elif has(t, r"column") and has(t, r"truck|bus"):
            n = "Columnas elevadoras para camión y autobús"
        elif has(t, r"single post|one column|1 post|single column"):
            n = "Elevador móvil de 1 columna"
        elif has(t, r"scissor|shear lift"):
            n = "Elevador de tijera"
            if has(t, r"in-ground|in ground"):
                q.append("empotrado")
            if has(t, r"mid rise|mid-rise|small|portable|mobile"):
                q.append("media altura")
            if has(t, r"super thin|on ground"):
                q.append("ultradelgado")
            if has(t, r"alignment"):
                q.append("para alineación")
        elif has(t, r"4 post|four post|4t garage|4 pillar|4 ton four"):
            n = "Elevador de 4 postes"
            if has(t, r"alignment"):
                q.append("para alineación")
            if has(t, r"parking"):
                q.append("estacionamiento")
        elif has(t, r"2 post|two post|2 column|2 poles|double-cylinder|double cylinder"):
            n = "Elevador de 2 postes"
            if has(t, r"clear floor|gantry"):
                q.append("piso libre")
            if has(t, r"base plate|floor plate"):
                q.append("con placa base")
            if has(t, r"asymmetrical"):
                q.append("brazos asimétricos")
            if has(t, r"parking|stacker"):
                q.append("estacionamiento")
        else:
            n = "Elevador de autos"
        cap = capacity(t)
        if cap:
            q.append(cap)
    elif cat == "simuladores":
        n = "Simulador de camino (detector de ruidos de chasis)"
        if has(t, r"touch screen"):
            q.append("pantalla táctil")
        cap = capacity(t)
        if cap:
            q.append(cap)
    elif cat == "bancadas":
        n = "Bancada de enderezado de chasis"
    elif cat == "cabinas":
        n = "Cabina de pintura"
        if has(t, r"bus"):
            q.append("para autobús")
        if has(t, r"gas burner"):
            q.append("quemador de gas")
        if has(t, r"diesel"):
            q.append("calefacción diésel")
    elif cat == "tornos":
        n = "Torno de frenos en vehículo" if has(t, r"on car|upon car|get on and off|pro up") else "Torno de frenos (discos y tambores)"
    elif cat == "vulcanizadoras":
        if has(t, r"hydraulic press|curing press"):
            n = "Prensa vulcanizadora para parches"
        else:
            n = "Vulcanizadora"
            if truck:
                q.append("para camión")
            if has(t, r"portable"):
                q.append("portátil")
            if has(t, r"temperature"):
                q.append("temperatura regulable")
    elif cat == "fluidos":
        if has(t, r"refrigerant|a/c"):
            n = "Recuperadora de refrigerante A/C"
            if has(t, r"flushing and cleaning"):
                n = "Máquina de lavado de sistema A/C"
        elif has(t, r"\batf\b|transmission|gearbox"):
            n = "Cambiadora de aceite de transmisión (ATF)"
        elif has(t, r"brake fluid|brake oil"):
            n = "Cambiadora de líquido de frenos"
        elif has(t, r"cooling"):
            n = "Limpiadora de sistema de enfriamiento"
        elif has(t, r"injector|fuel system"):
            n = "Limpiadora de inyectores"
        elif has(t, r"oil extractor"):
            n = "Extractor neumático de aceite"
        elif has(t, r"nitrogen"):
            n = "Generador de nitrógeno para llantas"
        else:
            n = "Equipo de fluidos"
    else:
        if has(t, r"dolly"):
            n = "Patín para mover vehículos (dolly)"
        elif has(t, r"transmission"):
            n = "Gato de transmisión"
        elif has(t, r"crane"):
            n = "Grúa de taller 2000 lb"
        elif has(t, r"low profile"):
            n = "Gato hidráulico de perfil bajo 3 t"
        elif has(t, r"engine support"):
            n = "Traviesa soporte de motor"
        elif has(t, r"ramps"):
            n = "Rampas hidráulicas"
        elif has(t, r"spreader|expander"):
            n = "Abridor de llantas manual"
        elif has(t, r"clamp"):
            n = "Garras para alineadora 11\"-25\""
        elif has(t, r"bead breaker"):
            n = "Destalonador portátil"
        elif has(t, r"scraping"):
            n = "Raspador de llantas portátil"
        else:
            n = "Herramienta de reparación de llantas"
    if q:
        n += " · " + ", ".join(dict.fromkeys(q))
    return n


def model(title):
    m = re.search(r"\b(XP[- ]?[A-Z]?\d{2,4}[A-Z]?|A7|C93\d\dA|HO-X520|SH-300)\b", title, re.I)
    return m.group(1).upper().replace(" ", "-") if m else ""


def placeholder_price(p):
    return p in ("$20-1,000", "$50-2,000")


def main():
    details = {}
    for line in (ROOT / "raw/details.jsonl").read_text().splitlines():
        if line.strip():
            d = json.loads(line)
            details[d["id"]] = d

    products = []
    for i, line in enumerate((ROOT / "raw/all_products.tsv").read_text().splitlines()):
        page, slug, img, price, moq, sold, title = line.split("\t")
        pid = slug.rsplit("_", 1)[1]
        cat = classify(pid, title, price)
        ph = placeholder_price(price)
        d = details.get(pid)
        products.append({
            "id": pid,
            "n": i,
            "pg": int(page),
            "cat": cat,
            "es": spanish_name(cat, title),
            "t": title,
            "m": (dict(d["attrs"]).get("Modelo") if d else "") or model(title),
            "p": "Precio a consultar" if ph else price,
            "lo": None if ph else low_price(price),
            "hi": None if ph else high_price(price),
            "moq": moq,
            "sold": int(sold.split()[0]) if sold else 0,
            "url": f"https://www.alibaba.com/product-detail/{slug}.html",
            "src": CDN + img.split("?")[0],
            "spec": d is not None,
        })

    # Productos sin ficha: modelo equivalente = misma categoría y mismo precio que uno con ficha.
    ref = {}
    for p in products:
        if p["spec"]:
            ref.setdefault((p["cat"], p["p"]), p["id"])
    for p in products:
        if not p["spec"]:
            r = ref.get((p["cat"], p["p"]))
            if r:
                p["ref"] = r

    specs = {k: {"tiers": v["tiers"], "lead": v["lead"], "attrs": v["attrs"]} for k, v in details.items()}
    imgs = {p["id"]: base64.b64encode((ROOT / f"img/{p['id']}.jpg").read_bytes()).decode() for p in products}

    cats = [{"k": k, "l": CAT_LABELS[k], "c": sum(1 for p in products if p["cat"] == k)} for k in CAT_ORDER]
    data = {"products": products, "specs": specs, "cats": cats}

    tpl = (ROOT / "template.html").read_text()
    out = (tpl.replace("/*DATA*/null", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
              .replace("/*IMGS*/null", json.dumps(imgs, separators=(",", ":"))))
    (ROOT / "index.html").write_text(out)

    with open(ROOT / "catalogo_xpromise.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["#", "Categoría", "Producto (español)", "Modelo", "Precio USD", "Pedido mínimo",
                    "Vendidos", "Título original en Alibaba", "Enlace", "Foto", "Ficha técnica"])
        for p in products:
            d = details.get(p["id"])
            ficha = " | ".join(f"{a}: {b}" for a, b in d["attrs"]) if d else ""
            w.writerow([p["n"] + 1, CAT_LABELS[p["cat"]], p["es"], p["m"], p["p"], p["moq"],
                        p["sold"] or "", p["t"], p["url"], p["src"], ficha])

    print(len(products), "productos;", sum(p["spec"] for p in products), "con ficha;",
          sum(1 for p in products if p.get("ref")), "con ficha de modelo equivalente")
    for c in cats:
        print(f"  {c['l']}: {c['c']}")
    print("index.html", round((ROOT / "index.html").stat().st_size / 1e6, 2), "MB")


if __name__ == "__main__":
    main()
