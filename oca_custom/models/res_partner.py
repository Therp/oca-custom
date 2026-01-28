# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)

PARAM_PREFIX = "oca_membership_channel_sync."
MEMBER_STATES = {"paid"}


class ResPartner(models.Model):
    _inherit = "res.partner"

    github_name = fields.Char(readonly=False)

    def _cfg_id(self, key: str) -> int | None:
        val = self.env["ir.config_parameter"].sudo().get_param(PARAM_PREFIX + key)
        if val and str(val).isdigit():
            return int(val)
        return None

    def _sync_member_tag_from_membership_state(self):
        member_tag_id = self._cfg_id("member_tag_id") or 3
        member_tag = self.env["res.partner.category"].browse(member_tag_id).exists()
        if not member_tag:
            _logger.info(
                "\nMember tag id=%s not found; skip membership_state tag sync\n",
                member_tag_id,
            )
            return

        to_add = self.filtered(
            lambda p: p.membership_state in MEMBER_STATES
            and member_tag not in p.category_id
        )
        to_remove = self.filtered(
            lambda p: p.membership_state not in MEMBER_STATES
            and member_tag in p.category_id
        )

        if to_add:
            to_add.with_context(skip_membership_channel_sync=True).write(
                {"category_id": [(4, member_tag.id)]}
            )
        if to_remove:
            to_remove.with_context(skip_membership_channel_sync=True).write(
                {"category_id": [(3, member_tag.id)]}
            )

    @api.model
    def _cron_membership_tag_sync(self, batch_size=500):
        ICP = self.env["ir.config_parameter"].sudo()
        last_id = int(
            ICP.get_param("oca_membership_channel_sync.cron_last_partner_id", "0") or 0
        )
        member_tag_id = int(
            ICP.get_param("oca_membership_channel_sync.member_tag_id", "3") or 3
        )

        partners = self.sudo().search(
            [
                ("id", ">", last_id),
                "|",
                ("membership_state", "=", "paid"),
                ("category_id", "in", [member_tag_id]),
            ],
            order="id asc",
            limit=batch_size,
        )

        if not partners:
            ICP.set_param("oca_membership_channel_sync.cron_last_partner_id", "0")
            return True

        partners._sync_member_tag_from_membership_state()
        ICP.set_param(
            "oca_membership_channel_sync.cron_last_partner_id", str(partners[-1].id)
        )

    def write(self, vals):
        res = super().write(vals)
        if self.env.context.get("skip_membership_channel_sync"):
            return res

        if "membership_state" in vals:
            self._sync_member_tag_from_membership_state()

        return res
