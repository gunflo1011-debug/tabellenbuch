function generateBreadcrumb() {
  const breadcrumbEl = document.getElementById("breadcrumb");
  if (!breadcrumbEl) return;

  // Aktuellen Pfad holen
  const path = window.location.pathname.split("/").filter(Boolean);
  const startIndex = path.indexOf("pages");
  const subPath = path.slice(startIndex + 1);

  // Mapping: Dateinamen/Ordner -> Anzeigename
  const nameMap = {
    "mathematik": "Mathematik",
    "algebra": "Algebra",
    "analysis": "Analysis",
    "analysis-komplex.html": "Analysis (komplex)",
    "analysis-reell.html": "Analysis (reell)",
    "arithmetik.html": "Arithmetik",
    "dgl.html": "Differentialgleichungen",
    "diskret.html": "Diskrete Mathematik",
    "funktionen.html": "Funktionen",
    "funktionalanalysis.html": "Funktionalanalysis",
    "geometrie.html": "Geometrie",
    "grundlagen.html": "Grundlagen",
    "info-code-krypto.html": "Info & Krypto",
    "kategorien-logik.html": "Kategorien & Logik",
    "lineare-algebra.html": "Lineare Algebra",
    "mass-integration.html": "Maß & Integration",
    "numerik.html": "Numerik",
    "optimierung.html": "Optimierung",
    "statistik.html": "Statistik",
    "topologie-geo.html": "Topologie & Geometrie",
    "trigonometrie.html": "Trigonometrie",
    "wahrscheinlichkeit.html": "Wahrscheinlichkeit",
    "zahlentheorie.html": "Zahlentheorie",

    // Algebra Unterseiten
    "gleichungen.html": "Gleichungen",
    "ungleichungen.html": "Ungleichungen",
    "terme.html": "Terme & Umformungen",
    "polynome.html": "Polynome",
    "gleichungssysteme.html": "Gleichungssysteme",
    "vektoren.html": "Vektoren & Räume",
    "matrizen.html": "Matrizen & Determinanten",
    "lineareabbildungen.html": "Lineare Abbildungen",
    "gruppen.html": "Gruppentheorie",
    "ringe.html": "Ringtheorie",
    "koerper.html": "Körpertheorie",
    "moduln.html": "Moduln & Algebren",
    "galois.html": "Galoistheorie",
    "liealgebren.html": "Lie-Algebren & -Gruppen",
    "kategorien.html": "Kategorien & Homologische Algebra",
    "kombinatorik.html": "Kombinatorische Algebra",
    "restklassen.html": "Restklassen & Kongruenzen",
    "algebraische-geometrie.html": "Algebraische Geometrie",

    // Start
    "index.html": "Startseite"
  };

  // Breadcrumb aufbauen
  let html = `<a href="/index.html">🏠 Startseite</a>`;
  let cumulativePath = "/pages";

  subPath.forEach((part, i) => {
    cumulativePath += "/" + part;
    const isLast = i === subPath.length - 1;
    const displayName = nameMap[part] || part.replace(".html", "").replace("-", " ");
    if (isLast) {
      html += ` <span>›</span> <span class="current">${displayName}</span>`;
    } else {
      html += ` <span>›</span> <a href="${cumulativePath}">${displayName}</a>`;
    }
  });

  breadcrumbEl.innerHTML = html;
}

// beim Laden ausführen
document.addEventListener("DOMContentLoaded", generateBreadcrumb);
