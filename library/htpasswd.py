#!/usr/bin/python

# Copyright (c) 2013, Nimbis Services, Inc.
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import os
import tempfile
from typing import Any, Tuple

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.bodsch.core.plugins.module_utils.passlib_bcrypt5_compat import (
    apply_passlib_bcrypt5_compat,
)
from ansible_collections.community.general.plugins.module_utils import deps

DOCUMENTATION = r"""
module: htpasswd
author:
    - "Ansible Core Team"
    - "Bodo 'bodsch' Schulz <bodo@boone-schulz.de>"

extends_documentation_fragment:
  - ansible.builtin.files
  - community.general.attributes

short_description: Manage user files for basic authentication

description:
  - Add and remove username/password entries in a password file using htpasswd.
  - This is used by web servers such as Apache and Nginx for basic authentication.
  - Implements monkey patch for bcrypt 5

attributes:
  check_mode:
    support: full
  diff_mode:
    support: none
options:
  path:
    type: path
    required: true
    aliases: [dest, destfile]
    description:
      - Path to the file that contains the usernames and passwords.
  name:
    type: str
    required: true
    aliases: [username]
    description:
      - User name to add or remove.
  password:
    type: str
    description:
      - Password associated with user.
      - Must be specified if user does not exist yet.
  hash_scheme:
    type: str
    default: "apr_md5_crypt"
    description:
      - Hashing scheme to be used. As well as the four choices listed here, you can also use any other hash supported by passlib,
        such as V(portable_apache22) and V(host_apache24); or V(md5_crypt) and V(sha256_crypt), which are Linux passwd hashes.
        Only some schemes in addition to the four choices below are compatible with Apache or Nginx, and supported schemes
        depend on C(passlib) version and its dependencies.
      - See U(https://passlib.readthedocs.io/en/stable/lib/passlib.apache.html#passlib.apache.HtpasswdFile) parameter C(default_scheme).
      - 'Some of the available choices might be: V(apr_md5_crypt), V(des_crypt), V(ldap_sha1), V(plaintext).'
      - 'B(WARNING): The module has no mechanism to determine the O(hash_scheme) of an existing entry, therefore, it does
        not detect whether the O(hash_scheme) has changed. If you want to change the scheme, you must remove the existing
        entry and then create a new one using the new scheme.'
    aliases: [crypt_scheme]
  state:
    type: str
    choices: [present, absent]
    default: "present"
    description:
      - Whether the user entry should be present or not.
  create:
    type: bool
    default: true
    description:
      - Used with O(state=present). If V(true), the file is created if it does not exist. Conversely, if set to V(false) and
        the file does not exist, it fails.
notes:
  - This module depends on the C(passlib) Python library, which needs to be installed on all target systems.
  - 'On Debian < 11, Ubuntu <= 20.04, or Fedora: install C(python-passlib).'
  - 'On Debian, Ubuntu: install C(python3-passlib).'
  - 'On RHEL or CentOS: Enable EPEL, then install C(python-passlib).'

requirements: [passlib>=1.6]

extends_documentation_fragment:
  - ansible.builtin.files
  - community.general.attributes
"""

EXAMPLES = r"""
- name: Add a user to a password file and ensure permissions are set
  htpasswd:
    path: /etc/nginx/passwdfile
    name: janedoe
    password: '9s36?;fyNp'
    owner: root
    group: www-data
    mode: '0640'

- name: Remove a user from a password file
  htpasswd:
    path: /etc/apache2/passwdfile
    name: foobar
    state: absent

- name: Add a user to a password file suitable for use by libpam-pwdfile
  community.general.htpasswd:
    path: /etc/mail/passwords
    name: alex
    password: oedu2eGh
    hash_scheme: md5_crypt
"""

_PasslibTypes = Tuple[Any, Any, Any]
_cached: _PasslibTypes | None = None


def load_passlib(module) -> _PasslibTypes:
    """
    Lädt passlib sicher zur Laufzeit (nach deps + bcrypt5-compat patch),
    cached das Ergebnis pro Python-Prozess.
    """
    global _cached
    if _cached is not None:
        return _cached

    deps.validate(module)
    apply_passlib_bcrypt5_compat(module)

    from passlib.apache import HtpasswdFile, htpasswd_context  # type: ignore[attr-defined]
    from passlib.context import CryptContext

    _cached = (HtpasswdFile, htpasswd_context, CryptContext)
    return _cached


