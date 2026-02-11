/* Copyright 2018 Surekha Technologies (https://www.surekhatech.com)
License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

odoo.define("website_oca_integrator.portal", function (require) {
    "use strict";

    const Tour = require("web_tour.tour");
    const base = require("web_editor.base");

    Tour.register(
        "integrator_portal",
        {
            url: "/my/account",
            test: true,
            wait_for: base.ready(),
        },
        [
            {
                trigger: "input[name='phone']",
                run: "text 123456789",
            },
            {
                trigger: ".module_js_select2 + .select2 .select2-search__field",
                run: "text Prod.",
            },
            {
                trigger: ".select2-results__option",
                run: "click",
            },
            {
                trigger: "input[name='github_organization']",
                run: "text test_github_organization",
            },
            {
                trigger: "textarea[name='website_short_description']",
                extra_trigger: ".select2-selection__choice",
                run: "text My company description",
            },
            {
                trigger: "button[type='submit']",
            },
            {
                trigger: ".btn-sm",
            },
        ]
    );
});
