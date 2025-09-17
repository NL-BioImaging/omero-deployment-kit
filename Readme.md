---
OMERO Deployment Kit

---

# What's This For?
This is a deployment solution for OMERO designed for research institutions that require production-ready OMERO server with minimal hassle. By using Ansible to configure the server and pull OME Docker containers, this deployment kit provides the best of both worlds: infrastructure automation with upstream compatibility.

OMERO deployments would typically involve downloading official OME Ansible playbooks and customising them for institutional requirements. This approach creates significant maintenance challenges: customised playbooks increasingly diverge from the upstream repository, making it difficult to incorporate updates, security patches, and improvements from OME.

Recognising these challenges, the OME team has developed excellent Docker-based solutions that provide clean separation between the OMERO application and deployment infrastructure. This deployment kit builds on OME's containerisation work by providing deployment automation to meet institutional infrastructure requirements (SSL certificates, LDAP integration, improved user namespace isolation, and pre-configured web applications).

# What Does OMERO Deployment Kit Do?
- 🐳 Sets up server and web components using OME Docker images
- 🔒 Installs and configures Nginx reverse proxy with certificate management  
- 🔐 Automatically sets up certificate trust stores for secure LDAP, OMERO Insight and API connections
- 🎨 Pre-configures omero-web plugins, including Pathviewer and Omero figure
- 🗄️ Optionally restores a database from an existing OMERO server and attaches network storage
- 🧪 Provides test deployments using self-signed certificates
- 🔑 Generates CSRs for production certificate management

# What Does OMERO Deployment Kit Not Do?
It does not provide a 'one for all' deployment and there is no conditional logic. For example, if you would like to deploy OMERO with LDAP integration, you should:
   - in `roles/docker/templates/server_conf.omero.j2`, change `config set omero.ldap.config false` --> `true`
   - uncomment the LDAP config variables directly below that line
   - update "{{ vault_ldap_base }}, "{{ vault_ldap_filter }}", "{{ vault_ldap_password }}", "{{ vault_ldap_urls }}", "{{ vault_ldap_username }}" and {{ vault_domain_controllers }}" in `vault.yml`  
The playbook is designed to make all customisations straightforward!

# How can I Use and Customise OMERO Deployment Kit?
This repository uses a branch-per-institution approach. Each institution should create and maintain their own branch with their specific configuration (LDAP settings, custom plugins, institutional branding, etc.). This allows sharing of institutional expertise while keeping deployments maintainable and avoiding complex conditional logic in the playbooks. 

# Quick Start With maastricht-test

The **maastricht-test branch** is designed for immediate testing with auto-generated self-signed certificates. It can also serve as a minimal version from which to build on.

1. **Request to join the NL-BioImaging GitHub organisation** via Issues or Discussions
> see *Requesting access...* section below for how to use this kit without write access to the repo
2. **Clone and use maastricht-test** (default branch):
   ```bash
   git clone https://github.com/NL-BioImaging/omero-deployment-kit
   cd omero-deployment-kit
   ```

3. **Create your own branch** (maastricht branches are PR-protected):
   ```bash
   git checkout -b your-institution-test
   ```
4. **Update deployment branch in hosts.yml to your branch name** 
5. **Configure if required:**
   - Copy `vault.yml.example` to `vault.yml` and fill in the variables.
   - After filling in the variables, **encrypt**:
   ```bash
   ansible-vault encrypt vault.yml
   ```

5. **Push your branch to remote**
 
7. **Deploy:**
   ```bash
   ansible-playbook playbook.yml
   ```

OMERO will be running. There's no need to restart the host.

# Production Deployment
For production deployments, create a custom branch from an existing configuration:

## 1. Choose Your Starting Point

```bash
# Start from Maastricht's configuration 
git clone https://github.com/NL-BioImaging/omero-deployment-kit
cd omero-deployment-kit
git checkout maastricht-university
git checkout -b your-institution

# OR start from another institution's branch
git checkout other-university
git checkout -b your-institution

# OR start from test-localhost (minimal setup - build your own!)
git checkout test-localhost
git checkout -b your-institution
```

## 2. Configure Settings
1. Update deployment variables at the top of `hosts.yml` to point to your branch.
2. Optionally, for access from The Internet, update `server_name` in `hosts.yml` and configure your External firewalling.
3. Customise OMERO server configuration in `roles/docker/templates/server_conf.omero.j2`
4. Customise OMERO web configuration in `roles/docker/templates/web_conf.omero.j2`
5. Customise web plugins by editing `roles/docker/templates/Dockerfile-web`
6. Set variables in vault.yml.example and save as vault.yml
7. **Encrypt your vault Before committing:** `ansible-vault encrypt vault.yml`
8. Push your changes to your remote branch

## 3. Deploy to Production

```bash
ansible-playbook playbook.yml
```

## 4. SSL Certificate Management
maastricht-university branch uses this workflow for deployment and renewal of certificates:

1. **On initial deployment** of the server, Ansible will:
   - Generate a private key on the server; `/etc/ssl/private/omero.key`
   - Generate a Certificate Signing Request (CSR)
   - Place the CSR in `(~/omero-deployment-kit/)ssl/omero.csr` 
2.  **When required** simply send `omero.csr` from omero-deployment-kit to your CA
3. **To Renew or install the signed certificate**:
   - Place the certificate in `(~/omero-deployment-kit/)ssl/omero.pem` on the machine running ansible.
   - Commit and publish changes to Remote
   - run `ansible-playbook playbook` again.

>also see `ssl/README.md` for more information

# Requesting access and contributing your Institution's Configuration
Request write access to the repo via [GitHub Issues](https://github.com/NL-BioImaging/omero-deployment-kit/issues) or [Discussions](https://github.com/orgs/NL-BioImaging/discussions). Other institutions will then be able to use your configuration as a starting point. This collaborative approach helps the entire OMERO community benefit from shared expertise while providing you with a maintainable deployment that stays current with upstream OME releases. If you would like to use the playbook without requesting write access, feel free to fork, but keep in mind that doing so fragments this effort somewhat. If your new repo is private, you can use the following task in your base role and add your server's public key as a deploy key to your repo.

```yaml
- name: Clone omero-deployment-kit repository
  git:
    repo: "{{ deployment_repo }}"
    dest: "{{ ansible_user_dir }}/omero-deployment-kit"
    version: "{{ deployment_branch }}"
    force: yes
    key_file: "{{ ansible_user_dir }}/.ssh/[id]"
    accept_hostkey: yes
```
>*where [id] is your private key*

# Database Migration (Advanced)
If you would like to restore the database from an existing OMERO server, place the sql dump here: `backups/restore_omero_from_dump.sql`. This will trigger the migration role when the playbook is ran. See the playbook for implementation details. You will also need to attach existing storage and point to it via the 'vault_NFS_fullpath' variable. Have a look at the "mount HNAS HDS NFS exports" task in the base role; you may need to ammend this task. Only attempt the migration if you know what you are doing. Backup all data and the database (and be sure you can restore it!) before the migration.

# Prerequisites
- Ubuntu/Debian server with SSH access
- Ansible installed on your local machine
