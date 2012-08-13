Ext.define('devilry.student.browseperiods.AssignmentGrid', {
    extend: 'Ext.grid.Panel',
    alias: 'widget.student-browseperiods-assignmentgrid',

    /**
     * @cfg {Function} [urlCreateFn]
     * Function to call to genereate urls. Takes an AssignmentGroup record as parameter.
     */

    /**
     * @cfg {Object} [urlCreateFnScope]
     * Scope of ``urlCreateFn``.
     */
    
    constructor: function(config) {
        this.createStore();
        this.callParent([config]);
    },

    assignmentTpl: Ext.create('Ext.XTemplate',
        '<a href="{url}">{data.parentnode__long_name}</a>'
    ),

    pointsTpl: Ext.create('Ext.XTemplate', 
        '<span class="pointscolumn">',
        '    <tpl if="feedback">',
        '       {feedback__points}',
        '    </tpl>',
        '    <tpl if="!feedback">',
        '       <span class="nofeedback">&empty;</span>',
        '   </tpl>',
        '</span>'
    ),

    gradeTpl: Ext.create('Ext.XTemplate', 
        '<div class="gradecolumn">',
            '<tpl if="feedback">',
                '<span class="is_passing_grade">',
                    '<tpl if="feedback__is_passing_grade"><span class="passing_grade">',
                        gettext('Passed'),
                    '</span></tpl>',
                    '<tpl if="!feedback__is_passing_grade"><span class="not_passing_grade">',
                        gettext('Failed'),
                    '</span></tpl>',
                    ' (<span class="grade">{feedback__grade}</span>)',
                '</span>',
                //'<div class="delivery_type">',
                    //'<tpl if="feedback__delivery__delivery_type == 0"><span class="electronic">Electronic</span></tpl>',
                    //'<tpl if="feedback__delivery__delivery_type == 1"><span class="non-electronic">Non-electronic</span></tpl>',
                    //'<tpl if="feedback__delivery__delivery_type == 2"><span class="neutralInlineItem">From previous period (semester)</span></tpl>',
                    //'<tpl if="feedback__delivery__delivery_type &gt; 2"><span class="warningInlineItem">Unknown delivery type</span></tpl>',
                //'</div>',
            '</tpl>',
            '<tpl if="!feedback">',
                '<span class="nofeedback">',
                    gettext('No feedback'),
                '</span>',
            '</tpl>',
        '</div>'
    ),

    createStore: function() {
        this.store = Ext.create('Ext.data.Store', {
            model: 'devilry.apps.student.simplified.SimplifiedAssignmentGroup',
            remoteFilter: true,
            remoteSort: false,
            autoSync: true
        });
        this.store.pageSize = 100000;
        //this.store.proxy.setDevilryOrderby(['parentnode__publishing_time', 'parentnode__short_name']);
    },

    loadGroupsInPeriod: function(periodRecord) {
        this.store.proxy.setDevilryFilters([{
            field: 'parentnode__parentnode',
            comp: 'exact',
            value: periodRecord.get('id')
        }])
        this.store.load({
            scope: this,
            callback: function(records, op) {
                this.getEl().unmask();
                if(records.length === 0) {
                    this.getEl().mask('You are not registered on any assignments within this period/semester. This may not be an issue if your subject/course do not have assignments, if no assignments have been published yet, or if the subject/course only use Devilry to register final results.', 'information-mask');
                }
            }
        });
    },
    
    initComponent: function() {
        var urlCreateFunction = Ext.bind(this.urlCreateFn, this.urlCreateFnScope);
        Ext.apply(this, {
            //cls: 'selectable-grid',
            //hideHeaders: true,
            disableSelection: true,
            columns: [{
                header: gettext('Assignment'),
                dataIndex: 'parentnode__long_name',
                flex: 4,
                renderer: function(value, m, record) {
                    return this.assignmentTpl.apply({
                        data: record.data,
                        url: urlCreateFunction(record)
                    });
                }
            //}, {
                //header: 'Points', dataIndex: 'feedback__points', flex: 1,
                //renderer: function(value, m, record) {
                    //return this.pointsTpl.apply(record.data);
                //}
            }, {
                header: gettext('Grade'),
                dataIndex: 'feedback__grade',
                flex: 2,
                renderer: function(value, m, record) {
                    return this.gradeTpl.apply(record.data);
                }
            }]
        });
        this.callParent(arguments);
    }
});
