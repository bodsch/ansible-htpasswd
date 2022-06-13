
# Ansible Role:  `htpasswd`

An Ansible Role to handle credentials over `htpasswd` for webservers like nginx.

[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/bodsch/ansible-htpasswd/CI)][ci]
[![GitHub issues](https://img.shields.io/github/issues/bodsch/ansible-htpasswd)][issues]
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/bodsch/ansible-htpasswd)][releases]

[ci]: https://github.com/bodsch/ansible-htpasswd/actions
[issues]: https://github.com/bodsch/ansible-htpasswd/issues?q=is%3Aopen+is%3Aissue
[releases]: https://github.com/bodsch/ansible-htpasswd/releases


## Requirements & Dependencies

- None

### Operating systems

Tested on

* ArchLinux
* Debian based
    - Debian 10 / 11
    - Ubuntu 20.04
* RedHat based
    - Alma Linux 8
    - Rocky Linux 8
    - OracleLinux 8

## configuration

### default

```yaml
htpasswd_credentials: {}

htpasswd_list_users: true
```

### credentials

see also [molecule tests](molecule/default/group_vars/all/vars.yaml)

```yaml
htpasswd_credentials:
  admin:
    password: ZRhgqhaAjdbuFXj2PLJTzYy5PrRsStNaeYWd9c3Ze3
    path: /etc/nginx/.admin-passwdfile

  administrator:
    password: gp!tk<r+JcDyJhV5!tgzZVUWx233HLVZMJUy<YNVPZ
    path: /etc/nginx/.admin-passwdfile
    crypt_scheme: apr_md5_crypt
```

---

## Author and License

- Bodo Schulz

## License

[Apache](LICENSE)

`FREE SOFTWARE, HELL YEAH!`
