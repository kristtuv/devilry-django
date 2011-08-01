Ext.define('devilry.gradeeditors.DraftEditorWindow', {
    extend: 'Ext.window.Window',
    alias: 'widget.gradedrafteditormainwin',
    title: 'Create feedback',
    width: 500,
    height: 400,
    layout: 'fit',
    modal: true,

    config: {
        /**
         * @cfg
         * ID of the Delivery where the feedback belongs. (Required).
         */
        deliveryid: undefined,

        /**
         * @cfg
         * Use the administrator RESTful interface to store drafts? If this is
         * ``false``, we use the examiner RESTful interface.
         */
        isAdministrator: false,

        /**
         * @cfg
         * The data attribute of the record returned when loading the
         * grade-editor config. (Required).
         */
        gradeeditor_config: undefined,

        /**
         * @cfg
         * The data attribute of the record returned when loading the
         * grade-editor registry item. (Required).
         */
        registryitem: undefined
    },

    constructor: function(config) {
        this.callParent([config]);
        this.initConfig(config);
    },

    initComponent: function() {
        Ext.apply(this, {
            dockedItems: [{
                xtype: 'toolbar',
                dock: 'bottom',
                ui: 'footer',
                items: ['->', {
                    xtype: 'button',
                    text: 'Save draft',
                    scale: 'large',
                    iconCls: 'icon-save-32',
                    listeners: {
                        scope: this,
                        click: this.onSaveDraft,
                    }
                }, {
                    xtype: 'button',
                    text: 'Publish',
                    scale: 'large',
                    iconCls: 'icon-add-32',
                    listeners: {
                        scope: this,
                        click: this.onPublish
                    }
                }]
            }],

            items: {
                xtype: 'panel',
                frame: false,
                border: false,
                layout: 'fit',
                loader: {
                    url: this.registryitem.draft_editor_url,
                    renderer: 'component',
                    autoLoad: true,
                    loadMask: true,
                    listeners: {
                        scope: this,
                        load: this.onLoadDraftEditor
                    }
                }
            }
        });
        this.callParent(arguments);
    },

    /**
     * Change the size of the grade editor window. Useful when the default size is
     * suboptimal for an editor.
     *
     * @param width New width.
     * @param height Ne height.
     * */
    changeSize: function(width, height) {
        this.setWidth(width);
        this.setHeight(height);
        this.center();
    },

    /**
     * @private
     */
    onLoadDraftEditor: function() {
        // TODO: Load latest draft.
    },

    /**
     * @private
     * Get the draft editor.
     */
    getDraftEditor: function() {
        return this.getComponent(0).getComponent(0);
    },

    /**
     * @private
     * Call the onPublish() method in the draft editor.
     */
    onPublish: function() {
        this.getDraftEditor().onPublish();
    },

    /**
     * @private
     * Call the onSaveDraft() method in the draft editor.
     */
    onSaveDraft: function() {
        this.getDraftEditor().onSaveDraft();
    },

    /**
     * @private
     * Exit the grade editor.
     */
    exit: function() {
        this.close();
    },

    /**
     * @private
     */
    save: function(published, draftstring, saveconfig) {
        var classname = Ext.String.format(
            'devilry.apps.gradeeditors.simplified.{0}.SimplifiedFeedbackDraft',
            this.isAdministrator? 'administrator': 'examiner'
        );
        var staticfeedback = Ext.create(classname, {
            draft: draftstring,
            published: published,
            delivery: this.deliveryid
        });
        staticfeedback.save(saveconfig, saveconfig);
    },

    /**
     * Save the current draftstring.
     *
     * @param draftstring The draftstring to save.
     * @param onFailure Called when the save fails. The scope is the draft
     *    editor that ``saveDraft`` was called from.
     */
    saveDraft: function(draftstring, onFailure) {
        this.save(false, draftstring, {
            scope: this.getDraftEditor(),
            failure: onFailure
        });
    },

    /**
     * Save and publish draftstring.
     *
     * @param draftstring The draftstring to save.
     * @param onFailure Called when the save fails. The scope is the draft
     *    editor that ``saveDraft`` was called from.
     */
    saveDraftAndPublish: function(draftstring, onFailure) {
        var me = this;
        this.save(true, draftstring, {
            scope: this.getDraftEditor(),
            success: function(response) {
                me.exit();
            },
            failure: onFailure
        });
    },

    /**
     * Get the grade editor configuration that is stored on the current
     * assignment.
     */
    getGradeEditorConfig: function() {
        return this.gradeeditor_config;
    }
});
