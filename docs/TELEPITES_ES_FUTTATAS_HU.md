# Telepítés és Futtatás (PumpDiag Web v2.0)

## Helyi futtatás (Windows)
1. Csomagold ki a letöltött `PumpDiag_Web_Javitott_Kiadas.zip` fájlt egy új mappába.
2. Nyiss meg egy parancssort a kicsomagolt mappában. (Fájlkezelő címsorába írd be: `cmd`)
3. Hozz létre egy virtuális környezetet: 
   `python -m venv venv`
4. Aktiváld a környezetet: 
   `venv\Scripts\activate`
5. Telepítsd a függőségeket: 
   `pip install -r requirements.txt`
6. Indítsd el az alkalmazást: 
   `streamlit run app.py`

## Felhős futtatás (Streamlit Community Cloud)
1. Hozd létre az ingyenes GitHub fiókodat (github.com).
2. Hozz létre egy új publikus vagy privát repository-t (pl. `pumpdiag-web-v2`).
3. Töltsd fel a kicsomagolt ZIP tartalmát (megtartva a mappaszerkezetet, kivéve a `venv` mappát, ha létrehoztad).
4. Lépj be a share.streamlit.io oldalra.
5. Válaszd a 'Create app' / 'New app' gombot.
6. Válaszd ki a létrehozott GitHub tárolódat.
7. A belépési fájl ('Main file path') pontosan ez legyen: `app.py`.
8. Kattints a 'Deploy!' gombra. Az alkalmazás 2-3 percen belül elérhető lesz.

**Korábbi verzió leváltása:** 
Ha már van egy régi verziód feltöltve a GitHubra, töltsd le onnan a régi adataidat biztos ami biztos. 
Ezután a legegyszerűbb, ha a régi GitHub tárolódban kitörlöd a fájlokat, és az új ZIP tartalmát töltöd fel a helyükre, vagy egy teljesen új tárolót hozol létre az új verziónak.
