python app/utils/create_project_folders.py для создания необходимых директорий и правк у ним.
./data/db
./uploads

---
Для тестирования

curl -X POST -F "file=@[file-name].csv" http://127.0.0.1:5000/api/calculateDistance
