// Keep county history in the browser; Python receives only unplotted totals.
window.dash_clientside = Object.assign({}, window.dash_clientside, {
    epidemicCurve: {
        selectFrame: function (events, timeline, model, progress) {
            events = events || [];
            const start = progress && progress.model === model && progress.count <= events.length
                ? progress.count : 0;
            const fields = ['day', 'totalSusceptible', 'totalExposed',
                'totalAsymptomaticCount', 'totalTreatableCount', 'totalInfectedCount',
                'totalRecoveredCount', 'totalDeceased'];
            const points = events.slice(start).map(function (event) {
                const point = {};
                fields.forEach(function (field) { point[field] = event[field] || 0; });
                return point;
            });
            const selected = timeline == null ? null : events[timeline];
            return {start: start, count: events.length, model: model,
                day: selected ? selected.day : null, points: points};
        }
    }
});
