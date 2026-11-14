# Javítási és Tesztelési Jegyzőkönyv

## 1. Kijavított P0 és P1 problémák
- **Frekvencia és időbélyegek:** A program most már az időoszlop (`time_s`) alapján dinamikusan ellenőrzi és számítja a mintavételi frekvenciát. Ha a jel nem numerikus vagy egyenetlen, adatminőségi hibával leáll (F-01, F-06 javítva).
- **Amplitúdóskálázás:** A Hanning ablak koherens veszteségét 1/0.5 (tehát 2.0) szorzóval korrigálja az FFT számítás, így a szinuszok amplitúdója fillérre pontosan megegyezik a várt bemenettel (F-02 javítva).
- **Jel előkészítés:** A DC komponens eltávolításra kerül, az RMS valós váltakozóáramú rezgést számol. Nulla vagy állandó jelnél a program elutasítja az elemzést (F-03 javítva).
- **Elavult eredmények:** Beépítésre került a `stale` (elavult) állapot. Ha a felhasználó a felületen RPM-et vagy csatornát vált, a régi eredmény érvénytelenítődik, megelőzve az adatok összekeveredését (F-07 javítva).
- **Diagnosztikai motor:** 
  - A csapágyhiba megállapításához a kurtózis önmagában már nem elég 5 pont eléréséhez; szükséges hozzá a burkológörbén látható ismétlődés is (F-04 javítva).
  - Az alap-/rögzítési hibák 5 pontja elérhetővé vált azáltal, hogy kiegészült a szabály a "mérési pont lokalizációja" nevű metainformációval. Ha ez nincs megadva, a hiba állapota "nem támogatott" marad, de jelzi a hiányzó adatot (F-05 javítva).
- **Ábrák és letöltések:** A Plotly ábrák csúcsmegőrző módon jelennek meg. Elkészült a round-trip ZIP mentés, és a ReportLab Unicode-támogatása be van állítva a PDF-jelentéshez, kiküszöbölve az ő/ű problémát.

## 2. Automatizált Eredmények (Integrációs Tesztek)
A `tests/test_integration.py` a következőket validálta:
- Szabályos szinusz (1000Hz mintavétel, 25Hz frekvencia, 2.0 amplitúdó) esetén: időalap ellenőrzése sikeres (1000Hz), az FFT csúcs frekvenciája 25.0, a maximális amplitúdó 2.0 (hibahatáron belül).
- Konstans jel ellenőrzése elbukik ("állandó vagy zérus" üzenettel).
- Túl rövid jel ellenőrzése elbukik ("túl rövid" üzenettel).
- Egyedi ütés (magas kurtózis, de ismétlődő burkolócsúcs nélkül) nem minősül teljes bizonyosságú csapágyhibának a diagnosztikában.
- Gépláb metaadat megadása esetén az 1x amplitúdóval rendelkező alap-hibajelölt szabály támogatott lesz (6 ponttal).

## 3. Nem ellenőrzött részek / Korlátok
- Ez a verzió zárt, asztali környezetben lett tesztelve E2E (Playwright/Selenium) böngészővezérlés nélkül, ezért a Streamlit gombkattintásainak felületi élménye csak az app.py logikájára támaszkodik.
- Valós ipari validáció nem történt, a rendszer egy fejlett matematikai jelfeldolgozó demonstrátor.
