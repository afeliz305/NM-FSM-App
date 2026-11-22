# Flask Students Management App

This is a simple Flask web application to manage students' information using a SQLite database and SQLAlchemy for database interactions. The app allows you to:
- View all student records
- Add new student records

## Features
- **CRUD Operations**: Add and view student records.
- **Flask SQLAlchemy**: Database ORM for managing data.
- **SQLite**: Local database for development.
- **Bootstrap**: For basic styling of the web interface.

---

## Tech Stack
- **Frontend**: HTML, CSS (with Bootstrap)
- **Backend**: Python (Flask Framework)
- **Database**: SQLite (local development)


---

## Installation Guide

### Prerequisites
- Python 3.8 or later
- pip (Python package manager)

### Steps to Run Locally
1. Clone the repository:
   ```bash
   git clone https://github.com/Qoslaye/flask-students-Management-app.git
   cd flask-students-Management-app


   ---
## 📸 Screenshot
---
<img width="928" alt="1" src="https://github.com/user-attachments/assets/0eaf44c0-5e9c-4337-bc98-f2b692ffa5c0">
<img width="926" alt="2" src="https://github.com/user-attachments/assets/cc6c3dec-3f87-49c9-b955-04313813c92c">
<img width="940" alt="3" src="https://github.com/user-attachments/assets/fc522675-b620-44b1-a843-48b9aedc642a">

---

## Feature Flags

### `ENABLE_MAJOR_FIELD`

Toggles the **Major** column in the student list and form.

| Environment | Default Value |
|-------------|---------------|
| staging     | `true`        |
| production  | `true`        |

**Terraform variable** (in `devops-course/terraform/variables.tf`):
```hcl
variable "enable_major_field" {
  type    = map(string)
  default = {
    staging    = "true"
    production = "true"
  }
}
```

**ECS environment injection** (in `devops-course/terraform/ecs.tf`):
```hcl
{
  name  = "ENABLE_MAJOR_FIELD"
  value = var.enable_major_field[terraform.workspace]
}
```

**Running locally with flag enabled:**
```bash
set ENABLE_MAJOR_FIELD=true
python app.py
```

**Test coverage:**
- `tests/http/` – parametrized tests verifying form field (`name="major"`) and list column (`<th>Major</th>`) visibility for both flag values, plus POST persistence.
- `tests/integration/test_student_db.py` – two tests verifying DB inserts with and without a major value.
