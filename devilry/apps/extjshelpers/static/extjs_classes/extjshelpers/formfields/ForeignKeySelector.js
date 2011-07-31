Ext.define('devilry.extjshelpers.formfields.ForeignKeySelector', {
    extend: 'Ext.form.field.ComboBox',
    alias: 'widget.foreignkeyselector',
    requires: [
        'devilry.extjshelpers.models.Node'
    ],

    config: {
        valueField: 'id',
        displayTpl: '{id}',
        emptyText: 'Select something',
        dropdownTpl: '{id}'
    },

    constructor: function(config) {
        this.initConfig(config);
        this.callParent([config]);
    },

    initComponent: function() {
        var me = this;
        Ext.apply(this, {
            store: Ext.create('Ext.data.Store', {
                model: 'devilry.extjshelpers.models.Node',
                remoteFilter: true,
                remoteSort: true,
                autoSync: true,
                autoLoad: true,
                listeners: {
                    scope: this,
                    load: this.onStoreLoad
                },
            }),

            listConfig: {
                loadingText: 'Loading...',
                emptyText: 'No matching items found.',
                getInnerTpl: function() {
                    return me.dropdownTpl;
                }
            }
        });
        this.callParent(arguments);
    },

    onStoreLoad: function(store, records, successful) {
        if(successful) {
            console.log('storeLoaded');
            var form = this.up('form');
            record = form.getRecord();
            //var fields = form.getForm().getFields();
            //var field = fields.filter('name', fieldname).items[0];
            //field.setValue(records[0].data[fieldname]);
            console.log(record.data.parentnode);
            this.setValue(records[0]);
        } else {
            throw "Failed to load store for foreign key."
        }
    },

    /** Display ``this.displayTpl`` if any selection, or ``this.emptyText`` if
     * no selection. */
    setValue: function(value, doSelect) {
        value = Ext.Array.from(value);
        this.callParent(value, doSelect);
        if(value.length > 0) {
            var record = value[0];
            this.displayTplData = record.data;
            this.setRawValue(this.getDisplayValue());
        } else {
            this.setRawValue(this.emptyText);
        }
    }
});
