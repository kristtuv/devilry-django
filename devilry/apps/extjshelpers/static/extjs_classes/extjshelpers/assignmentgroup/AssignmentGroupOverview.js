/**
 * Combines {@link devilry.extjshelpers.assignmentgroup.AssignmentGroupInfo} and
 * {@link devilry.extjshelpers.assignmentgroup.DeliveryInfo}
 * into a complete AssignmentGroup reader and manager
 * (if {@link #canExamine} is enabled).
 *
 *      -----------------------------------------------------------------
 *      |                     |                                         |
 *      |                     |                                         |
 *      |                     |                                         |
 *      | AssignmentGroupInfo | DeliveryInfo                            |
 *      |                     |                                         |
 *      |                     |                                         |
 *      |                     |                                         |
 *      |                     |                                         |
 *      -----------------------------------------------------------------
 */
Ext.define('devilry.extjshelpers.assignmentgroup.AssignmentGroupOverview', {
    extend: 'Ext.panel.Panel',
    width: 1000,
    height: 800,
    layout: 'border',
    alias: 'widget.assignmentgroupoverview',
    requires: [
        'devilry.extjshelpers.assignmentgroup.DeliveryInfo',
        'devilry.extjshelpers.assignmentgroup.AssignmentGroupInfo'
    ],

    headingTpl: Ext.create('Ext.XTemplate',
        '<div class="treeheader">',
        '   <div class="level1">{parentnode__parentnode__parentnode__long_name}</div>',
        '   <div class="level2">{parentnode__parentnode__long_name}</div>',
        '   <div class="level3">{parentnode__long_name}</div>',
        '<div>'
    ),

    config: {
        /**
         * @cfg
         * AssignmentGroup ``Ext.data.Store``. (Required).
         */
        assignmentgroupstore: undefined,

        /**
         * @cfg 
         * Delivery  ``Ext.data.Model``. (Required).
         */
        deliverymodel: undefined,

        /**
         * @cfg
         * Deadline ``Ext.data.Store``. (Required).
         * _Note_ that ``deadlinestore.proxy.extraParams`` is changed by
         * {@link devilry.extjshelpers.assignmentgroup.DeadlineListing}.
         */
        deadlinestore: undefined,

        /**
         * @cfg
         * FileMeta ``Ext.data.Store``. (Required).
         * _Note_ that ``filemetastore.proxy.extraParams`` is changed by
         * {@link devilry.extjshelpers.assignmentgroup.DeliveryInfo}.
         */
        filemetastore: undefined,

        /**
         * @cfg
         * FileMeta ``Ext.data.Store``. (Required).
         * _Note_ that ``filemetastore.proxy.extraParams`` is changed by
         * {@link devilry.extjshelpers.assignmentgroup.StaticFeedbackInfo}.
         */
        staticfeedbackstore: undefined,

        /**
         * @cfg
         * Enable creation of new feedbacks? Defaults to ``false``.
         * See: {@link devilry.extjshelpers.assignmentgroup.DeliveryInfo#canExamine}.
         *
         * When this is ``true``, the authenticated user still needs to have
         * permission to POST new feedbacks for the view to work.
         */
        canExamine: false
    },


    initComponent: function() {
        var me = this;
        this.mainHeader = Ext.create('Ext.Component');
        this.centerArea = Ext.create('Ext.container.Container');
        this.sidebar = Ext.create('Ext.container.Container');

        Ext.apply(this, {
            items: [{
                region: 'north',
                height: 66,
                xtype: 'container',
                layout: 'fit',
                items: [this.mainHeader]
            }, {
                region: 'west',
                layout: 'fit',
                width: 220,
                xtype: 'panel',
                collapsible: true,   // make collapsible
                //titleCollapse: true, // click anywhere on title to collapse.
                split: true,
                items: [{
                    xtype: 'panel',
                    layout: 'border',
                    items: [{
                        region: 'north',
                        items: [{
                            xtype: 'assignmentgroupdetailspanel',
                            title: 'Assignment group',
                            bodyPadding: 10,
                            singlerecordontainer: this.assignmentgroup_recordcontainer
                        }]
                    }, {
                        region: 'center',
                        items: [{
                            xtype: 'deadlinelisting',
                            title: 'Deadlines',
                            assignmentgroup_recordcontainer: this.assignmentgroup_recordcontainer,
                            delivery_recordcontainer: this.delivery_recordcontainer,
                            deliverymodel: this.deliverymodel,
                            deadlinestore: this.deadlinestore,
                            selectedDeliveryId: this.selectedDeliveryId,
                            canExamine: this.canExamine,
                            listeners: {
                                scope: this,
                                selectDelivery: this.setDelivery
                            }
                        }]
                    }]
                }]
            }, {
                region: 'center',
                layout: 'border',
                items: [{
                    region: 'north',
                    xtype: 'deliveryinfo',
                    delivery_recordcontainer: this.delivery_recordcontainer,
                    filemetastore: this.filemetastore
                }, {
                    region: 'center',
                }]
            }],
        });
        this.callParent(arguments);
    },

    /**
     * @private
     */
    onLoadAssignmentGroup: function(assignmentgrouprecord) {
        this.assignmentgroupid = assignmentgrouprecord.id;
        assignmentgroup = assignmentgrouprecord.data;
        //this.mainHeader.update(this.headingTpl.apply(assignmentgroup));
        //this.assignmentid = assignmentgroup.parentnode;

        //var query = Ext.Object.fromQueryString(window.location.search);
        //this.sidebar.add({
            //xtype: 'assignmentgroupinfo',
            //assignmentgroup: assignmentgroup,
            //deliverymodel: this.deliverymodel,
            //deadlinestore: this.deadlinestore,
            //canExamine: this.canExamine,
            //layout: 'fit',
            //selectedDeliveryId: parseInt(query.deliveryid)
        //});
    },

    setAssignmentGroupRecord: function(record) {
        this.down('assignmentgroupdetailspanel').setAssignmentGroupRecord(record);
    },

    /**
     * Create a {@link devilry.extjshelpers.assignmentgroup.DeliveryInfo}
     * containing the given delivery and place it in the center area.
     *
     * @param {Ext.model.Model} deliveryRecord A Delivery record.
     */
    setDelivery: function(deliveryRecord) {
        //if(deliveryRecord.data.deadline__assignment_group == this.assignmentgroupid) { // Note that this is not for security (that is handled on the server, however it is to prevent us from showing a delivery within the wrong assignment group (which is a bug))
            //this.centerArea.removeAll();
            //this.centerArea.add({
                //xtype: 'deliveryinfo',
                //assignmentid: this.assignmentid,
                //delivery: deliveryRecord.data,
                //filemetastore: this.filemetastore,
                //staticfeedbackstore: this.staticfeedbackstore,
                //canExamine: this.canExamine
            //});
            //console.log(deliveryRecord);
        //} else {
            //var errormsg = Ext.String.format(
                //'Invalid deliveryid: {0}. Must be a delivery made by AssignmentGroup: {1}',
                //deliveryRecord.id,
                //this.assignmentgroupid);
            //console.error(errormsg);
        //}
    }
});
