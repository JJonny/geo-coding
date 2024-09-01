### Preparation

### 1. Create and run venv
    `python3 -m venv .venv`
    `source .venv/bin/activate`
    `pip install -U pip`
    `pip install -r requirements.txt`

### 2. Creating the necessary directories with access permissions.
    `python create_project_folders.py` 
    
    ./data/db
    ./uploads

### 3. Run docker services
    `docker-compose up -d `

### 4. Apply migrations
    `alembic upgrade head`

---
### Testing.

#### POST
**[file-name]** - your csv file for uploading.
```
curl -X POST -F "file=@[file-name.csv]" http://127.0.0.1:5000/api/calculateDistance
```

#### GET
**[task_id]** - task_id getting after uploading file.
```
curl http://127.0.0.1:5000/api/getResult/[task_id]
```

