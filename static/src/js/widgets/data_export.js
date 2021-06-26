odoo.define('web.DataExportOverride', function (require) {
    "use strict";
    var core = require('web.core');
    var _t = core._t;
    var framework = require('web.framework');
    var pyUtils = require('web.py_utils');
    var DataExportParent = require('web.DataExport');
    var Dialog = require('web.Dialog');

var DataExport = DataExportParent.include({
    template: 'ExportDialog',
    _exportData(exportedFields, exportFormat, idsToExport) {
     if (_.isEmpty(exportedFields)) {
            Dialog.alert(this, _t("Please select fields to export..."));
            return;
        }
        if (this.isCompatibleMode) {
            exportedFields.unshift({ name: 'id', label: _t('External ID') });
        }
        framework.blockUI();
    var data_to_print = JSON.stringify({
                    model: this.record.model,
                    fields: exportedFields,
                    ids: idsToExport,
                    domain: this.domain,
                    groupby: this.groupby,
                    report_name: this.report_name,
                    context: pyUtils.eval('contexts', [this.record.getContext()]),
                    import_compat: this.isCompatibleMode,
                })
    if(exportFormat=='xlsx' || exportFormat=='csv'){
        this.getSession().get_file({
            url: '/web/export/' + exportFormat,
            data: {
                data: data_to_print
            },
            complete: framework.unblockUI,
            error: (error) => this.call('crash_manager', 'rpc_error', error),
        });
    }else{
        {
            var self = this;
            var id = null
            if (this.value) {
                id = this.value;
            }
                    this._rpc({
                        model: "report.tree.view.pdf.printer",
                        method: "PrintDictionary",
                        args: [id, data_to_print],
                    }).then(function (result) {
                        self.do_action(result);
                    });
        }
    }
    },
    _addField: function (fieldID, label) {
        var $fieldList = this.$('.o_fields_list');
        if (!$fieldList.find(".o_export_field[data-field_id='" + fieldID + "']").length) {
            var li =  $('<li>', {'class': 'o_export_field', 'data-field_id': fieldID});
            li.attr('contentEditable',true);
            var editable_label = $('<span>', {'class': "fa fa-arrows o_short_field mx-1"});
            editable_label.attr('contentEditable',false);
            var movable_label = $('<span>', {'class': " o_short_field mx-1"});
            movable_label.append(editable_label);
            movable_label.attr('contentEditable',false);
            $fieldList.append(
                li.append(
                    movable_label,
                    label,
                    $('<span>', {'class': 'fa fa-trash m-1 pull-right o_remove_field', 'title': _t("Remove field")})
                )
            );
        }
    },
    _onExportData() {
        let exportedFields = this.$('.o_export_field').map((i, field) => ({
                name: $(field).data('field_id'),
                label: field.textContent,
            }
        )).get();
        let exportFormat = this.$exportFormatInputs.filter(':checked').val();
        if (exportFormat=='pdf'){
           var report_name = prompt("Please, enter the name of the report:", "e.g., Reports");
           this.report_name = report_name;
        }

        this._exportData(exportedFields, exportFormat, this.idsToExport);

    },
     init: function () {
            this._super.apply(this, arguments);
            this.report_name='';
     },

});
return {
    DataExport: DataExport,
};
})