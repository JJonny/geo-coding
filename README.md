### Preparation

`python app/utils/create_project_folders.py` - Creating the necessary directories with access permissions.
- ./data/db
- ./uploads

---
### Testing.

**[file-name]** - your csv file for uploading.
`curl -X POST -F "file=@[file-name.csv]" http://127.0.0.1:5000/api/calculateDistance`

**[task_id]** - task_id getting after uploading file.
`curl -X POST -F "file=@[file-name.csv]" http://127.0.0.1:5000/api/getResults/[task_id]`

