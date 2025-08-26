# Instrukcije za ubacivanje postojeće baze podataka

## Korak 1: Priprema baze podataka

1. **Kopirajte vašu postojeću `db.sqlite3` datoteku** na VPS server
2. **Postavite je u `/opt/todo/` direktorijum**

## Korak 2: Ubacivanje baze u Docker kontejner

```bash
# Idite u direktorijum aplikacije
cd /opt/todo

# Zaustavite Docker kontejnere
docker-compose down

# Kopirajte bazu u Docker volume
docker volume create todo_sqlite_data
docker run --rm -v todo_sqlite_data:/app -v $(pwd)/db.sqlite3:/app/db.sqlite3 alpine cp /app/db.sqlite3 /app/

# Pokrenite kontejnere ponovo
docker-compose up -d
```

## Korak 3: Provera da li je baza uspešno ubacena

```bash
# Proverite da li aplikacija radi
docker-compose logs web

# Pristupite admin panelu
# Idite na: https://todo.emikon.rs/admin
```

## Korak 4: Ako je potrebno, pokrenite migracije

```bash
# Ako je potrebno, pokrenite migracije
docker-compose exec web python manage.py migrate
```

## Napomene

- **NE menjajte bazu tokom deployment-a** - sve promene će biti izgubljene
- **Backup se radi automatski** svaki dan u 2:00
- **Baza se čuva u Docker volume-u** `todo_sqlite_data`
- **Ako trebate da pristupite bazi direktno:**
  ```bash
  docker-compose exec web sqlite3 /app/db.sqlite3
  ```
