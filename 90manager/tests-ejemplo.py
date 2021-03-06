#!/usr/bin/python
"""
Copyright 2017 by
    * Juan Miguel Lechuga Pérez
    * Jose Luis López Pino
    * Carlos Antonio Rivera Cabello

 This file is part of 90Manager.

    90Manager is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    90Manager is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with 90Manager.  If not, see <http://www.gnu.org/licenses/>.

Tests creation and use of a single user
"""

from django.contrib.auth.models import User
from django.test import TestCase


class UserTestCase(TestCase):
    def set_up(self):
        self.uno = User.objects.create(email="este@ema.il", password='unpass')
        self.otro = User.objects.create(email="este@ema.il", password='otro')

    def test_put(self):
        self.uno.put()
        self.uno.toggle_active()
        self.assertEqual(self.uno.is_active(), 'Putting one')
        self.assertRaises(self.otro.put, TypeError)
