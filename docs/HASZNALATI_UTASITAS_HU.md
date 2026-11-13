# PumpDiag Web - Használati Utasítás

## 1. Az alkalmazás megnyitása
- Indítsd el az alkalmazást a telepítési útmutató (TELEPITES_HU.md) szerint.
- Nyisd meg a böngészőben a kapott localhost címet.

## 2. Demó elindítása
- A Kezdőlapon kattints a "Tengelybeállítási hiba demó betöltése" vagy a "Csapágyhiba demó betöltése" gombra.
- Várj, amíg megjelenik a "Demó betöltve" zöld üzenet.

## 3. Saját mérési fájlok feltöltése
- Kattints a "Browse files" gombra a fájlfeltöltőben.
- Válassz egy CSV formátumú mérési adatfájlt.
- Elvárt oszlopok: `time_s` (idő másodpercben) és tetszőleges rezgéscsatornák (pl. `pump_de_h`), mértékegység: m/s².

## 4. Elemzés indítása
- Lépj át az "Elemzés" fülre.
- A lenyíló listából válaszd ki a vizsgálandó rezgéscsatornát.
- Add meg a névleges fordulatszámot (RPM).
- Kattints az "Elemzés indítása" gombra.

## 5. Diagramok kezelése és értelmezése
- Lépj a "Diagramok" fülre.
- Itt látható a gyorsulás-időjel (interaktívan nagyítható).
- Alatta az amplitúdóspektrum, piros szaggatott vonalakkal jelölve a forgási harmonikusokat (1x, 2x, 3x...).

## 6. Diagnosztikai eredmény
- A "Diagnosztika & Jelentés" fülön a legfelső doboz jelzi az elsődleges gyanút (pl. Tengelybeállítási hiba gyanúja).
- Fontos: Ez nem minősül automatikus bizonyosságnak, hanem a frekvencia-jellemzőkből levont statisztikai következtetés.

## 7. PDF és adatok letöltése
- Ugyanezen a fülön kattints a "PDF Letöltése" gombra a riport mentéséhez.
- A "Mentés" fülön a teljes diagnosztikai eredményt ZIP-ben kimentheted.
