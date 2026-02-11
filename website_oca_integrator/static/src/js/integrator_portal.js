/* Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

odoo.define("website_oca_integrator.website_oca_integrator", function (require) {
    "use strict";

    const publicWidget = require("web.public.widget");

    publicWidget.registry.integratorModuleSelector = publicWidget.Widget.extend({
        selector: ".module_js_select2",

        /**
         * @override
         */
        start: function () {
            this.$el.select2({
                tags: false,
                maximumInputLength: 25,
                maximumSelectionLength: 5,
                ajax: {
                    url: "/my/account/get_developed_modules",
                    dataType: "json",
                    data: (params) => ({query: params.term, limit: 25}),
                    processResults: (data) => ({
                        results: _.map(data, (x) => ({id: x.id, text: x.name})),
                    }),
                },
            });
            $.ajax({
                type: "GET",
                url: "/my/account/get_favourite_modules",
                dataType: "json",
                success: (data) => {
                    const options = _.map(
                        data,
                        (x) => new Option(x.name, x.id, true, true)
                    );
                    this.$el.append(options).trigger("change");
                },
            });
        },
    });

    publicWidget.registry.integratorDescriptionEditor = publicWidget.Widget.extend({
        selector: "textarea.website_description_editor",
        events: {"click button, .a-submit": "_submit"},
        assetLibs: ["web_editor.compiled_assets_wysiwyg"],

        /**
         * @override
         */
        start: function () {
            if (!this.$el.val().match(/\S/)) {
                this.$el.val("<p><br/></p>");
            }
            const toolbar = [
                ["style", ["style"]],
                ["font", ["bold", "italic", "underline", "clear"]],
                ["para", ["ul", "ol", "paragraph"]],
                ["table", ["table"]],
                ["history", ["undo", "redo"]],
            ];
            this.$el.summernote({
                height: 200,
                toolbar: toolbar,
                styleWithSpan: false,
            });
        },
        _submit: function () {
            const $form = this.$el.closest("form");
            this.$el.html($form.find(".note-editable").code());
        },
    });
});
