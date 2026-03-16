Vytvorené v rámci projektu **Mier nie je samozrejmosť** pri príležitosti 80. výročie konca 2. svetovej vojny na GJH

# Simulácie

`enigma.py` a `lorenz.py` sú simulácie mechanizmov nemeckých šifrovacích strojov Enigma a Lorenz SZ. Na ich spustenie je potrebná knižnica [winter](https://github.com/mk8-bruh/winter.py). Oba programy majú oddelenú sekciu `logic`, v ktorej sa nachádza samotná reprezentácia mechanizmu. Po stiahnutí programu aj knižnice do jedného priečinka spustite v termináli príkazom `python [enigma|lorenz].py`. Uistite sa, že terminálové okno má rozmery minimálne 43 x 15 znakov.

V oboch simuláciách použite `Tab` na prepnutie medzi písacím módom a nastaveniami. V nastaveniach sa môžete navigovať šípkami vo všetkých smeroch. V rotorových nastaveniach Enigmy môžete písmenami nastaviť pozíciu rotora (`<` značí pozíciu, ktorá pri pretočení pretočí nasledujúci rotor) a číslami `1`-`8` nastaviť typ rotora (rôzne konfigurácie a pozície pretočenia; presne tie, sa používali v nemeckej armáde v praxi). Rotor 0 (`NaN`) značí absenciu rotora. Písmenami `A`-`C` môžete nastaviť typ reflektora (táto simulácia nepodporuje rotujúci reflektor ani viac rotorov). Na plugboarde môžete písať kofiguráciu v dvojiciach písmen a použiť `Backspace`/`Delete` na vymazanie vybranej dvojice. V rotorových nastaveniach Lorenz použite `Space` na prepnutie medzi binárnym a pozičným módom; v binárnom móde môžete prepisovať hodnoty `0`/`1`, kým v pozičnom móde môžete písať pozície jednotlivých rotorov.

# [Enigma](https://en.wikipedia.org/wiki/Cryptanalysis_of_the_Enigma)

![Picutre of an Enigma machine](https://upload.wikimedia.org/wikipedia/commons/thumb/b/bd/Enigma_%28crittografia%29_-_Museo_scienza_e_tecnologia_Milano.jpg/500px-Enigma_%28crittografia%29_-_Museo_scienza_e_tecnologia_Milano.jpg)

Enigma bol stroj používaný na bežnú komunikáciu vo všetkých odvetviach nemeckej armády. V štandardnej Enigme išiel vstup z klávesnice najskôr cez tzv. "plugboard", ktorý dokázal obojstranne vymeniť ľubovoľné páry písmen (umožňujúc viac ako 150 biliónov kombinácií), ďalej cez 3 rotory, ktoré mali statickú konfiguráciu, ale v pravidelných intervaloch sa otáčali (prvý rotor pri každom písmene, druhý pri každej 26. otáčke prvého rotora and tretí pri každej 26. otáčke druhého rotora), čím celková konfigurácia rotovala s opakovaním po 16,900 znakoch. Na konci bol reflektor, ktorý vždy spájal páry 2 písmen; týmto pádom poslal signál späť celým mechanizmom, cez všetky rotory, plugboard až ku lampičkám, ktoré vysvietili zašifrované písmeno. Mechanizmus reflektora, ktorý bol unikátny pre Enigmu zaručoval seba-inverziu (ak `A -> X` tak `X -> A`), čo v praxi znamenalo že na zašifrovanie aj rozšifrovanie stačila len jedna klávesnica. Reflektor bol ale zároveň najväčšou kryptografickou slabinou Enigmy, keďže žiadne písmeno sa nedalo zašifrovať samo na seba, a práve vďaka tejto vlastnosti dokázal Alan Turing vytvoriť [bombe](https://en.wikipedia.org/wiki/Bombe), vďaka ktorej sa dal kľúč zistiť v priebehu niekoľkých hodín. So všetkými prvkami mala vojenská Enigma až 158,962,555,217,826,360,000 (158 triliónov) rôznych nastavení.

![Diagram of the Enigma's internal mechanism](http://www.rotilom.com/juin44/enigma/principe_en.jpg)

# [Lorenz](https://en.wikipedia.org/wiki/Cryptanalysis_of_the_Lorenz_cipher)

![Picture of a Lorenz SZ40](https://www.cryptomuseum.com/crypto/lorenz/sz40/img/lorenz_sz40_small.jpg)

Lorenz bol nadstavec na tzv. [rádiový teletyp (RTTY)](https://en.wikipedia.org/wiki/Teleprinter) používaný na najtajnejšiu komunikáciu nemeckým vrchným veliteľstvom. Táto šifra bola digitálna a oveľa ťažšia na prelomenie, obzvlášť bez pomoci strojov (bol kvôli nej skonštruovaný prvý programovateľný, elektrický a digitálny počítač na svete, [Colossus](https://en.wikipedia.org/wiki/Colossus_computer)). Používala písmená zakódované do piatich bitov podľa [ITA2](https://en.wikipedia.org/wiki/Baudot_code#ITA2) a kódovala ich [Vernamovou prúdovou šifrou](https://en.wikipedia.org/wiki/Gilbert_Vernam#The_Vernam_cipher) z dvoch sád piatich rotorov. Na rozdiel od Enigmy sa všetky rotory líšili počtom článkov (41, 31, 29, 26, 23, 43, 47, 51, 53, 59, 37, 61), vďaka čomu mali oveľa väčšiu periódu (počet otočení, po koľkých sa dostanú do rovnakej polohy). Rotory boli kompletne konfigurovateľné, teda všetky bity (`1`/`0`) sa dali manuálne prepnúť, čo poskytovalo `2^501` rôznych nastavení. V spojení s počtom rôznych polôh rotorov a správaním tzv. motorových rotorov, ktoré kontrolovali pohyb ostatných rotorov existoval astronomicky veľký počet kombinácií stavu, v ktorom sa šifrovací stroj mohol nachádzať.

![Diagram of the Lorenz's logical structure](https://www.codesandciphers.org.uk/lorenz/pictures/Lordiag.gif)

