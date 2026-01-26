# Copyright (C) 2016-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestMembershipTagSync(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ICP = cls.env["ir.config_parameter"].sudo()
        cls.tag_member = cls.env["res.partner.category"].create({"name": "Member"})
        cls.partner = cls.env["res.partner"].create({"name": "Partner A"})
        cls.ICP.set_param(
            "oca_membership_channel_sync.member_tag_id", str(cls.tag_member.id)
        )

    def _set_membership_state_sql(self, partner, state):
        # membership_state is computed/stored and not always writable directly.
        self.env.cr.execute(
            "UPDATE res_partner SET membership_state=%s WHERE id=%s",
            (state, partner.id),
        )
        self.env.invalidate_all()
        return self.env["res.partner"].browse(partner.id)

    def test_01_action_sync_adds_member_tag_when_paid(self):
        partner = self._set_membership_state_sql(self.partner, "paid")
        self.assertNotIn(self.tag_member, partner.category_id)

        partner.action_membership_sync()
        self.assertIn(self.tag_member, partner.category_id)

    def test_02_action_sync_removes_member_tag_when_not_paid(self):
        partner = self._set_membership_state_sql(self.partner, "paid")
        partner.action_membership_sync()
        self.assertIn(self.tag_member, partner.category_id)

        partner = self._set_membership_state_sql(self.partner, "none")
        partner.action_membership_sync()
        self.assertNotIn(self.tag_member, partner.category_id)

    def test_03_cron_sync_reconciles_in_batches(self):
        # Reset cron cursor so this test is deterministic
        self.ICP.set_param("oca_membership_channel_sync.cron_last_partner_id", "0")

        partner = self._set_membership_state_sql(self.partner, "paid")
        self.assertNotIn(self.tag_member, partner.category_id)

        # Run cron manually
        self.env["res.partner"]._cron_membership_tag_sync(batch_size=100)

        partner = self.env["res.partner"].browse(self.partner.id)
        self.assertIn(self.tag_member, partner.category_id)
