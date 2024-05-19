
# SikkerTxtDeling - STxtD

Eksamen i Programmering-B


![Logo](https://images.contentful.com/bg6mjhdcqk2h/7fidechodYAghafk7dblSz/70e0702c79524c4da91ac13b0df9f661/file_sharing.png)


## Features💡

- RSA-kryptering: Anvender RSA-kryptering til sikker filoverførsel.
- Brugernavnsgenerering: Genererer automatisk tilfældige brugernavne til brugere.
- Hostudsendelse: Hosts udsender deres detaljer for nem opdagelse af klienter.
- Hostopdagelse: Klienter kan lytte efter og opdage tilgængelige hosts.
- Filoverførsel: Giver klienter mulighed for at anmode om og modtage tekstfiler fra hosts.
- Platformuafhængig: Designet til at fungere på Windows.
- Trådede forbindelser: Håndterer flere forbindelser samtidigt ved hjælp af trådning.
- Simpelt interface: Brugervenligt kommandolinjeinterface til både hosting og forbindelse.


## FAQ❓

#### Q1: Hvad er SikkerTxtDeling?

SikkerTxtDeling er en Python-baseret applikation, der giver brugere mulighed for sikkert at dele tekstfiler ved hjælp af RSA-kryptering.

#### Q2: Hvordan sikrer SikkerTxtDeling sikkerheden af mine filer?

SikkerTxtDeling bruger RSA-kryptering til at sikre transmissionen af tekstfiler. Dette sikrer, at kun den tiltænkte modtager med den korrekte private nøgle kan dekryptere og læse filerne.

#### Q3: Hvad skal jeg bruge for at køre SikkerTxtDeling?

Du skal have Python installeret på dit system sammen med kryptografi-biblioteket. De nødvendige biblioteker kan installeres ved hjælp af requirements.txt filen, der er inkluderet i projektet.

#### Q4: Hvordan starter jeg en server for at være host for filer?

Kør applikationen og vælg 'host' valgmuligheden. Serveren vil begynde at udsende sine detaljer og vente på, at klienter opretter forbindelse.

#### Q5: Hvordan opretter jeg forbindelse til en host for at modtage filer?

Kør applikationen og vælg 'connect' valgmuligheden. Applikationen vil lytte efter tilgængelige hosts og bede dig om at oprette forbindelse til en.

#### Q6: Hvad skal jeg gøre, hvis jeg ikke kan finde nogen hosts at oprette forbindelse til?

Sørg for, at host serveren kører og udsender sine detaljer. Tjek også dine netværksindstillinger for at sikre, at din enhed kan modtage udsendelsesbeskeder.

#### Q7: Hvorfor kan jeg ikke bruge denne applikation på skolens netværk?

Der kan være flere grunde til, at du ikke kan bruge applikationen på skolens netværk
- Netværksrestriktioner: Skolen har muligvis strenge firewall-regler og restriktioner for at forhindre uautoriseret adgang og sikre netværkets sikkerhed.
  
- Blokerede porte: De porte, vi bruger til udsendelse (5001) og hovedforbindelsen (5000), kan være blokeret af netværksadministratorerne.
  
- Administrative tilladelser: Kørsel af serverapplikationer kræver ofte administrative tilladelser, som du måske ikke har på skolens computere eller netværk.
  
- Netværksadresseoversættelse (NAT): Skole netværker bruger tit NAT, hvilket kan forårsage problemer med direkte peer-to-peer forbindelser.
  
- Sikkerhedspolitikker: Skolens IT-politikker kan forbyde brugen af brugerdefinerede netværksapplikationer for at forhindre sikkerhedsrisici.
  
- Udsendelsesproblemer: UDP-udsendelser kan være begrænset eller filtreret af netværksudstyr for at reducere unødvendig trafik.

<p align="center">
  <img src="https://s5.ezgif.com/tmp/ezgif-5-53536aae3c.gif" alt="Centered GIF" style="display: block; margin: auto;">
</p>


## Anerkendelser📚

 - Python Software Foundation: For at skabe og vedligeholde Python, programmeringssproget brugt til at bygge denne applikation.

 - PyCryptodome: For at levere et omfattende og sikkert kryptografisk bibliotek, som er ryggraden i vores krypteringsfunktioner.

 - RSA Algoritmen: For den grundlæggende kryptografiske metode, der muliggør sikker dataoverførsel.

 - Open Source Community: For deres løbende bidrag og støtte, hvilket gør ressourcer og biblioteker tilgængelige for alle udviklere.

 - GitHub: For at levere en platform til at dele og samarbejde om kodeprojekter.


## Lavet af🙋‍♂️

- Kangal580  & riskbudur31


##
![AarhusTech](https://img.shields.io/badge/AarhusTech-red?style=flat)
