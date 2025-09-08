# Database Migration
## To Restore a Database Backup During Deployment:
First, please run the ansible playbook once to initialise this omero-deployment-kit. Once that's done, if you are migrating from another OMERO instance, you can place your PostgreSQL database dump file in this directory and name it "restore_omero_from_dump.sql" to trigger the migration role.The migration role only triggers if "restore_omero_from_dump.sql" is placed in `omero-deployment-kit/backups/`. The final task in the migration role renames "restore_omero_from_dump.sql" to "omero_dump.sql.processed". 

## An Alternative: Encrypted Backups in Git or a Secure Remote Source
For single-command deployment, you can encrypt database backups with ansible-vault and commit them to the repository (or use an unencrypted secure remote location), ammend the playbook, and migrate without the manual database placement.

## Creating Backups
Follow the omero documentation: https://omero.readthedocs.io/en/stable/sysadmins/server-backup-and-restore.html

## Important Notes
Database restore will **completely replace** existing database data! This has only been tested as part of an OMERO migration process and is **not** intended to be used for scheduled backup/restore tasks. 