***Trenovani prostredi CIRCGymu***


Cely seznam (zatim netrideny) je [tady](environments.md)



**Jaky typ akci trenovat?**

reach, push, slide,pick, drop,catch, pick and place, poke (delayed), throw (delayed), move

v dalsi fazi jejich kombinace 


**Jak prostredi natrenovat?**


**Trenovani RL algoritmu bez videni**

5. Procti si kod pro trenovani RL ulohy v [Pybulletu](run.py)
6. Modifikuj trenovanovaci kod pro sve prostredi a natrenuj robota na zvolenou ulohu (reach, pick apod.)
7. Evaluuj vysledky, vytvor gif po natrenovani a uloz natrenovane vahy do repository. Pokud lze, pripoj hodbnotu uspesnosti trenovani.
8. Popis zpusob trenovani do md souboru a pripoj gif. Melo by to vypadat asi [takto](example.md)
9. Modifikuj prostredi a rewardy pro ulohu push, pull, pick and place, poke a throw, v pripade mobilnich robotu i pro pohyb. Pokud lze, prepinej jednotlive typy uloh parametrem pri spousteni.

**Trenovani RL algoritmu s videnim**

10. Vloz do trenovaciho kodu predtrenovane videni Yolact
11. Modifikuj rewardy pro informaci z vystupu Yolactu
13. Zopakuj body 7.-9. 

**Trenovani RL algoritmu s unsupervised videnim**

10. Vloz do trenovaciho kodu predtrenovane videni VAE
11. Modifikuj rewardy pro informaci z vystupu Yolactu
13. Zopakuj body 7.-9. 


***Navod na praci s Yolactem (videni 3dvs)***
[navod](yolact_guide.md)
