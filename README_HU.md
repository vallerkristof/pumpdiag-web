# PumpDiag Web v2.0 - Szivattyúdiagnosztikai Alkalmazás

Ez egy független vizsgálat és ellenőrzés alapján javított, továbbfejlesztett rezgésdiagnosztikai webalkalmazás szivattyúk elemzésére.
Az alkalmazás Streamlit keretrendszerben készült.

## Újdonságok és Javítások a v2.0-ban
- Helyes FFT amplitúdóskálázás és frekvencia-azonosítás a megadott időbélyegekből.
- Robusztus adatminőségi kapu: nullajelek, NaN és konstans jelek szűrése.
- Fejlett diagnosztikai szabályrendszer, amely nemcsak kurtózisra, hanem több bizonyítékra támaszkodik.
- Vizuális interaktív felület, megőrizve az adatcsúcsokat.
- PDF jelentés Unicode-támogatással, teljes bizonyítéklistával és gépazonosítással.
- Projektmentés és -visszatöltés ZIP formátumban (round-trip).
