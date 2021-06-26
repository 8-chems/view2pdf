# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.addons.web.controllers.main import GroupsTreeNode
import operator
import json
import ast
from odoo.tools.safe_eval import safe_eval
import datetime
import re

class ReportTreeViewPdfPrinter(models.Model):
    _name = 'report.tree.view.pdf.printer'
    _description = "MIS Report Template"
    headers = fields.Char(string = 'Headers')
    rows = fields.Char(string = 'Rows')
    name= fields.Char(string = 'Report name')
    period_filter = fields.Char(string = 'Period filter')

    def parse(self, data):
        params = json.loads(data)
        model, fields, ids, domain, report_name, import_compat = \
            operator.itemgetter('model', 'fields', 'ids', 'domain', 'report_name', 'import_compat')(params)
        field_names = [f['name'] for f in fields]
        if import_compat:
            columns_headers = field_names
        else:
            columns_headers = [val['label'].strip() for val in fields]
        Model = self.env[model].with_context(**params.get('context', {}))
        groupby = params.get('groupby')
        if not import_compat and groupby:
            groupby_type = [Model._fields[x.split(':')[0]].type for x in groupby]
            domain = [('id', 'in', ids)] if ids else domain
            groups_data = Model.read_group(domain, [x if x != '.id' else 'id' for x in field_names], groupby, lazy=False)

            # read_group(lazy=False) returns a dict only for final groups (with actual data),
            # not for intermediary groups. The full group tree must be re-constructed.
            tree = GroupsTreeNode(Model, field_names, groupby, groupby_type)
            for leaf in groups_data:
                tree.insert_leaf(leaf)

            response_data = self.from_group_data(fields, tree)
        else:
            Model = Model.with_context(import_compat=import_compat)
            records = Model.browse(ids) if ids else Model.search(domain, offset=0, limit=False, order=False)

            if not Model._is_an_ordinary_table():
                fields = [field for field in fields if field['name'] != 'id']

            export_data = records.export_data(field_names).get('datas',[])

        if (ids):
            period_filter = 'records selected manually'
        else:
            periods = self.parse_domain2period(str(domain))
            if(periods['date_from'] and periods['date_from']):
                period_filter = periods['date_from']+' to '+ periods['date_to']
            else:
                period_filter ='No period filter was specified'

        return {
            'report_name':report_name,
            'export_data':export_data,
            'columns_headers':columns_headers,
            'period_filter':period_filter,
            }

    def parse_domain2period(self, domain):
        date_from = None
        date_from_compiler = re.compile('\'(>|>=)\', \'\d\d\d\d-\d\d-\d\d\'')
        matche_date_from = date_from_compiler.search(domain)
        if (matche_date_from):
            date_from = date_to = re.search('\d\d\d\d-\d\d-\d\d', domain).group(0)

        date_to = None
        date_to_compiler = re.compile('\'(<|<=)\', \'\d\d\d\d-\d\d-\d\d\'')
        matche_date_to = date_from_compiler.search(domain)
        if (matche_date_to):
            date_to = re.search('\d\d\d\d-\d\d-\d\d', domain).group(0)

        return {
            'date_from': date_from,
            'date_to': date_to
        }

    def PrintDictionary(self, args):
        ModelClass = self.env['report.tree.view.pdf.printer']
        response_data = ModelClass.parse(args)
        Instance = ModelClass.create({
            'headers':response_data['columns_headers'],
            'rows': response_data['export_data'],
            'name': response_data['report_name'],
            'period_filter': response_data['period_filter']
         })
        return (
            Instance.env.ref("view2pdf.qweb_pdf_export")
                .report_action(Instance, data=dict(dummy=True))  # required to propagate context
        )

    def parseText(self, text):
        parsed = safe_eval(text)
        return parsed

    def String2Dict(self, text):
        converted = safe_eval(text,{"datetime": datetime})
        return converted

    def isDigit(self, text):
        clean_text= text.replace(' ','')
        valid = True
        try:
            float(clean_text)
        except ValueError:
            valid = False
        return valid
class CustomReport(models.Model):
    _inherit = "ir.actions.report"
    def render_qweb_pdf(self, res_ids=None, data=None):
        if self.report_name == "view2pdf.view_template_printer":
            if not res_ids:
                res_ids = self.env.context.get("active_ids")
            return super(CustomReport,self).render_qweb_pdf(res_ids, data=None)
        return super(CustomReport, self).render_qweb_pdf(res_ids, data)




