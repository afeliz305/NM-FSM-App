# terraform.tfvars actual values
# Overrides defaults in variables.tf
# Committed to Git (no secrets here)
# ── Environment IPs and DB credentials ──
# db_ip defaults in variables.tf - no override needed
db_name = "fsm_db"
db_user = "flaskapp"
# db_password NOT stored here (never put passwords in files)
# Setup-DevOps-Environment.ps1 populated the password in the appropriate environment variable (TF_VAR_db_password) during assignment #1
