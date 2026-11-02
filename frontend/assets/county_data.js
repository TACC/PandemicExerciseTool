// Project data only; sorting and selection belong to AG Grid.
window.dash_clientside = Object.assign({}, window.dash_clientside, {
    countyData: {
        selectDay: function (events, timeline, assets) {
            if (!events || timeline == null || !events[timeline]) return null;
            return {
                day: events[timeline].day,
                mapping: (assets || {}).mapping || {},
                counties: (events[timeline].counties || []).map(function (county) {
                    const totals = Object.assign({}, county);
                    delete totals.ageGroups;
                    return totals;
                })
            };
        },
        selectedAge: function (history, timeline, selected) {
            if (!selected || timeline == null) return null;
            const day = (history || [])[timeline];
            return {
                fips: selected, day: timeline,
                pending: !day || !Object.prototype.hasOwnProperty.call(day, selected),
                ages: day ? day[selected] : null
            };
        }
    }
});
