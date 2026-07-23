# Sprint 0 – Contractul Primei Pagini (First Screen Contract)
*Status: Activ, certificat sub Checkpoint OMEGA v2.0*

---

## 1. Principiul de Dezvoltare
> **Niciun sprint nu începe cu baza de date, API-ul sau codul. Fiecare sprint începe cu ecranul pe care îl vede omul și se termină când omul îl poate folosi.**

---

## 2. Ce vede omul în primele 30 de secunde (Ecranul „Astăzi”)

> **Bună dimineața, Nic.**  
>   
> Ai rămas aici:  
> * Aseară ai lucrat la identitatea NicMar OS.  
> * A rămas deschisă decizia despre Sprint 0.  
> * Ai promis că astăzi alegi prima funcționalitate.  
>   
> Astăzi cred că merită să faci aceste trei lucruri:  
> 1. Finalizează prima victorie pentru Sprint 0.  
> 2. Testează salvarea unei idei noi.  
> 3. Continuă discuția despre memoria platformei.  
>   
> Ai nevoie de ceva?  
> 🔍 Găsește o conversație  
> 💡 Salvează o idee  
> 💬 Întreabă-mă ceva

---

## 3. De unde vine fiecare informație? (Sursa datelor)
* **„Ai rămas aici”** $ightarrow$ Se extrage automat din memoria conversațiilor recente / sesiune anterioară.
* **„Decizii / Lucruri deschise”** $ightarrow$ Se extrag din stările marcate ca nerezolvate în ziua precedentă.
* **Cele 3 lucruri recomandate** $ightarrow$ Priorități generate din contextul activ și promisiunile salvate.
* **Butonatele de acțiune rapidă** $ightarrow$ Comenzi directe către căutare, captură și asistent.

---

## 4. Ce trebuie construit tehnic (Back-to-Front)
Pentru ca acest ecran să existe și să poată fi folosit mâine, dezvoltarea livrează:
1. **Un vizualator simplu (UI Web Minimalist):** O singură pagină curată, fără meniuri încărcate, construită exclusiv în jurul textului de întâmpinare.
2. **Un suport de memorie locală:** Un fișier sau o structură JSON ușoară unde citim contextul de ieri și scriem prioritățile de azi.
3. **Câmpul de Captură Rapidă:** Un mecanism care preia un gând tastat și îl salvează instant în jurnalul zilei.
