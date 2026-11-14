# Használati Utasítás

## 1. Demó indítása
A Kezdőlapon válaszd ki a szimulált hibajelleget (pl. Tengelybeállítási hiba), majd kattints a "Demó betöltése" gombra. Ezzel az adatok betöltődnek a memóriába.

## 2. Saját CSV feltöltése
A Kezdőlapon a "Saját CSV feltöltése" dobozban húzd be a fájlt. 
Elvárás: a CSV tartalmazzon egy `time_s` nevű oszlopot (az idő másodpercben), és legalább egy adatcsatornát (a mért értékekkel, pl. $m/s^2$-ben).

## 3. Elemzés indítása
- Lépj az **"Elemzés és Feldolgozás"** fülre.
- Válaszd ki az elemzendő csatornát.
- Add meg a pontos névleges fordulatszámot (RPM).
- Állítsd be a burkológörbe-spektrumhoz tartozó szűrősávot.
- Opcionálisan add meg a mérési pont lokalizációját (ez szükséges a rögzítési hibák vizsgálatához).
- Kattints az **"Elemzés indítása"** gombra. (Az adatok ellenőrzésen esnek át. Ha kritikus hiba van, a program leállítja az elemzést.)

## 4. Diagramok
A **"Diagramok"** fülön interaktív ábrákat találsz. A rendszer csúcsmegőrző algoritmust használ a böngésző tehermentesítésére.
Nagyítani kijelöléssel tudsz, az eredeti nézethez duplán kattints az ábrán.

## 5. Bizonyítékok és Jelentés
A **"Diagnosztika & Jelentés"** fül bemutatja az elsődleges hibajelleget és az időtartományi mutatókat (RMS, Kurtózis stb.).
A "Részletes Bizonyítékok" alatt lenyitható dobozokban látod, hogy egy-egy hiba (pl. csapágyhiba, mechanikai lazaság) mennyi támogató (✅), ellentmondó (❌) vagy hiányzó (⚠️) bizonyítékkal rendelkezik.
Az oldal alján található gombbal egy formázott **PDF jelentést** tölthetsz le.

## 6. Projekt mentése és visszatöltése
A **"Mentés & Visszatöltés"** fülön a teljes munkamenetet lementheted egyetlen ZIP fájlba, majd később ugyanitt visszatöltheted, hogy folytasd az elemzést.
