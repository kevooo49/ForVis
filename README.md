# ForVis

# Wymagania wstępne:

1. **Zainstalowany Docker oraz Docker Compose**
   - Instrukcja instalacji Docker na Ubuntu 16.04: 
     [DigitalOcean Tutorial](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04)
   - Instalacja Docker Compose:
     ```bash
     sudo apt install docker-compose
     ```
   - Instalacja Node.js i npm:
     ```bash
     sudo apt install nodejs
     sudo apt install npm
     ```

2. **Wyłączenie serwera Apache, jeśli działa:**
   ```bash
   sudo pkill apache
   ```

---

# Instrukcja uruchomienia systemu:

1. **Budowanie plików frontendowych:**
   Z katalogu `frontend/formulavis` wykonaj:
   ```bash
   npm install
   npm run build
   ```

2. **Uruchomienie systemu z folderu z plikiem `docker-compose.yml`:**
   - Standardowe uruchomienie:
     ```bash
     docker-compose up
     ```
   - Jeśli wymagane są uprawnienia administratora:
     ```bash
     sudo docker-compose up
     ```

3. **Uniknięcie błędów z plikami:**
   Wykonaj poniższą komendę:
   ```bash
   sudo chmod 777 _files
   ```

---

# Rozwiązywanie problemów:

### 1. **Błąd "Got permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock":**
   Ustaw odpowiednie uprawnienia:
   ```bash
   sudo chmod 666 /var/run/docker.sock
   ```

### 2. **Błąd związany z działającymi serwisami (np. nginx, postgres):**
   Wyłącz działające serwisy:
   ```bash
   sudo service nginx stop
   sudo service postgres stop
   ```

### 3. **Błąd "version in ... unsupported":**
   W pliku `docker-compose.yml` zmień wersję z `3` na `2`.

### 4. **Błąd związany z usługą nginx lub frontendem:**
   Postępuj zgodnie z poniższymi krokami:
   1. Zatrzymaj system:
      ```bash
      CTRL + C lub docker-compose stop
      ```

   2. W sekcji `frontend` pliku `docker-compose.yml` dodaj opcję:
      ```yml
      command: npm install --no-optional
      ```

   3. Uruchom system ponownie:
      ```bash
      docker-compose up
      ```

   4. Po ponownym wystąpieniu błędu frontend, zatrzymaj system:
      ```bash
      docker-compose stop
      ```

   5. Usuń wcześniej dodaną opcję w sekcji `frontend` w pliku `docker-compose.yml`.

   6. Uruchom system ponownie:
      ```bash
      docker-compose up
      ```

---

# Dane administratora:

- Login: `admin`
- Hasło: `admin`

---

# Dostęp do systemu:

1. **Strona główna projektu:**
   Wpisz w przeglądarce:
   ```txt
   localhost
   ```

2. **Panel administratora:**
   Wpisz w przeglądarce:
   ```txt
   localhost:8000/admin/
   ```

---

# **DEVELOPMENT**

   first terminal window:
   ```bash
   cd forvis-frontend
   ng serve --host 0.0.0.0 --port 4200
   ```

   second terminal window:
   ```bash
   docker-compose -f docker-compose.dev.yml up --build
   ```



**Uwagi dodatkowe:**
- System może wymagać kilku sekund na pełne uruchomienie.
- Powyższe instrukcje są zoptymalizowane dla Ubuntu 16.04, ale mogą działać również na nowszych wersjach systemu.
