# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
import logging
from datetime import date

_logger = logging.getLogger(__name__)

class account_third_check(osv.osv):
    """ Account Third Check """
    _name = "account.third.check"
    _inherit = "account.third.check"

    def _send_mail_overdue_checks(self, cr, uid, ids=[], context=None):

        mail_mail = self.pool.get('mail.mail')

	admin_id = self.pool.get('res.users').search(cr,uid,[('login','=','admin')])
	if not admin_id:
		logging.getLogger(__name__).error('No admin user present in the system, contact your system administrator')
		return None
	for admin in self.pool.get('res.users').browse(cr,uid,admin_id):
		admin_email = admin.partner_id.email

	group_id = self.pool.get('res.groups').search(cr,uid,[('name','=','Financial Manager')])
	if not group_id:
		logging.getLogger(__name__).error('No Financial Manager group present in the system, contact your system administrator')
		return None
	user_ids = self.pool.get('res.users').search(cr,uid,[('groups_id','in',group_id)])
	finance_emails = []
	for finance_user in self.pool.get('res.users').browse(cr,uid,user_ids):
		finance_emails.append(finance_user.partner_id.email)

	now = date.today()
	args = [('state','=','holding'),('clearing_date','>=',str(now))]
	check_ids = self.pool.get('account.third.check').search(cr,uid,args)

	email_body = '<body><h3>Cheques a depositar</h3><table>'	
	for check in self.pool.get('account.third.check').browse(cr,uid,check_ids):
		email_body = email_body + '<tr><td>Banco %s,</td>'%(check.bank_id.name)
		email_body = email_body + '<td> nro. de cheque %s,</td>'%(check.number)
		email_body = email_body + '<td> para la fecha %s,</td>'%(check.clearing_date)
		email_body = email_body + '<td> y el monto de %f</td>'%(check.amount)
		email_body = email_body + '</tr>'
		
	email_body = email_body + '</body>'
	
	mail_ids = []
	for fin_email in finance_emails:
	        mail_ids.append(mail_mail.create(cr, uid, {
        	               'email_from': str(admin_email),
                	       'email_to': str(fin_email),
	                       'subject': 'Cheques pendientes de depositar',
        	               'body_html': '<p>%s</p>' % (email_body)}, context=context))

	return None

account_third_check()

