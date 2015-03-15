# Copyright 2014, Tresys Technology, LLC
#
# This file is part of SETools.
#
# SETools is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 2.1 of
# the License, or (at your option) any later version.
#
# SETools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with SETools.  If not, see
# <http://www.gnu.org/licenses/>.
#
from . import qpol
from . import role
from . import mls
from . import symbol


class InvalidUser(symbol.InvalidSymbol):

    """Exception for invalid users."""
    pass


def user_factory(qpol_policy, name):
    """Factory function for creating User objects."""

    if isinstance(name, qpol.qpol_user_t):
        return User(qpol_policy, name)

    try:
        symbol = qpol.qpol_user_t(qpol_policy, name)
    except ValueError:
        raise InvalidUser("{0} is not a valid user".format(name))

    return User(qpol_policy, symbol)


class User(symbol.PolicySymbol):

    """A user."""

    @property
    def roles(self):
        """The user's set of roles."""

        r = set()

        for role_ in self.qpol_symbol.role_iter(self.policy):
            item = role.role_factory(self.policy, role_)

            # object_r is implicitly added to all roles by the compiler.
            # technically it is incorrect to skip it, but policy writers
            # and analysts don't expect to see it in results, and it
            # will confuse, especially for role set equality user queries.
            if item != "object_r":
                r.add(item)

        return r

    @property
    def mls_level(self):
        """The user's default MLS level."""
        return mls.level_factory(self.policy, self.qpol_symbol.dfltlevel(self.policy))

    @property
    def mls_range(self):
        """The user's MLS range."""
        return mls.range_factory(self.policy, self.qpol_symbol.range(self.policy))

    def statement(self):
        roles = list(str(r) for r in self.roles)
        stmt = "user {0} roles ".format(self)
        if (len(roles) > 1):
            stmt += "{{ {0} }}".format(' '.join(roles))
        else:
            stmt += roles[0]

        try:
            stmt += " level {0.mls_level} range {0.mls_range};".format(self)
        except mls.MLSDisabled:
            stmt += ";"

        return stmt
