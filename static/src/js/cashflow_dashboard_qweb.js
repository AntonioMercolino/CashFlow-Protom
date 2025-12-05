/** @odoo-module **/

import { registry } from "@web/core/registry";

const actionRegistry = registry.category("actions");

function CashflowDashboardQweb(env, action) {

    const rpc = env.services.rpc;

    rpc("/cashflow/dashboard/kpi", {}).then(data => {
        document.querySelector("#cf_balance").textContent = data.kpi.balance;
        document.querySelector("#cf_income").textContent = data.kpi.income;
        document.querySelector("#cf_outcome").textContent = data.kpi.outcome;
    });

    return {
        destroy() {},
    };
}

actionRegistry.add("cashflow_dashboard_qweb", CashflowDashboardQweb);
