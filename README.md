
# Ansible Role:  `htpasswd`

An Ansible Role to handle credentials over `htpasswd` for webservers like nginx.

[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/bodsch/ansible-htpasswd/main.yml?branch=main)][ci]
[![GitHub issues](https://img.shields.io/github/issues/bodsch/ansible-htpasswd)][issues]
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/bodsch/ansible-htpasswd)][releases]
[![Ansible Quality Score](https://img.shields.io/ansible/quality/50067?label=role%20quality)][quality]

[ci]: https://github.com/bodsch/ansible-htpasswd/actions
[issues]: https://github.com/bodsch/ansible-htpasswd/issues?q=is%3Aopen+is%3Aissue
[releases]: https://github.com/bodsch/ansible-htpasswd/releases
[quality]: https://galaxy.ansible.com/bodsch/htpasswd


## Requirements & Dependencies

- `passlib>=1.6`

### Operating systems

Tested on

* ArchLinux
* Debian based
    - Debian 10 / 11
    - Ubuntu 20.04


## configuration

### default

```yaml
htpasswd_credentials_path: /etc/nginx

htpasswd_credentials: []

htpasswd_list_users: true
```

### credentials

see also [molecule tests](molecule/default/group_vars/all/vars.yaml)

```yaml
htpasswd_credentials:
  - path: "{{ htpasswd_credentials_path }}/.admin-passwdfile"
    mode: "u=rw,g=r,o-r"
    owner: "www-data"
    users:
    - username: admin
      password: ZRhgqhaAjdbuFXj2PLJTzYy5PrRsStNaeYWd9c3Ze3
    - username: administrator
      password: gp!tk<r+JcDyJhV5!tgzZVUWx233HLVZMJUy<YNVPZ
      state: absent
      # https://docs.ansible.com/ansible/latest/collections/community/general/htpasswd_module.html#parameter-crypt_scheme
      # available choices might be: apr_md5_crypt, des_crypt, ldap_sha1, plaintext
      crypt_scheme: plaintext

  - path: "{{ htpasswd_credentials_path }}/.monitoring-passwdfile"
    users:
    - username: monitoring
      password: gp!tk<r+JcDyJhV5!tgzZVUWx233HLVZMJUy<YNVPZ
      crypt_scheme: des_crypt
```

---

## Author and License

- Bodo Schulz

## License

[Apache](LICENSE)

**FREE SOFTWARE, HELL YEAH!**
