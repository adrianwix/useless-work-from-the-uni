EiP Praktikum WS 2018/2019
==========================

Ziel
----

Implemetieren Sie in Python ein rundenbasiertes Gesellschaftsspiel für 2 oder
mehr Mitspieler mit Hilfe des vorgegebenen Frameworks.
Das vorgegebene Framework erlaubt sowohl die lokale Ausführung als auch die Ausführung
über das Internet.
Ein Beispielprogramm `TicTacToe.py` ist vorgegeben, an dem Sie sich orientieren können.
Es enthält ausgiebige Kommentare zu den Methoden, die Sie implementieren müssen.
Die letzte auszuführende Codezeile in Ihrem Programm muss immer

    GamePlayer.run(...

mit beginnen!
Der Aufruf startet die Ausführung über das Framework und kehrt erst zurück,
wenn das Spiel beendet wurde


Ausführung
----------

Sie können `TicTacToe.py` oder ein von Ihnen programmiertes Spiel direkt ausführen.
Alternativ können Sie auch `GamePlayer.py` ausführen.
Dieses Programm erkennt alle Spieledateien im Verzeichnis und erlaubt sowohl das
lokale Spielen als auch das Spielen über das Internet über einen entsprechenden Dialog.


Aufgaben
--------

### Aufgabe 0 - Versionskontrolle Git
Richten Sie wie auf der Wiki-Seiter im Reader beschrieben Ihre Arbeitsumgebung ein.
  
### Aufgabe 1 - Vier Gewinnt
Implementieren Sie das Spiel `Vier gewinnt` für 2 Spieler und führen Sie es zunächst
nur lokal aus.
Wenn dies funktioniert, testen Sie, ob es auch über das Internet funktioniert.
Eine Datei `VierGewinnt.py` ist bereits vorgegeben.
Eine ausführliche Spielbeschreibung finden Sie in der Wikipedia.
Zur Umsetzung können Sie z.B. folgendermaßen vorgehen:

1. Überlegen Sie sich, wie den Spielzustand über eine globale Variable darstellen wollen
und initialisieren Sie diese im globalen Scope oder über die `initGame` Funtion.
2. Implementieren Sie die `paintGame` Funktion.
Das Programm sollte sich anschließend starten lassen und das Spielfeld darstellen.
3. Implementieren Sie die Zuglogik in der `makeMove` Funktion und geben Sie immer den Index
desjenigen Spielers zurück, der gerade nicht am Zug war.
4. Implementieren Sie die Überprüfung, ob ein Spieler gewonnen hat, sodass die
`makeMove` Funktion korrekt -1 zurückgeben kann, falls ein Spieler gewonnen hat.


#### Aufgabe 2 - Implementierung eines Spiels nach Wahl
Imlementieren Sie ein Spiel Ihrer Wahl.
Besprechen Sie Ihre Spielidee mit einem Betreuer, bevor Sie mit der Implementierung
beginnen.
Am zweiten Praktikumstag werden Bilddateien von Karten und Spielsteinen diverser Spiele
zu Verfügung gestellt.
Außerdem wird erläutert, wie Sie diese in Ihrem Programm laden können, sodass die Ausführung
über das Netzwerk funktioniert, auch wenn die Dateien nicht auf den anderen PCs
an gleicher Stelle zur Verfügung stehen.

Überlegen Sie, wie sie schrittweise vorgehen können.
Spätestens nach zwei Stunden programmieren, sollte es möglich sein, geschriebenen Code
auszuführen und anhand dessen die Funktion zu überprüfen.
Vermeiden Sie stundenlanges Programmieren, ohne über ausführbaren Code zu verfügen,
weil dies das Risiko birgt, dass sich so viele Fehler ansammeln oder man einen
Denkfehler begeht, sodass sich der Code nicht mehr korrigieren lässt.