class HtPasswd:
    """ """

    def __init__(self, module):
        """
        """
        self.module = module

        self.module.log("HtPasswd::__init__()")

        self.path = module.params.get("path")
        self.username = module.params.get("name")
        self.password = module.params.get("password")
        self.hash_scheme = module.params.get("hash_scheme")
        self.state = module.params.get("state")
        self.create = module.params.get("create")

        self.apache_hashes = ["apr_md5_crypt", "des_crypt", "ldap_sha1", "plaintext"]

        self._passlib_cached = None

    def run(self):
        """ """
        self.module.log("HtPasswd::run()")

        # TODO double check if this hack below is still needed.
        # Check file for blank lines in effort to avoid "need more than 1 value to unpack" error.
        try:
            with open(self.path) as f:
                lines = f.readlines()

            # If the file gets edited, it returns true, so only edit the file if it has blank lines
            strip = False
            for line in lines:
                if not line.strip():
                    strip = True
                    break

            if strip:
                # If check mode, create a temporary file
                if self.module.check_mode:
                    temp = tempfile.NamedTemporaryFile()
                    self.path = temp.name

                with open(self.path, "w") as f:
                    f.writelines(line for line in lines if line.strip())

        except OSError:
            # No preexisting file to remove blank lines from
            pass

        try:
            self.module.log(f"  - state: '{self.state}'")

            if self.state == "present":
                (msg, changed) = self.present(
                    self.path,
                    self.username,
                    self.password,
                    self.hash_scheme,
                    self.create,
                    self.module.check_mode,
                )

            elif self.state == "absent":
                if not os.path.exists(self.path):
                    self.module.warn(f"{self.path} does not exist")

                    return dict(
                        failed=False, changed=True, msg=f"{self.username} not present"
                    )
                    # self.module.exit_json(msg=f"{self.username} not present", changed=False)

                (msg, changed) = self.absent(
                    self.path, self.username, self.module.check_mode
                )

                return dict(failed=False, changed=changed, msg=msg)

            else:
                return dict(
                    failed=True, changed=False, msg=f"Invalid state: '{self.state}'"
                )
                # self.module.fail_json(msg=f"Invalid state: '{self.state}'")
                # return  # needed to make pylint happy

            (msg, changed) = self.check_file_attrs(changed, msg)

            return dict(failed=False, changed=changed, msg=msg)

            # self.module.exit_json(msg=msg, changed=changed)

        except Exception as e:
            return dict(failed=True, changed=False, msg=f"{e}")

        return dict(failed=True, msg="development")

    def _passlib(self):
        """ """
        self.module.log("HtPasswd::_passlib()")

        if self._passlib_cached is None:
            self._passlib_cached = load_passlib(self.module)

        return self._passlib_cached

    def create_missing_directories(self, dest):
        """ """
        self.module.log(f"HtPasswd::create_missing_directories({dest})")

        destpath = os.path.dirname(dest)
        if not os.path.exists(destpath):
            os.makedirs(destpath)

    def present(self, dest, username, password, hash_scheme, create, check_mode):
        """Ensures user is present

        Returns (msg, changed)"""
        self.module.log(
            f"HtPasswd::present({dest}, {username}, {password}, {hash_scheme}, {create}, {check_mode})"
        )

        HtpasswdFile, htpasswd_context, CryptContext = self._passlib()

        if hash_scheme in self.apache_hashes:
            context = htpasswd_context
        else:
            context = CryptContext(schemes=[hash_scheme] + self.apache_hashes)

        if not os.path.exists(dest):
            if not create:
                raise ValueError(f"Destination {dest} does not exist")
            if check_mode:
                return (f"Create {dest}", True)

            self.create_missing_directories(dest)
            ht = HtpasswdFile(
                dest, new=True, default_scheme=hash_scheme, context=context
            )
            ht.set_password(username, password)
            ht.save()

            return (f"Created {dest} and added {username}", True)
        else:
            ht = HtpasswdFile(
                dest, new=False, default_scheme=hash_scheme, context=context
            )

            found = ht.check_password(username, password)

            if found:
                return (f"{username} already present. ", False)
            else:
                if not check_mode:
                    ht.set_password(username, password)
                    ht.save()
                return (f"Add/update {username}", True)

    def absent(self, dest, username, check_mode):
        """Ensures user is absent

        Returns (msg, changed)"""
        self.module.log(f"HtPasswd::absent({dest}, {username}, {check_mode})")

        HtpasswdFile, _, _ = self._passlib()

        ht = HtpasswdFile(dest, new=False)

        if username not in ht.users():
            return (f"{username} not present", False)
        else:
            if not check_mode:
                ht.delete(username)
                ht.save()
            return (f"Remove {username}", True)

    def check_file_attrs(self, changed, message):
        """ """
        self.module.log(
            f"HtPasswd::check_file_attrs(changed={changed}, message={message})"
        )

        file_args = self.module.load_file_common_arguments(self.module.params)

        if self.module.set_fs_attributes_if_different(file_args, False):

            if changed:
                message += " and "

            changed = True
            message += "ownership, perms or SE linux context changed"

        return message, changed


def main():
    """ """
    args = dict(
        path=dict(type="path", required=True, aliases=["dest", "destfile"]),
        name=dict(type="str", required=True, aliases=["username"]),
        password=dict(type="str", no_log=True),
        hash_scheme=dict(type="str", default="apr_md5_crypt", aliases=["crypt_scheme"]),
        state=dict(type="str", default="present", choices=["present", "absent"]),
        create=dict(type="bool", default=True),
    )
    module = AnsibleModule(
        argument_spec=args, add_file_common_args=True, supports_check_mode=True
    )

    handler = HtPasswd(module)
    result = handler.run()

    module.log(msg=f"= result : {result}")

    module.exit_json(**result)


if __name__ == "__main__":
    main()
