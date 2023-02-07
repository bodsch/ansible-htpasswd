# python 3 headers, required if submitting to Ansible

from __future__ import (absolute_import, print_function)
__metaclass__ = type

from ansible.utils.display import Display

display = Display()


class FilterModule(object):
    """
        Ansible file jinja2 tests
    """

    def filters(self):
        return {
            'validate': self.validate,
            'report': self.report,
        }

    def validate(self, data):
        """
        """
        valid = []
        non_valid = []

        if isinstance(data, list):
            for d in data:
                htpwd_path = d.get("path", None)
                htpwd_users = d.get("users", None)

                if htpwd_users:
                    for u in htpwd_users:
                        username = u.get("username", None)
                        password = u.get("password", None)

                        if username and password:
                            valid.append(d)
                        else:
                            msg = f"username and/or password for the path are missing ({htpwd_path})."
                            non_valid.append(msg)

        result = dict(
            valid_entries = valid,
            non_valid_msg = non_valid
        )
        # display.v(f"= result: {result} {type(result)}")

        return result

    def report(self, data):
        """
        """
        result = []

        if isinstance(data, list):
            for d in data:
                changed = d.get("changed", False)
                # state = d.get("state", False)
                # failed = d.get("failed", False)
                msg = d.get("msg", False)

                if changed:
                    result.append(msg)

        return result
