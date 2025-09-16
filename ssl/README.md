---
SSL Certificate Management for OMERO Deployment Kit
---

# Certificate Workflow

## Initial Deployment
On first run, the playbook will:

1. Generate `/etc/ssl/private/omero.key`
   - This private key NEVER leaves the server and is NEVER committed to the repository
   
2. Generate a Certificate Signing Request (CSR), `omero.csr`, from the private key and place in this directory
   - Send this CSR to your Certificate Authority to get it signed

3. Disable nginx

4. Skip further encryption tasks.

## Installing Your Signed Certificate
Once you receive the signed certificate from your CA:

1. Place the signed certificate in this directory as `omero.pem`
2. Commit and push the certificate to your institutions's branch
3. Re-run the playbook.
   - `omero.pem` will be detected and installed
   - The PKCS#12 bundle needed for OMERO Insight and API connections will be created
   - nginx will be enabled and started

## Certificate Renewal
To renew your certificate:
1. The existing CSR (`omero.csr`) can be reused, however,
2. If you prefer not to reuse, you can trigger the gereration of a new key and CSR by deleting `/etc/ssl/private/omero.key`
2. Get the certificate signed by your CA
3. Replace `omero.pem` with the new certificate
4. Re-run the Ansible playbook

# Security Notes
- Private keys are NEVER stored in this repository
- CSRs are gitignored - they contain no sensitive information but don't need to be committed
- **Only signed certificates (omero.pem) should be committed to the repository**
- The `.gitignore` is configured to exclude private keys and CSRs

# Test Deployments
For test deployments certificates are auto-generated and this directory is not used.