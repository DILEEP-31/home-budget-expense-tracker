/**
 * Interactive Chart.js integration for Home Budget Tracker.
 * Manages Category Doughnut, Monthly Grouped Bar, Savings Trend Line, and Budget Horizontal Bar charts.
 * Features:
 * - Loading spinners during asynchronous API fetch
 * - Graceful empty-state banners when zero transactions exist
 * - Responsive error handling with retry capability
 * - Standardized Indian Rupee (₹) tooltip currency formatters
 */

const BudgetCharts = (function() {
    'use strict';

    // Store active chart instances by canvas ID to avoid canvas reuse errors
    const instances = {};

    function formatCurrency(val) {
        return '₹' + Number(val || 0).toLocaleString('en-IN', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }

    function getContainerElements(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return null;
        return {
            container: container,
            loading: container.querySelector('.chart-loading'),
            empty: container.querySelector('.chart-empty'),
            error: container.querySelector('.chart-error'),
            canvas: container.querySelector('canvas')
        };
    }

    function setViewState(els, state, msg) {
        if (!els) return;
        if (els.loading) els.loading.classList.toggle('d-none', state !== 'loading');
        if (els.empty) {
            els.empty.classList.toggle('d-none', state !== 'empty');
            if (msg && els.empty.querySelector('.chart-empty-msg')) {
                els.empty.querySelector('.chart-empty-msg').textContent = msg;
            }
        }
        if (els.error) {
            els.error.classList.toggle('d-none', state !== 'error');
            if (msg && els.error.querySelector('.chart-error-msg')) {
                els.error.querySelector('.chart-error-msg').textContent = msg;
            }
        }
        if (els.canvas) els.canvas.style.display = (state === 'canvas') ? 'block' : 'none';
    }

    function destroyChart(canvasId) {
        if (instances[canvasId]) {
            instances[canvasId].destroy();
            delete instances[canvasId];
        }
    }

    /**
     * 1. Category Expense Doughnut Chart
     */
    async function loadCategoryDoughnut(containerId, canvasId, apiUrl) {
        const els = getContainerElements(containerId);
        setViewState(els, 'loading');
        destroyChart(canvasId);

        try {
            const resp = await fetch(apiUrl, { credentials: 'same-origin' });
            if (!resp.ok) {
                if (resp.status === 401) throw new Error("Please log in to view chart.");
                throw new Error("Unable to retrieve category data.");
            }
            const json = await resp.json();

            if (!json.has_data || !json.data || json.data.length === 0) {
                setViewState(els, 'empty', "No expense records found for this period.");
                return;
            }

            setViewState(els, 'canvas');
            const ctx = document.getElementById(canvasId).getContext('2d');

            instances[canvasId] = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: json.labels,
                    datasets: [{
                        data: json.data,
                        backgroundColor: json.colors,
                        borderColor: '#ffffff',
                        borderWidth: 2,
                        hoverOffset: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '68%',
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                boxWidth: 12,
                                padding: 14,
                                font: { family: 'Poppins', size: 11 }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const val = context.raw || 0;
                                    const pct = json.percentages[context.dataIndex] || 0;
                                    return ` ${label}: ${formatCurrency(val)} (${pct}%)`;
                                }
                            }
                        }
                    }
                }
            });
        } catch (err) {
            setViewState(els, 'error', err.message);
        }
    }

    /**
     * 2. Monthly Income vs. Expense Grouped Bar Chart
     */
    async function loadMonthlySummaryBar(containerId, canvasId, apiUrl) {
        const els = getContainerElements(containerId);
        setViewState(els, 'loading');
        destroyChart(canvasId);

        try {
            const resp = await fetch(apiUrl, { credentials: 'same-origin' });
            if (!resp.ok) {
                if (resp.status === 401) throw new Error("Please log in to view chart.");
                throw new Error("Unable to retrieve monthly summary.");
            }
            const json = await resp.json();

            if (!json.has_data) {
                setViewState(els, 'empty', "No income or expense records found for this year.");
                return;
            }

            setViewState(els, 'canvas');
            const ctx = document.getElementById(canvasId).getContext('2d');

            instances[canvasId] = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: json.months,
                    datasets: [
                        {
                            label: 'Income',
                            data: json.incomes,
                            backgroundColor: '#10b981',
                            borderRadius: 4,
                            barPercentage: 0.6,
                            categoryPercentage: 0.8
                        },
                        {
                            label: 'Expense',
                            data: json.expenses,
                            backgroundColor: '#ef4444',
                            borderRadius: 4,
                            barPercentage: 0.6,
                            categoryPercentage: 0.8
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            grid: { display: false },
                            ticks: { font: { family: 'Poppins', size: 11 } }
                        },
                        y: {
                            grid: { color: 'rgba(0, 0, 0, 0.05)' },
                            ticks: {
                                font: { family: 'Poppins', size: 11 },
                                callback: function(val) {
                                    if (val >= 1000) return '₹' + (val / 1000) + 'k';
                                    return '₹' + val;
                                }
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                boxWidth: 12,
                                font: { family: 'Poppins', size: 11 }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(ctx) {
                                    return ` ${ctx.dataset.label}: ${formatCurrency(ctx.raw)}`;
                                }
                            }
                        }
                    }
                }
            });
        } catch (err) {
            setViewState(els, 'error', err.message);
        }
    }

    /**
     * 3. Monthly and Cumulative Savings Trend Line Chart
     */
    async function loadSavingsTrendLine(containerId, canvasId, apiUrl) {
        const els = getContainerElements(containerId);
        setViewState(els, 'loading');
        destroyChart(canvasId);

        try {
            const resp = await fetch(apiUrl, { credentials: 'same-origin' });
            if (!resp.ok) {
                if (resp.status === 401) throw new Error("Please log in to view chart.");
                throw new Error("Unable to retrieve savings trend.");
            }
            const json = await resp.json();

            if (!json.has_data) {
                setViewState(els, 'empty', "No savings history available for this year.");
                return;
            }

            setViewState(els, 'canvas');
            const ctx = document.getElementById(canvasId).getContext('2d');

            instances[canvasId] = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: json.labels,
                    datasets: [
                        {
                            label: 'Monthly Net Savings',
                            data: json.monthly_savings,
                            borderColor: '#4f46e5',
                            backgroundColor: 'rgba(79, 70, 229, 0.08)',
                            borderWidth: 2.5,
                            tension: 0.35,
                            fill: true,
                            pointRadius: 4,
                            pointBackgroundColor: '#4f46e5'
                        },
                        {
                            label: 'Cumulative Savings',
                            data: json.cumulative_savings,
                            borderColor: '#06b6d4',
                            borderWidth: 2,
                            borderDash: [5, 5],
                            tension: 0.35,
                            fill: false,
                            pointRadius: 3,
                            pointBackgroundColor: '#06b6d4'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            grid: { display: false },
                            ticks: { font: { family: 'Poppins', size: 11 } }
                        },
                        y: {
                            grid: { color: 'rgba(0, 0, 0, 0.05)' },
                            ticks: {
                                font: { family: 'Poppins', size: 11 },
                                callback: function(val) {
                                    if (val >= 1000 || val <= -1000) return '₹' + (val / 1000) + 'k';
                                    return '₹' + val;
                                }
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                boxWidth: 12,
                                font: { family: 'Poppins', size: 11 }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(ctx) {
                                    return ` ${ctx.dataset.label}: ${formatCurrency(ctx.raw)}`;
                                }
                            }
                        }
                    }
                }
            });
        } catch (err) {
            setViewState(els, 'error', err.message);
        }
    }

    /**
     * 4. Horizontal Bar Chart for Budget Utilization
     */
    async function loadBudgetUtilizationBar(containerId, canvasId, apiUrl) {
        const els = getContainerElements(containerId);
        setViewState(els, 'loading');
        destroyChart(canvasId);

        try {
            const resp = await fetch(apiUrl, { credentials: 'same-origin' });
            if (!resp.ok) {
                if (resp.status === 401) throw new Error("Please log in to view chart.");
                throw new Error("Unable to retrieve budget data.");
            }
            const json = await resp.json();

            if (!json.has_data || !json.labels || json.labels.length === 0) {
                setViewState(els, 'empty', "No budget limits or spending configured for this month.");
                return;
            }

            setViewState(els, 'canvas');
            const ctx = document.getElementById(canvasId).getContext('2d');

            instances[canvasId] = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: json.labels,
                    datasets: [
                        {
                            label: 'Budget Limit',
                            data: json.budgets,
                            backgroundColor: '#cbd5e1',
                            borderRadius: 4,
                            barPercentage: 0.7,
                            categoryPercentage: 0.8
                        },
                        {
                            label: 'Actual Spent',
                            data: json.spents,
                            backgroundColor: function(context) {
                                const idx = context.dataIndex;
                                const status = json.statuses[idx];
                                if (status === 'exceeded') return '#ef4444';
                                if (status === 'warning') return '#f59e0b';
                                return '#10b981';
                            },
                            borderRadius: 4,
                            barPercentage: 0.7,
                            categoryPercentage: 0.8
                        }
                    ]
                },
                options: {
                    indexAxis: 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            grid: { color: 'rgba(0, 0, 0, 0.05)' },
                            ticks: {
                                font: { family: 'Poppins', size: 11 },
                                callback: function(val) {
                                    if (val >= 1000) return '₹' + (val / 1000) + 'k';
                                    return '₹' + val;
                                }
                            }
                        },
                        y: {
                            grid: { display: false },
                            ticks: { font: { family: 'Poppins', size: 11 } }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                boxWidth: 12,
                                font: { family: 'Poppins', size: 11 }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(ctx) {
                                    const idx = ctx.dataIndex;
                                    const pct = json.percentages[idx] || 0;
                                    return ` ${ctx.dataset.label}: ${formatCurrency(ctx.raw)} (${pct}% used)`;
                                }
                            }
                        }
                    }
                }
            });
        } catch (err) {
            setViewState(els, 'error', err.message);
        }
    }

    return {
        loadCategoryDoughnut,
        loadMonthlySummaryBar,
        loadSavingsTrendLine,
        loadBudgetUtilizationBar,
        destroyChart
    };
})();
