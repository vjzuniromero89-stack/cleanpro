import re
CATS = [
 ("cabinas",     r"spray booth|paint booth|painting room|paint room|painting booth|spray paint|paint oven|painting machine"),
 ("simuladores", r"road simulator|road test simulator|chassis suspension|abnormal (noise|sound)|car shaker|shaking machine|shake machine|road shaking|suspension tester|sound testing|road simulation|rattle test"),
 ("bancadas",    r"straightening bench|frame machine|frame straightener|car bench|body repair (machine|equipment|tool)|straightening machine"),
 ("tornos",      r"brake (disc |drum )?lathe|drum lathe|disc lathe|brake drum|drum disc cutter"),
 ("vulcanizadoras", r"vulcaniz|tire patch|tyre curing|curing press|patch machine|reconditioning"),
 ("fluidos",     r"refrigerant|a/c|atf|transmission fluid|fluid oil|brake fluid|cooling system|fuel injector|fuel system|oil extractor|flush|nitrogen|oil exchanger|gearbox flush"),
 ("herramientas",r"dolly|transmission jack|transmission lifting jack|shop crane|low profile car lift jack|engine support|car ramps|tire spreader|tyre expander|tire remover, portable|bead breaker|timing tire repair|clamp 11"),
 ("alineadoras", r"wheel alignment|wheel aligner|alignment machine|alignment system|aligner|car alignment|truck alignment|four wheel alignment|4 wheel alignment|alignment equipment|alignment camera"),
 ("combos",      r"changer.{0,40}balancer combo|balancer combo|changer and (wheel )?balanc|balancer.{0,20}tire changer|tyre changer and wheel balancer|tire changers and wheel balancers|tire machine and balancer"),
 ("desmontadoras", r"tire changer|tyre changer|tire changing|tyre changing|tirechanger|tire changers|tire repair machine|tyre machine|tire machine|tire fitting|tire removal|tyre removal|tire remove|tyre repair equipment|tire dismount|wheel changer|tire mounting|tyre opening|tire repair service|tire remover truck|tire remover|changer tires"),
 ("balanceadoras", r"balanc"),
 ("elevadores",  r"lift|hoist|lifter|stacker|elevator|parking system"),
]
LABELS = {
 "alineadoras":"Alineadoras 3D",
 "balanceadoras":"Balanceadoras",
 "desmontadoras":"Desmontadoras de llantas",
 "combos":"Combos desmontadora + balanceadora",
 "elevadores":"Elevadores y rampas",
 "simuladores":"Simuladores de chasis (detector de ruidos)",
 "bancadas":"Bancadas de enderezado (chasis)",
 "cabinas":"Cabinas de pintura",
 "tornos":"Tornos de frenos",
 "vulcanizadoras":"Vulcanizadoras",
 "fluidos":"Fluidos, A/C y limpieza",
 "herramientas":"Gatos y herramientas",
}
def first_match(title):
    t=title.lower(); best=None
    for key,pat in CATS:
        m=re.search(pat,t)
        if m and (best is None or m.start()<best[0]): best=(m.start(),key)
    return best[1] if best else "otros"

def low_price(p):
    n=re.findall(r'[\d,]+',p)
    return float(n[0].replace(',','')) if n else 0

def classify(title, price):
    t=title.lower()
    # Strong product nouns win regardless of position
    for key in ("cabinas","simuladores","bancadas","tornos","vulcanizadoras","fluidos","herramientas"):
        if re.search(dict(CATS)[key],t): return key
    k=first_match(title)
    lp=low_price(price)
    # SEO-stuffed titles: use price as tie-breaker
    if k=="alineadoras" and lp<1000:
        k = "balanceadoras" if "balanc" in t else ("desmontadoras" if re.search(dict(CATS)["desmontadoras"],t) else k)
    if k in ("elevadores","desmontadoras","balanceadoras","combos") and re.search(dict(CATS)["alineadoras"],t) and 2000<=lp<=15000 and not re.search(r"4 post|four post|column|scissor|2 post|two post",t[:40]):
        k="alineadoras"
    if k=="combos" and lp>=2000 and re.search(dict(CATS)["alineadoras"],t): k="alineadoras"
    return k
